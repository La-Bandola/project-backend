from django.core.exceptions import ValidationError
from django.db.models import DecimalField, F, Q, Sum
from django.db.models.functions import Coalesce
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.eventos.models import EventoParticipant
from apps.parches.models import Membership, Parche

from .models import Balance, Transaccion
from .serializers import BalanceSerializer, TransaccionSerializer
from .services import create_transaction, pay_event_participant


class TransaccionListCreateView(generics.ListCreateAPIView):
    """RF_27 – Historial de transacciones del parche con filtros opcionales."""
    serializer_class   = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        parche_id = self.kwargs['parche_id']
        qs = Transaccion.objects.filter(parche_id=parche_id).order_by('-created_at')

        # Filtros opcionales: ?year=2025&month=6&type=pago
        year  = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        tipo  = self.request.query_params.get('type')

        if year:
            qs = qs.filter(created_at__year=year)
        if month:
            qs = qs.filter(created_at__month=month)
        if tipo:
            qs = qs.filter(type=tipo)

        return qs

    def perform_create(self, serializer):
        parche_id = self.kwargs['parche_id']
        parche = Parche.objects.get(id=parche_id)
        serializer.save(
            from_user=self.request.user,
            parche=parche,
        )


class TransaccionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF_28 – Editar o eliminar una transacción dentro del contexto de un parche."""
    serializer_class   = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaccion.objects.filter(
            parche__memberships__user=self.request.user
        )


class TransaccionGlobalListView(generics.ListAPIView):
    """Historial global de todas las transacciones del usuario en todos los parches."""
    serializer_class   = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaccion.objects.filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user)
        ).select_related('from_user', 'to_user', 'parche').order_by('-created_at')


class TransaccionUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Editar o eliminar cualquier transacción global manual."""
    serializer_class   = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaccion.objects.filter(
            Q(from_user=self.request.user) | Q(to_user=self.request.user)
        )


class BalanceParcheView(APIView):
    """RF_23 – Resumen general de balance por parche."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, parche_id):
        parche = Parche.objects.get(id=parche_id)
        balances = Balance.objects.filter(parche=parche)
        serializer = BalanceSerializer(balances, many=True)
        return Response(serializer.data)


class BalancePersonalView(APIView):
    """RF_21 – Balance de deudas, pagos e ingresos del usuario en un parche."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, parche_id):
        user = request.user

        year  = request.query_params.get('year')
        month = request.query_params.get('month')

        def tx_filter(qs):
            if year: qs = qs.filter(created_at__year=year)
            if month: qs = qs.filter(created_at__month=month)
            return qs

        enviado  = tx_filter(Transaccion.objects.filter(parche_id=parche_id, from_user=user, type='pago')).aggregate(t=Sum('amount'))['t'] or 0
        recibido = tx_filter(Transaccion.objects.filter(parche_id=parche_id, to_user=user, type='pago')).aggregate(t=Sum('amount'))['t'] or 0
        deudas_tx = tx_filter(Transaccion.objects.filter(parche_id=parche_id, from_user=user, type='deuda')).aggregate(t=Sum('amount'))['t'] or 0

        # IDs de responsables de eventos donde el usuario tiene deudas (para evitar doble conteo)
        responsible_ids = set(EventoParticipant.objects.filter(
            evento__parche_id=parche_id, user=user
        ).exclude(
            user=F('evento__responsible')
        ).values_list('evento__responsible_id', flat=True))

        qs_evt_deuda = EventoParticipant.objects.filter(
            ~Q(user=F('evento__responsible')),
            evento__parche_id=parche_id, user=user
        )
        if year:  qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__year=year)
        if month: qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__month=month)

        qs_evt_deuda = qs_evt_deuda.annotate(
            amount_paid_calc=Coalesce(
                Sum(
                    'user__transacciones_enviadas__amount',
                    filter=Q(
                        # Todos los pagos al responsable del evento en el parche,
                        # incluyendo pagos manuales sin evento vinculado (evento=None)
                        user__transacciones_enviadas__to_user=F('evento__responsible'),
                        user__transacciones_enviadas__parche_id=parche_id,
                        user__transacciones_enviadas__type='pago',
                    )
                ), 0.0, output_field=DecimalField()
            )
        ).filter(amount_owed__gt=F('amount_paid_calc'))

        deudas_evt = sum(float(p.amount_owed) - float(p.amount_paid_calc) for p in qs_evt_deuda)
        deudas = float(deudas_tx) + deudas_evt

        # Pagos que NO van a responsables de eventos → los únicos que se restan del neto
        # para evitar doble conteo (los pagos a responsables ya reducen deudas_evt)
        enviado_standalone = float(tx_filter(Transaccion.objects.filter(
            parche_id=parche_id, from_user=user, type='pago'
        ).exclude(
            to_user_id__in=responsible_ids
        )).aggregate(t=Sum('amount'))['t'] or 0)

        return Response({
            'pagado':   float(enviado),
            'recibido': float(recibido),
            'deudas':   deudas,
            'neto':     float(recibido) - enviado_standalone - deudas,
        })



