from typing import Any, Dict

from .models import BankAccount, User


def create_registered_user(user_data: Dict[str, Any]) -> User:
    """Create a new application user with the provided profile fields."""
    return User.objects.create_user(
        username=user_data['username'],
        email=user_data.get('email', ''),
        password=user_data['password'],
        nickname=user_data.get('nickname', ''),
        bio=user_data.get('bio', ''),
    )


def create_bank_account(user: User, account_data: Dict[str, Any]) -> BankAccount:
    """Create a bank account linked to the authenticated user."""
    return BankAccount.objects.create(user=user, **account_data)
