from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import EspacioAhorro, AporteAhorro
from .serializers import EspacioAhorroSerializer, AporteAhorroSerializer
from apps.parches.models import Parche, Membership


class EspacioAhorroListCreateView(generics.ListCreateAPIView):
    """RF_20 – Listar y crear espacios de ahorro dentro de un parche."""
    serializer_class   = EspacioAhorroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        parche_id = self.kwargs['parche_id']
        return EspacioAhorro.objects.filter(parche_id=parche_id)

    def perform_create(self, serializer):
        parche_id = self.kwargs['parche_id']
        parche    = Parche.objects.get(id=parche_id)
        serializer.save(parche=parche, creator=self.request.user)


class EspacioAhorroDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF_20 – Ver, editar o eliminar un espacio de ahorro."""
    serializer_class   = EspacioAhorroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EspacioAhorro.objects.filter(
            parche__memberships__user=self.request.user
        )


class AporteAhorroCreateView(APIView):
    """RF_20 – Realizar un aporte a un espacio de ahorro."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, espacio_id):
        try:
            espacio = EspacioAhorro.objects.select_related('parche').get(pk=espacio_id)
        except EspacioAhorro.DoesNotExist:
            return Response({'error': 'Espacio de ahorro no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Verificar membresía en el parche
        if not Membership.objects.filter(parche=espacio.parche, user=request.user).exists():
            return Response({'error': 'No perteneces al parche de este espacio.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AporteAhorroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']

        with transaction.atomic():
            aporte = serializer.save(espacio=espacio, user=request.user)
            # Actualizar el monto acumulado del espacio
            espacio.current_amount = espacio.current_amount + amount
            espacio.save(update_fields=['current_amount'])

            from apps.finanzas.models import Transaccion
            if request.user != espacio.creator:
                Transaccion.objects.create(
                    parche=espacio.parche,
                    from_user=request.user,
                    to_user=espacio.creator,
                    amount=amount,
                    type='pago',
                    concept=f"Ahorro: {espacio.name}"
                )

        return Response(
            AporteAhorroSerializer(aporte).data,
            status=status.HTTP_201_CREATED
        )
