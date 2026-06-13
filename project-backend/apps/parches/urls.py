from django.urls import path
from .views import ParcheListCreateView, ParcheDetailView, JoinParcheView, ParcheMembersView

urlpatterns = [
    path('',          ParcheListCreateView.as_view(), name='parche_list'),
    path('<int:pk>/', ParcheDetailView.as_view(),     name='parche_detail'),
    path('join/',     JoinParcheView.as_view(),        name='parche_join'),
    path('<int:pk>/members/',  ParcheMembersView.as_view(),     name='parche_members'),
]