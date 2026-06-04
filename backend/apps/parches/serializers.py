from rest_framework import serializers
from .models import Parche, Membership
from apps.users.serializers import UserSerializer

class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model  = Membership
        fields = ['id', 'user', 'role', 'joined_at']

class ParcheSerializer(serializers.ModelSerializer):
    creator     = UserSerializer(read_only=True)
    memberships = MembershipSerializer(many=True, read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model  = Parche
        fields = ['id', 'name', 'description', 'creator', 'invite_code', 'memberships', 'members_count', 'created_at']
        read_only_fields = ['id', 'creator', 'invite_code', 'created_at']

    def get_members_count(self, obj):
        return obj.memberships.count()

class JoinParcheSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=12)