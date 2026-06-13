from rest_framework import generics, permissions
from .models import Evento, EventoParticipant, Suscripcion
from .serializers import EventoSerializer, EventoParticipantSerializer, SuscripcionSerializer
from apps.parches.models import Parche

class EventoListCreateView(generics.ListCreateAPIView):
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
    serializer_class   = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Evento.objects.filter(
            parche__memberships__user=self.request.user
        )


class MarcarPagadoView(generics.UpdateAPIView):
    serializer_class   = EventoParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EventoParticipant.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        from django.utils import timezone
        serializer.save(paid=True, paid_at=timezone.now())


class SuscripcionListCreateView(generics.ListCreateAPIView):
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
    serializer_class   = SuscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Suscripcion.objects.filter(
            parche__memberships__user=self.request.user
        )