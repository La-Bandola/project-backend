import pytest

from apps.users.serializers import BankAccountSerializer, RegisterSerializer


pytestmark = pytest.mark.django_db


class TestUserSerializers:
    def test_register_serializer_rejects_invalid_email_and_short_username(self):
        serializer = RegisterSerializer(
            data={
                'username': 'ab',
                'email': 'not-an-email',
                'password': 'short',
            }
        )

        assert serializer.is_valid() is False
        assert 'username' in serializer.errors
        assert 'email' in serializer.errors
        assert 'password' in serializer.errors

    def test_bank_account_serializer_rejects_short_number(self):
        serializer = BankAccountSerializer(
            data={
                'bank': 'nequi',
                'number': '123',
                'is_primary': True,
            }
        )

        assert serializer.is_valid() is False
        assert 'number' in serializer.errors
