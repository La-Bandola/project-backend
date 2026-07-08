from rest_framework import serializers
from .models import EspacioAhorro, AporteAhorro
from apps.users.serializers import UserSerializer


class AporteAhorroSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model  = AporteAhorro
        fields = ['id', 'user', 'amount', 'note', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class EspacioAhorroSerializer(serializers.ModelSerializer):
    creator            = UserSerializer(read_only=True)
    aportes            = AporteAhorroSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model  = EspacioAhorro
        fields = [
            'id', 'parche', 'creator', 'name', 'description',
            'goal_amount', 'current_amount', 'target_date',
            'progress_percentage', 'aportes', 'created_at'
        ]
        read_only_fields = ['id', 'parche', 'creator', 'current_amount', 'created_at']
