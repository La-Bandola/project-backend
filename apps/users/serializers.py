from typing import Any, Dict

from rest_framework import serializers

from .models import BankAccount, User
from .services import create_bank_account, create_registered_user


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=3)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'nickname', 'bio']

    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create a user through the service layer."""
        return create_registered_user(validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'nickname', 'bio', 'photo']
        read_only_fields = ['id', 'username']


class BankAccountSerializer(serializers.ModelSerializer):
    """Validate and persist a user bank account."""

    number = serializers.CharField(min_length=5)

    class Meta:
        model = BankAccount
        fields = ['id', 'bank', 'number', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data: Dict[str, Any]) -> BankAccount:
        """Create a bank account through the service layer."""
        user = self.context['request'].user
        return create_bank_account(user, validated_data)