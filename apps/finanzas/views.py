from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Q
from .models import Transaccion, Balance
from .serializers import TransaccionSerializer, BalanceSerializer
from apps.parches.models import Parche

class TransaccionListCreateView(generics.ListCreateAPIView):
    serializer_class   = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        parche_id = self.kwargs['parche_id']
        return Transaccion.objects.filter(
            parche_id=parche_id
        ).order_by('-created_at')

    def perform_create(self, serializer):
        parche_id = self.kwargs['parche_id']
        parche    = Parche.objects.get(id=parche_id)
        serializer.save(from_user=self.request.user, parche=parche)


class TransaccionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaccion.objects.filter(
            parche__memberships__user=self.request.user
        )


class BalanceParcheView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, parche_id):
        parche = Parche.objects.get(id=parche_id)
        balances = Balance.objects.filter(parche=parche)
        serializer = BalanceSerializer(balances, many=True)
        return Response(serializer.data)


class BalancePersonalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, parche_id):
        user = request.user

        enviado = Transaccion.objects.filter(
            parche_id=parche_id,
            from_user=user,
            type='pago'
        ).aggregate(total=Sum('amount'))['total'] or 0

        recibido = Transaccion.objects.filter(
            parche_id=parche_id,
            to_user=user,
            type='pago'
        ).aggregate(total=Sum('amount'))['total'] or 0

        deudas = Transaccion.objects.filter(
            parche_id=parche_id,
            from_user=user,
            type='deuda'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'pagado':   enviado,
            'recibido': recibido,
            'deudas':   deudas,
            'neto':     recibido - enviado - deudas
        })


class ResumenMutuoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, parche_id):
        user = request.user

        transacciones = Transaccion.objects.filter(
            parche_id=parche_id
        ).filter(
            Q(from_user=user) | Q(to_user=user)
        ).select_related('from_user', 'to_user')

        resumen = {}
        for tx in transacciones:
            if tx.from_user == user:
                otro = tx.to_user
                resumen.setdefault(otro.username, 0)
                resumen[otro.username] -= float(tx.amount)
            else:
                otro = tx.from_user
                resumen.setdefault(otro.username, 0)
                resumen[otro.username] += float(tx.amount)

        return Response(resumen)