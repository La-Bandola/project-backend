from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.finanzas.services import pay_event_participant
from apps.parches.models import Parche

from .models import Evento, EventoParticipant, Suscripcion
from .serializers import EventoParticipantSerializer, EventoSerializer, SuscripcionSerializer


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


class PagarEventoView(APIView):
    """Realizar un pago (parcial o total) para un evento."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            participant = EventoParticipant.objects.get(pk=pk, user=request.user)
        except EventoParticipant.DoesNotExist:
            return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

        amount = request.data.get('amount')
        concept = request.data.get('concept', f"Evento: {participant.evento.name}")
        destination_account = request.data.get('destination_account', '')

        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pay_event_participant(
                participant=participant,
                amount=amount,
                concept=concept,
                destination_account=destination_account,
            )
        except ValidationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'ok'})


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
        from django.db.models import Sum, F, Q, DecimalField
        from django.db.models.functions import Coalesce

        pendientes = EventoParticipant.objects.annotate(
            paid_calc=Coalesce(
                Sum(
                    'user__transacciones_enviadas__amount',
                    filter=Q(
                        user__transacciones_enviadas__evento=F('evento'),
                        user__transacciones_enviadas__type='pago'
                    )
                ), 0.0, output_field=DecimalField()
            )
        ).filter(
            ~Q(user=F('evento__responsible')),
            user=request.user,
            amount_owed__gt=F('paid_calc')
        ).select_related('evento', 'evento__parche', 'evento__responsible')

        data = [
            {
                'participant_id':   p.id,
                'evento_id':        p.evento.id,
                'evento_nombre':    p.evento.name,
                'parche_id':        p.evento.parche.id,
                'parche_nombre':    p.evento.parche.name,
                'monto_adeudado':   str(p.amount_owed),
                'monto_pagado':     str(p.paid_calc),
                'monto_restante':   str(p.amount_owed - p.paid_calc),
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