from rest_framework import serializers
from .models import Evento, EventoParticipant, Suscripcion
from apps.users.serializers import UserSerializer
from apps.users.models import BankAccount


class BankAccountMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'bank', 'number', 'is_primary']


class UserWithBankSerializer(UserSerializer):
    cuentas_bancarias = BankAccountMiniSerializer(source='bank_accounts', many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['cuentas_bancarias']


class EventoParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    paid = serializers.BooleanField(source='is_fully_paid', read_only=True)

    class Meta:
        model  = EventoParticipant
        fields = ['id', 'user', 'amount_owed', 'amount_paid', 'paid', 'payment_proof', 'paid_at']


class EventoSerializer(serializers.ModelSerializer):
    responsible  = UserWithBankSerializer(read_only=True)
    participants = EventoParticipantSerializer(many=True, read_only=True)

    responsible_id    = serializers.IntegerField(write_only=True, required=False)
    participant_ids   = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    custom_amounts = serializers.DictField(    
        child=serializers.DecimalField(max_digits=12, decimal_places=2),
        write_only=True,
        required=False,
        default=dict
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
            
        if validated_data.get('split_type') == 'custom' and participant_ids:
            total = validated_data.get('total_amount', 0)
            suma  = sum(
                float(custom_amounts.get(str(uid), 0))
                for uid in participant_ids
            )
            if round(suma, 2) != round(float(total), 2):
                raise serializers.ValidationError({
                    'custom_amounts': f'Los montos asignados ${suma:,.0f} no suman el total del evento ${float(total):,.0f}'
                })

        evento = Evento.objects.create(**validated_data)

        if participant_ids:
            from apps.users.models import User
            from django.utils import timezone
            count = len(participant_ids)
            for uid in participant_ids:
                user = User.objects.get(id=uid)
                if evento.split_type == 'equal':
                    amount = evento.total_amount / count
                elif evento.split_type == 'custom':
                    amount = custom_amounts.get(str(uid), 0)
                else:
                    amount = 0
                
                is_responsible = (evento.responsible is not None and user.id == evento.responsible.id)
                EventoParticipant.objects.create(
                    evento=evento, 
                    user=user, 
                    amount_owed=amount,
                    paid=is_responsible,
                    paid_at=timezone.now() if is_responsible else None
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
            from django.utils import timezone
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
                
                is_responsible = (instance.responsible is not None and user.id == instance.responsible.id)
                EventoParticipant.objects.create(
                    evento=instance, 
                    user=user, 
                    amount_owed=amount,
                    paid=is_responsible,
                    paid_at=timezone.now() if is_responsible else None
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
