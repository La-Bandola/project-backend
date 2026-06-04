from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, BankAccountListCreateView, BankAccountDeleteView

urlpatterns = [
    path('register/',              RegisterView.as_view(),            name='register'),
    path('login/',                 TokenObtainPairView.as_view(),     name='login'),
    path('token/refresh/',         TokenRefreshView.as_view(),        name='token_refresh'),
    path('me/',                    ProfileView.as_view(),             name='profile'),
    path('me/bank-accounts/',      BankAccountListCreateView.as_view(), name='bank_accounts'),
    path('me/bank-accounts/<int:pk>/', BankAccountDeleteView.as_view(), name='bank_account_delete'),
]