class BalanceMensualView(APIView):
    """RF_21 – Balance mensual consolidado del usuario en todos sus parches."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user  = request.user
        year  = request.query_params.get('year')
        month = request.query_params.get('month')

        def tx_filter(qs):
            if year: qs = qs.filter(created_at__year=year)
            if month: qs = qs.filter(created_at__month=month)
            return qs

        enviado  = tx_filter(Transaccion.objects.filter(from_user=user, type='pago')).aggregate(t=Sum('amount'))['t'] or 0
        recibido = tx_filter(Transaccion.objects.filter(to_user=user, type='pago')).aggregate(t=Sum('amount'))['t'] or 0
        
        deudas_tx   = tx_filter(Transaccion.objects.filter(from_user=user, type='deuda')).aggregate(t=Sum('amount'))['t'] or 0

        qs_evt_deuda = EventoParticipant.objects.filter(
            ~Q(user=F('evento__responsible')),
            user=user
        )
        if year: qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__year=year)
        if month: qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__month=month)
        
        qs_evt_deuda = qs_evt_deuda.annotate(
            amount_paid_calc=Coalesce(
                Sum(
                    'user__transacciones_enviadas__amount',
                    filter=Q(
                        user__transacciones_enviadas__evento=F('evento'),
                        user__transacciones_enviadas__type='pago'
                    )
                ), 0.0, output_field=DecimalField()
            )
        ).filter(amount_owed__gt=F('amount_paid_calc'))
        
        deudas_evt = sum(float(p.amount_owed) - float(p.amount_paid_calc) for p in qs_evt_deuda)

        deudas   = float(deudas_tx) + deudas_evt
        enviado  = float(enviado)
        recibido = float(recibido)

        return Response({
            'year':     year,
            'month':    month,
            'pagado':   enviado,
            'recibido': recibido,
            'deudas':   deudas,
            'neto':     recibido - enviado - deudas,
        })


class ResumenMutuoView(APIView):
    """RF_24 – Balance mutuo entre el usuario y cada integrante de un parche."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, parche_id):
        user = request.user

        # IDs de responsables de eventos donde el usuario tiene deudas
        # Estos pagos se procesan en el paso 2 (vía amount_paid_calc) para evitar doble conteo
        responsible_ids = set(EventoParticipant.objects.filter(
            evento__parche_id=parche_id, user=user
        ).exclude(
            user=F('evento__responsible')
        ).values_list('evento__responsible_id', flat=True))

        transacciones = Transaccion.objects.filter(
            parche_id=parche_id
        ).filter(
            Q(from_user=user) | Q(to_user=user)
        ).select_related('from_user', 'to_user')

        resumen = {}

        # Paso 1: Solo transacciones standalone (sin evento vinculado)
        # Las transacciones de pago a responsables de eventos se omiten aquí
        # porque ya quedan capturadas en la reducción de deuda_restante del paso 2
        for tx in transacciones.filter(evento__isnull=True):
            if tx.from_user == user:
                if tx.to_user_id not in responsible_ids:
                    # Pago a alguien que NO es responsable de ningún evento mío
                    otro = tx.to_user
                    resumen.setdefault(otro.username, 0)
                    resumen[otro.username] -= float(tx.amount)
            else:
                # Dinero recibido: siempre lo incluimos
                otro = tx.from_user
                resumen.setdefault(otro.username, 0)
                resumen[otro.username] += float(tx.amount)

        # Paso 2: Deudas de eventos usando TODOS los pagos al responsable
        # (incluyendo pagos manuales sin evento vinculado)
        participaciones = EventoParticipant.objects.filter(
            evento__parche_id=parche_id
        ).filter(
            Q(user=user) | Q(evento__responsible=user)
        ).select_related('user', 'evento__responsible').annotate(
            amount_paid_calc=Coalesce(
                Sum(
                    'user__transacciones_enviadas__amount',
                    filter=Q(
                        user__transacciones_enviadas__to_user=F('evento__responsible'),
                        user__transacciones_enviadas__parche_id=parche_id,
                        user__transacciones_enviadas__type='pago'
                    )
                ), 0.0, output_field=DecimalField()
            )
        ).filter(amount_owed__gt=F('amount_paid_calc'))

        for p in participaciones:
            deuda_restante = float(p.amount_owed) - float(p.amount_paid_calc)
            # Si el usuario es quien debe
            if p.user == user and p.evento.responsible and p.evento.responsible != user:
                otro = p.evento.responsible
                resumen.setdefault(otro.username, 0)
                resumen[otro.username] -= deuda_restante

            # Si al usuario le deben (es el responsable del evento)
            if p.evento.responsible == user and p.user != user:
                otro = p.user
                resumen.setdefault(otro.username, 0)
                resumen[otro.username] += deuda_restante

        return Response(resumen)



class BoletinInicioView(APIView):
    """RF_25 – Boletín de balance para la página de inicio: resumen global del usuario."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        total_pagado = float(Transaccion.objects.filter(from_user=user, type='pago').aggregate(t=Sum('amount'))['t'] or 0)
        total_recibido = float(Transaccion.objects.filter(to_user=user, type='pago').aggregate(t=Sum('amount'))['t'] or 0)

        saldo_neto = total_recibido - total_pagado
        num_parches = Membership.objects.filter(user=user).count()

        return Response({
            'total_pagado':   total_pagado,
            'total_recibido': total_recibido,
            'saldo_neto':     saldo_neto,
            'num_parches':    num_parches,
        })