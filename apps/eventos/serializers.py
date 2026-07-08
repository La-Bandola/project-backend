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
    custom_amounts = serializers.DictField(
        child=serializers.DecimalField(max_digits=12, decimal_places=2),
        write_only=True, required=False,
        help_text="Mapa user_id -> monto para split_type='custom' (RF_14)"
    )

    class Meta:
        model  = Evento
        fields = [
            'id', 'parche', 'name', 'total_amount', 'split_type',
            'responsible', 'responsible_id',
            'pay_immediately', 'status',
            'receipt',
            'participants', 'participant_ids', 'custom_amounts',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'parche']

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        responsible_id  = validated_data.pop('responsible_id', None)
        custom_amounts  = validated_data.pop('custom_amounts', {})

        if responsible_id:
            from apps.users.models import User
            validated_data['responsible'] = User.objects.get(id=responsible_id)

        # RF_16: si pay_immediately=False, el estado inicia en 'waiting'
        if not validated_data.get('pay_immediately', True):
            validated_data['status'] = 'waiting'

        evento = Evento.objects.create(**validated_data)

        # RF_14 / RF_26 – cálculo automático de montos
        if participant_ids:
            from apps.users.models import User
            split_type = evento.split_type
            count      = len(participant_ids)
            for uid in participant_ids:
                user = User.objects.get(id=uid)
                if split_type == 'equal':
                    amount = evento.total_amount / count
                elif split_type == 'custom':
                    amount = custom_amounts.get(str(uid), 0)
                else:
                    amount = 0
                EventoParticipant.objects.create(
                    evento=evento, user=user, amount_owed=amount
                )

        return evento

    def update(self, instance, validated_data):
        participant_ids = validated_data.pop('participant_ids', None)
        custom_amounts  = validated_data.pop('custom_amounts', {})
        validated_data.pop('responsible_id', None)

        instance.name            = validated_data.get('name',            instance.name)
        instance.total_amount    = validated_data.get('total_amount',    instance.total_amount)
        instance.split_type      = validated_data.get('split_type',      instance.split_type)
        instance.pay_immediately = validated_data.get('pay_immediately', instance.pay_immediately)
        instance.status          = validated_data.get('status',          instance.status)
        instance.save()

        if participant_ids is not None:
            from apps.users.models import User
            instance.participants.all().delete()
            count = len(participant_ids)
            for uid in participant_ids:
                user = User.objects.get(id=uid)
                if instance.split_type == 'equal':
                    amount = instance.total_amount / count
                elif instance.split_type == 'custom':
                    amount = custom_amounts.get(str(uid), 0)
                else:
                    amount = 0
                EventoParticipant.objects.create(
                    evento=instance, user=user, amount_owed=amount
                )

        return instance


class SuscripcionSerializer(serializers.ModelSerializer):
    responsible    = UserSerializer(read_only=True)
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

    def update(self, instance, validated_data):
        responsible_id = validated_data.pop('responsible_id', None)
        if responsible_id:
            from apps.users.models import User
            validated_data['responsible'] = User.objects.get(id=responsible_id)
        return super().update(instance, validated_data)
