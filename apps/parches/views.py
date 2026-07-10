from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Membership, Parche
from .serializers import JoinParcheSerializer, ParcheSerializer
from .services import create_parche, join_parche

class ParcheListCreateView(generics.ListCreateAPIView):
    serializer_class   = ParcheSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Parche.objects.filter(memberships__user=self.request.user)

    def perform_create(self, serializer):
        parche = create_parche(self.request.user, serializer.validated_data)
        serializer.instance = parche

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
            parche = join_parche(request.user, invite_code)
        except ValidationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

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