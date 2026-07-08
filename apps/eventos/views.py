from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import Evento, EventoParticipant, Suscripcion
from .serializers import EventoSerializer, EventoParticipantSerializer, SuscripcionSerializer
from apps.parches.models import Parche


class EventoListCreateView(generics.ListCreateAPIView):
    """RF_12 – Listar y crear eventos dentro de un parche."""
    serializer_class   = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        parche_id = self.kwargs['parche_id']
        return Evento.objects.filter(parche_id=parche_id)

    def perform_create(self, serializer):
        parche_id = self.kwargs['parche_id']
        parche    = Parche.objects.get(id=parche_id)
        serializer.save(parche=parche)


class EventoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF_12 – Ver, editar o eliminar un evento."""
    serializer_class   = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Evento.objects.filter(
            parche__memberships__user=self.request.user
        )


class MarcarPagadoView(generics.UpdateAPIView):
    """RF_15 – Marcar la participación de un usuario como pagada."""
    serializer_class   = EventoParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventoParticipant.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(paid=True, paid_at=timezone.now())


class UploadPaymentProofView(APIView):
    """RF_32 – Subir comprobante/soporte de pago para una participación."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        try:
            participant = EventoParticipant.objects.get(pk=pk, user=request.user)
        except EventoParticipant.DoesNotExist:
            return Response(
                {'error': 'Participación no encontrada o no te pertenece.'},
                status=status.HTTP_404_NOT_FOUND
            )

        proof = request.FILES.get('payment_proof')
        if not proof:
            return Response(
                {'error': 'Se requiere el archivo de soporte (payment_proof).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        participant.payment_proof = proof
        participant.save()

        serializer = EventoParticipantSerializer(participant)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PendingDebtsView(APIView):
    """RF_22 – Listar deudas pendientes del usuario en todos sus eventos."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pendientes = EventoParticipant.objects.filter(
            user=request.user,
            paid=False
        ).select_related('evento', 'evento__parche', 'evento__responsible')

        data = [
            {
                'participant_id':   p.id,
                'evento_id':        p.evento.id,
                'evento_nombre':    p.evento.name,
                'parche_id':        p.evento.parche.id,
                'parche_nombre':    p.evento.parche.name,
                'monto_adeudado':   str(p.amount_owed),
                'responsable':      p.evento.responsible.username if p.evento.responsible else None,
                'pay_immediately':  p.evento.pay_immediately,
                'estado_evento':    p.evento.status,
                'creado_en':        p.evento.created_at,
            }
            for p in pendientes
        ]
        return Response(data, status=status.HTTP_200_OK)


class SuscripcionListCreateView(generics.ListCreateAPIView):
    """RF_18 – Listar y crear suscripciones en un parche."""
    serializer_class   = SuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        parche_id = self.kwargs['parche_id']
        return Suscripcion.objects.filter(parche_id=parche_id)

    def perform_create(self, serializer):
        parche_id = self.kwargs['parche_id']
        parche    = Parche.objects.get(id=parche_id)
        serializer.save(parche=parche)


class SuscripcionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF_18 / RF_19 – Ver, editar o eliminar una suscripción."""
    serializer_class   = SuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Suscripcion.objects.filter(
            parche__memberships__user=self.request.user
        )