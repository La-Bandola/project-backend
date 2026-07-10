from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.throttling import AnonRateThrottle
from .models import User, BankAccount
from .serializers import (
    RegisterSerializer, UserSerializer,
    BankAccountSerializer, ChangePasswordSerializer
)
from apps.parches.models import Membership


class LoginRateThrottle(AnonRateThrottle):
    """Limita intentos de login a 5 por minuto (RF_2)."""
    rate = '5/min'


class RegisterView(generics.CreateAPIView):
    """RF_4 – Registro de nuevos usuarios."""
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    serializer.data,
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """RF_2 / RNF_1 – Cierre de sesión seguro con blacklist del refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Se requiere el refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """RF_6 – El usuario puede ver y editar su perfil (foto, nickname, bio)."""
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """RF_6 / RNF_1 – Cambio seguro de contraseña."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Contraseña actualizada correctamente.'},
            status=status.HTTP_200_OK
        )


class BankAccountListCreateView(generics.ListCreateAPIView):
    """RF_5 – Listar y agregar cuentas bancarias propias."""
    serializer_class   = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # El BankAccountSerializer.create() ya obtiene el user desde
        # self.context['request'].user — no se pasa como kwarg para evitar duplicados.
        serializer.save()


class BankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF_5 – Editar o eliminar una cuenta bancaria propia."""
    serializer_class   = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)


class ContactBankAccountsView(APIView):
    """RF_7 – Ver cuentas bancarias de los miembros de un parche."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, parche_id):
        # Verificar que el usuario pertenece al parche
        if not Membership.objects.filter(
            parche_id=parche_id, user=request.user
        ).exists():
            return Response(
                {'error': 'No perteneces a este parche.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtener todos los usuarios del parche (excepto el solicitante)
        miembro_ids = Membership.objects.filter(
            parche_id=parche_id
        ).exclude(user=request.user).values_list('user_id', flat=True)

        cuentas = BankAccount.objects.filter(user_id__in=miembro_ids).select_related('user')

        data = [
            {
                'user_id':    c.user.id,
                'username':   c.user.username,
                'nickname':   c.user.nickname,
                'bank':       c.bank,
                'number':     c.number,
                'is_primary': c.is_primary,
            }
            for c in cuentas
        ]
        return Response(data, status=status.HTTP_200_OK)