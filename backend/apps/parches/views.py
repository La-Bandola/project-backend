import random
import string
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Parche, Membership
from .serializers import ParcheSerializer, JoinParcheSerializer

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class ParcheListCreateView(generics.ListCreateAPIView):
    serializer_class   = ParcheSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Parche.objects.filter(memberships__user=self.request.user)

    def perform_create(self, serializer):
        invite_code = generate_invite_code()
        parche = serializer.save(creator=self.request.user, invite_code=invite_code)
        Membership.objects.create(
            parche=parche,
            user=self.request.user,
            role='creator'
        )

class ParcheDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ParcheSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Parche.objects.filter(memberships__user=self.request.user)

class JoinParcheView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = JoinParcheSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invite_code = serializer.validated_data['invite_code']

        try:
            parche = Parche.objects.get(invite_code=invite_code)
        except Parche.DoesNotExist:
            return Response({'error': 'Código de invitación inválido'}, status=status.HTTP_404_NOT_FOUND)

        if Membership.objects.filter(parche=parche, user=request.user).exists():
            return Response({'error': 'Ya eres miembro de este parche'}, status=status.HTTP_400_BAD_REQUEST)

        Membership.objects.create(parche=parche, user=request.user, role='member')
        return Response(ParcheSerializer(parche).data, status=status.HTTP_200_OK)
    


User = get_user_model()

class ParcheMembersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        miembros = Membership.objects.filter(
            parche_id=pk
        ).select_related('user')

        data = [
            {
                'id': miembro.user.id,
                'username': miembro.user.username
            }
            for miembro in miembros
        ]

        return Response(data)