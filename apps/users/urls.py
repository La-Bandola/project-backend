from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, LogoutView, ProfileView, ChangePasswordView,
    BankAccountListCreateView, BankAccountDetailView,
    ContactBankAccountsView
)

urlpatterns = [
    # Autenticación (RF_1, RF_2, RF_3, RF_4)
    path('register/',              RegisterView.as_view(),        name='register'),
    path('login/',                 TokenObtainPairView.as_view(), name='login'),
    path('logout/',                LogoutView.as_view(),          name='logout'),
    path('token/refresh/',         TokenRefreshView.as_view(),    name='token_refresh'),

    # Perfil (RF_6)
    path('me/',                    ProfileView.as_view(),         name='profile'),
    path('me/change-password/',    ChangePasswordView.as_view(),  name='change_password'),

    # Cuentas bancarias propias (RF_5)
    path('me/bank-accounts/',             BankAccountListCreateView.as_view(), name='bank_accounts'),
    path('me/bank-accounts/<int:pk>/',    BankAccountDetailView.as_view(),     name='bank_account_detail'),

    # Cuentas bancarias de contactos del parche (RF_7)
    path('parches/<int:parche_id>/contacts/bank-accounts/', ContactBankAccountsView.as_view(), name='contact_bank_accounts'),
]