from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Q
from .models import Transaccion, Balance
from .serializers import TransaccionSerializer, BalanceSerializer
from apps.parches.models import Parche, Membership
from apps.eventos.models import EventoParticipant
from apps.ahorros.models import AporteAhorro


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

        enviado = tx_filter(Transaccion.objects.filter(parche_id=parche_id, from_user=user, type='pago')).aggregate(t=Sum('amount'))['t'] or 0
        recibido = tx_filter(Transaccion.objects.filter(parche_id=parche_id, to_user=user, type='pago')).aggregate(t=Sum('amount'))['t'] or 0
        deudas_tx = tx_filter(Transaccion.objects.filter(parche_id=parche_id, from_user=user, type='deuda')).aggregate(t=Sum('amount'))['t'] or 0
        
        qs_evt_deuda = EventoParticipant.objects.filter(evento__parche_id=parche_id, user=user, paid=False)
        if year: qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__year=year)
        if month: qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__month=month)
        deudas_evt = qs_evt_deuda.aggregate(t=Sum('amount_owed'))['t'] or 0
        
        deudas = float(deudas_tx) + float(deudas_evt)

        return Response({
            'pagado':   float(enviado),
            'recibido': float(recibido),
            'deudas':   deudas,
            'neto':     float(recibido) - float(enviado) - deudas,
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

        qs_evt_deuda = EventoParticipant.objects.filter(user=user, paid=False)
        if year: qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__year=year)
        if month: qs_evt_deuda = qs_evt_deuda.filter(evento__created_at__month=month)
        deudas_evt = qs_evt_deuda.aggregate(t=Sum('amount_owed'))['t'] or 0

        deudas   = float(deudas_tx) + float(deudas_evt)
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