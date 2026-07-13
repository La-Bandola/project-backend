from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Q
from .models import Transaccion, Balance
from .serializers import TransaccionSerializer, BalanceSerializer
from apps.parches.models import Parche, Membership
from apps.eventos.models import EventoParticipant


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
        parche    = Parche.objects.get(id=parche_id)
        serializer.save(from_user=self.request.user, parche=parche)


class TransaccionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF_28 – Editar o eliminar una transacción."""
    serializer_class   = TransaccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaccion.objects.filter(
            parche__memberships__user=self.request.user
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

        # Filtros opcionales por mes: ?year=2025&month=6
        year  = request.query_params.get('year')
        month = request.query_params.get('month')

        def apply_date_filters(qs):
            if year:
                qs = qs.filter(created_at__year=year)
            if month:
                qs = qs.filter(created_at__month=month)
            return qs

        enviado = apply_date_filters(
            Transaccion.objects.filter(parche_id=parche_id, from_user=user, type='pago')
        ).aggregate(total=Sum('amount'))['total'] or 0

        recibido = apply_date_filters(
            Transaccion.objects.filter(parche_id=parche_id, to_user=user, type='pago')
        ).aggregate(total=Sum('amount'))['total'] or 0

        deudas_tx = apply_date_filters(
            Transaccion.objects.filter(parche_id=parche_id, from_user=user, type='deuda')
        ).aggregate(total=Sum('amount'))['total'] or 0

        qs_evt = EventoParticipant.objects.filter(evento__parche_id=parche_id, user=user, paid=False)
        if year:
            qs_evt = qs_evt.filter(evento__created_at__year=year)
        if month:
            qs_evt = qs_evt.filter(evento__created_at__month=month)
        deudas_evt = qs_evt.aggregate(total=Sum('amount_owed'))['total'] or 0

        deudas = deudas_tx + deudas_evt

        return Response({
            'pagado':   enviado,
            'recibido': recibido,
            'deudas':   deudas,
            'neto':     recibido - enviado - deudas,
        })


class BalanceMensualView(APIView):
    """RF_21 – Balance mensual consolidado del usuario en todos sus parches."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user  = request.user
        year  = request.query_params.get('year')
        month = request.query_params.get('month')

        qs = Transaccion.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        )

        if year:
            qs = qs.filter(created_at__year=year)
        if month:
            qs = qs.filter(created_at__month=month)

        enviado  = qs.filter(from_user=user, type='pago').aggregate(t=Sum('amount'))['t'] or 0
        recibido = qs.filter(to_user=user,   type='pago').aggregate(t=Sum('amount'))['t'] or 0
        deudas_tx = qs.filter(from_user=user, type='deuda').aggregate(t=Sum('amount'))['t'] or 0
        
        qs_evt = EventoParticipant.objects.filter(user=user, paid=False)
        if year:
            qs_evt = qs_evt.filter(evento__created_at__year=year)
        if month:
            qs_evt = qs_evt.filter(evento__created_at__month=month)
        deudas_evt = qs_evt.aggregate(t=Sum('amount_owed'))['t'] or 0

        deudas = deudas_tx + deudas_evt

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

        # Agregar deudas de eventos
        participaciones = EventoParticipant.objects.filter(
            evento__parche_id=parche_id, paid=False
        ).filter(
            Q(user=user) | Q(evento__responsible=user)
        ).select_related('user', 'evento__responsible')

        for p in participaciones:
            # Si el usuario es quien debe
            if p.user == user and p.evento.responsible and p.evento.responsible != user:
                otro = p.evento.responsible
                resumen.setdefault(otro.username, 0)
                resumen[otro.username] -= float(p.amount_owed)
            
            # Si al usuario le deben (es el responsable del evento)
            if p.evento.responsible == user and p.user != user:
                otro = p.user
                resumen.setdefault(otro.username, 0)
                resumen[otro.username] += float(p.amount_owed)

        return Response(resumen)


class BoletinInicioView(APIView):
    """RF_25 – Boletín de balance para la página de inicio: resumen global del usuario."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Total pagado y recibido globalmente
        total_pagado = Transaccion.objects.filter(
            from_user=user, type='pago'
        ).aggregate(t=Sum('amount'))['t'] or 0

        total_recibido = Transaccion.objects.filter(
            to_user=user, type='pago'
        ).aggregate(t=Sum('amount'))['t'] or 0

        total_deudas = Transaccion.objects.filter(
            from_user=user, type='deuda'
        ).aggregate(t=Sum('amount'))['t'] or 0

        # Deudas pendientes de eventos (RF_22)
        deudas_pendientes = EventoParticipant.objects.filter(
            user=user, paid=False
        ).aggregate(t=Sum('amount_owed'))['t'] or 0

        # Número de parches activos
        num_parches = Membership.objects.filter(user=user).count()

        return Response({
            'total_pagado':             total_pagado,
            'total_recibido':           total_recibido,
            'total_deudas_transaccion': total_deudas,
            'deudas_pendientes_eventos': deudas_pendientes,
            'saldo_neto':               total_recibido - total_pagado - total_deudas,
            'num_parches':              num_parches,
        })