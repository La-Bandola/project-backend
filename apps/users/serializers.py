from rest_framework import serializers
from .models import User, BankAccount

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'password', 'nickname', 'bio']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            nickname=validated_data.get('nickname', ''),
            bio=validated_data.get('bio', ''),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'nickname', 'bio', 'photo']
        read_only_fields = ['id', 'username']


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BankAccount
        fields = ['id', 'bank', 'number', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']