from django.urls import path
from .views import EspacioAhorroListCreateView, EspacioAhorroDetailView, AporteAhorroCreateView

urlpatterns = [
    # Espacios de ahorro en un parche (RF_20)
    path('<int:parche_id>/ahorros/',          EspacioAhorroListCreateView.as_view(), name='ahorro_list'),
    path('<int:parche_id>/ahorros/<int:pk>/', EspacioAhorroDetailView.as_view(),     name='ahorro_detail'),

    # Aportes a un espacio (RF_20)
    path('ahorros/<int:espacio_id>/aportar/', AporteAhorroCreateView.as_view(),      name='ahorro_aportar'),
]
