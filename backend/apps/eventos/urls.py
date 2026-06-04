from django.urls import path
from .views import (
    EventoListCreateView, EventoDetailView,
    MarcarPagadoView,
    SuscripcionListCreateView, SuscripcionDetailView
)

urlpatterns = [
    path('<int:parche_id>/eventos/',          EventoListCreateView.as_view(),    name='evento_list'),
    path('<int:parche_id>/eventos/<int:pk>/', EventoDetailView.as_view(),        name='evento_detail'),
    path('participantes/<int:pk>/pagar/',     MarcarPagadoView.as_view(),        name='marcar_pagado'),
    path('<int:parche_id>/suscripciones/',    SuscripcionListCreateView.as_view(), name='suscripcion_list'),
    path('<int:parche_id>/suscripciones/<int:pk>/', SuscripcionDetailView.as_view(), name='suscripcion_detail'),
]