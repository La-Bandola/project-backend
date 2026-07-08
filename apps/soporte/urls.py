from django.urls import path
from .views import FeedbackCreateView, FeedbackListView

urlpatterns = [
    # RF_30 – Enviar feedback (opinión, reclamo, sugerencia)
    path('feedback/',  FeedbackCreateView.as_view(), name='feedback_create'),
    path('feedback/mis-envios/', FeedbackListView.as_view(), name='feedback_list'),
]
