from rest_framework import serializers
from .models import Evento, EventoParticipant, Suscripcion
from apps.users.serializers import UserSerializer

class EventoParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model  = EventoParticipant
        fields = ['id', 'user', 'amount_owed', 'paid', 'payment_proof', 'paid_at']

class EventoSerializer(serializers.ModelSerializer):
    responsible  = UserSerializer(read_only=True)
    participants = EventoParticipantSerializer(many=True, read_only=True)

    responsible_id    = serializers.IntegerField(write_only=True, required=False)
    participant_ids   = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model  = Evento
        fields = [
            'id', 'parche', 'name', 'total_amount', 'split_type',
            'responsible', 'responsible_id', 'receipt',
            'participants', 'participant_ids', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'parche']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        responsible_id  = validated_data.pop('responsible_id', None)

        if responsible_id:
            from apps.users.models import User
            validated_data['responsible'] = User.objects.get(id=responsible_id)

        evento = Evento.objects.create(**validated_data)

        if participant_ids:
            from apps.users.models import User
            split_type = evento.split_type
            count      = len(participant_ids)
            for uid in participant_ids:
                user = User.objects.get(id=uid)
                if split_type == 'equal':
                    amount = evento.total_amount / count
                else:
                    amount = 0
                EventoParticipant.objects.create(
                    evento=evento, user=user, amount_owed=amount
                )

        return evento


class SuscripcionSerializer(serializers.ModelSerializer):
    responsible = UserSerializer(read_only=True)
    responsible_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model  = Suscripcion
        fields = ['id', 'parche', 'name', 'amount', 'cutoff_date', 'responsible', 'responsible_id', 'created_at']
        read_only_fields = ['id', 'created_at', 'parche']

    def create(self, validated_data):
        responsible_id = validated_data.pop('responsible_id', None)
        if responsible_id:
            from apps.users.models import User
            validated_data['responsible'] = User.objects.get(id=responsible_id)
        return Suscripcion.objects.create(**validated_data)