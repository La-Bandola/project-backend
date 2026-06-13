from django.urls import path
from .views import (
    TransaccionListCreateView, TransaccionDetailView,
    BalanceParcheView, BalancePersonalView, ResumenMutuoView
)

urlpatterns = [
    path('<int:parche_id>/transacciones/',          TransaccionListCreateView.as_view(), name='transaccion_list'),
    path('<int:parche_id>/transacciones/<int:pk>/', TransaccionDetailView.as_view(),     name='transaccion_detail'),
    path('<int:parche_id>/balance/',                BalanceParcheView.as_view(),         name='balance_parche'),
    path('<int:parche_id>/balance/personal/',       BalancePersonalView.as_view(),       name='balance_personal'),
    path('<int:parche_id>/balance/mutuo/',          ResumenMutuoView.as_view(),          name='balance_mutuo'),
]