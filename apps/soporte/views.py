from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Feedback
from .serializers import FeedbackSerializer


class FeedbackCreateView(generics.CreateAPIView):
    """RF_30 – El usuario puede enviar una opinión, reclamo o sugerencia."""
    serializer_class   = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'detail': 'Tu comentario ha sido recibido. ¡Gracias por ayudarnos a mejorar!',
             'feedback': serializer.data},
            status=status.HTTP_201_CREATED
        )


class FeedbackListView(generics.ListAPIView):
    """RF_30 – Historial de feedbacks enviados por el usuario."""
    serializer_class   = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)
