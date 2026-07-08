from django.urls import path
from .views import (
    TransaccionListCreateView, TransaccionDetailView,
    BalanceParcheView, BalancePersonalView,
    BalanceMensualView, ResumenMutuoView,
    BoletinInicioView
)

urlpatterns = [
    # Historial de transacciones (RF_27, RF_28, RF_29)
    path('<int:parche_id>/transacciones/',          TransaccionListCreateView.as_view(), name='transaccion_list'),
    path('<int:parche_id>/transacciones/<int:pk>/', TransaccionDetailView.as_view(),     name='transaccion_detail'),

    # Balance por parche (RF_23)
    path('<int:parche_id>/balance/',                BalanceParcheView.as_view(),         name='balance_parche'),

    # Balance personal en un parche, con filtros de mes (RF_21)
    path('<int:parche_id>/balance/personal/',       BalancePersonalView.as_view(),       name='balance_personal'),

    # Balance mutuo por integrante (RF_24)
    path('<int:parche_id>/balance/mutuo/',          ResumenMutuoView.as_view(),          name='balance_mutuo'),

    # Balance mensual consolidado (RF_21)
    path('balance/mensual/',                        BalanceMensualView.as_view(),        name='balance_mensual'),

    # Boletín de inicio (RF_25)
    path('boletin/',                                BoletinInicioView.as_view(),         name='boletin_inicio'),
]