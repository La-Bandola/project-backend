from typing import Any, Dict

from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Membership, Parche


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model  = Membership
        fields = ['id', 'user', 'role', 'joined_at']

class ParcheSerializer(serializers.ModelSerializer):
    """Serialize parche details and related memberships."""

    creator       = UserSerializer(read_only=True)
    memberships   = MembershipSerializer(many=True, read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model  = Parche
        fields = ['id', 'name', 'description', 'creator', 'invite_code', 'memberships', 'members_count', 'created_at']
        read_only_fields = ['id', 'creator', 'invite_code', 'created_at']

    def get_members_count(self, obj: Parche) -> int:
        """Return the number of active members for the parche."""
        return obj.memberships.count()


class JoinParcheSerializer(serializers.Serializer):
    """Validate invite code input for joining a parche."""

    invite_code = serializers.CharField(max_length=12)