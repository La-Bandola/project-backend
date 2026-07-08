from django.urls import path
from .views import (
    EventoListCreateView, EventoDetailView,
    MarcarPagadoView, UploadPaymentProofView,
    PendingDebtsView,
    SuscripcionListCreateView, SuscripcionDetailView
)

urlpatterns = [
    # Eventos (RF_12, RF_13, RF_14, RF_15, RF_16)
    path('<int:parche_id>/eventos/',          EventoListCreateView.as_view(),    name='evento_list'),
    path('<int:parche_id>/eventos/<int:pk>/', EventoDetailView.as_view(),        name='evento_detail'),

    # Participantes
    path('participantes/<int:pk>/pagar/',    MarcarPagadoView.as_view(),         name='marcar_pagado'),
    path('participantes/<int:pk>/soporte/',  UploadPaymentProofView.as_view(),   name='upload_proof'),  # RF_32

    # Deudas pendientes (RF_22)
    path('deudas-pendientes/',               PendingDebtsView.as_view(),         name='deudas_pendientes'),

    # Suscripciones (RF_18, RF_19)
    path('<int:parche_id>/suscripciones/',          SuscripcionListCreateView.as_view(), name='suscripcion_list'),
    path('<int:parche_id>/suscripciones/<int:pk>/', SuscripcionDetailView.as_view(),     name='suscripcion_detail'),
]