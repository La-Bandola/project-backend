from rest_framework import serializers
from .models import Transaccion, Balance
from apps.users.serializers import UserSerializer

class TransaccionSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user   = UserSerializer(read_only=True)
    to_user_id = serializers.IntegerField(write_only=True, required=False)
    parche_name = serializers.CharField(source='parche.name', read_only=True)

    class Meta:
        model  = Transaccion
        fields = [
            'id', 'parche', 'parche_name', 'from_user', 'to_user', 'to_user_id',
            'amount', 'type', 'concept', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'parche', 'from_user']

    def create(self, validated_data):
        to_user_id = validated_data.pop('to_user_id', None)
        if to_user_id:
            from apps.users.models import User
            validated_data['to_user'] = User.objects.get(id=to_user_id)
        return Transaccion.objects.create(**validated_data)


class BalanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model  = Balance
        fields = ['id', 'parche', 'user', 'amount', 'updated_at']
        read_only_fields = ['id', 'parche', 'user', 'updated_at']