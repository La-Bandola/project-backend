from dataclasses import dataclass
from typing import Optional
import pytest;


ALLOWED_BANKS = ['nequi', 'daviplata', 'bancolombia', 'otro']


def validate_bank_account(data: dict) -> dict:
    errors = []

    bank = data.get('bank', '').strip().lower()
    number = data.get('number', '').strip()

    if not bank:
        errors.append("El banco es requerido")
    elif bank not in ALLOWED_BANKS:
        errors.append(f"Banco no permitido. Opciones: {', '.join(ALLOWED_BANKS)}")

    if not number:
        errors.append("El número o llave de cuenta es requerido")
    elif len(number) < 5:
        errors.append("El número de cuenta debe tener al menos 5 caracteres")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
    }


class TestBankAccounts:

    def test_accept_account_with_valid_data(self):
        data = {
            'bank': 'nequi',
            'number': '3001234567',
            'is_primary': True,
        }
        result = validate_bank_account(data)

        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_reject_not_allowed_bank(self):
        data = {
            'bank': 'bbva',
            'number': '3001234567',
        }
        result = validate_bank_account(data)

        assert result['valid'] is False
        assert any('no permitido' in e for e in result['errors'])

    def test_reject_empty_number(self):
        data = {
            'bank': 'nequi',
            'number': '',
        }
        result = validate_bank_account(data)

        assert result['valid'] is False
        assert any('número' in e.lower() or 'llave' in e.lower() for e in result['errors'])


@dataclass
class UserRegistration:
    username: str
    email: str
    password: str
    nickname: Optional[str] = None


def validate_registration(data: dict) -> dict:
    errors = []

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username:
        errors.append("El username es requerido")
    elif len(username) < 3:
        errors.append("El username debe tener al menos 3 caracteres")

    if not email:
        errors.append("El email es requerido")
    elif '@' not in email:
        errors.append("El email no es válido")

    if not password:
        errors.append("La contraseña es requerida")
    elif len(password) < 8:
        errors.append("La contraseña debe tener al menos 8 caracteres")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
    }


class TestUserRegistration:

    def test_registration_with_correct_data(self):
        data = {
            'username': 'testuser',
            'email': 'test@parcheck.com',
            'password': 'password123',
        }
        result = validate_registration(data)

        assert result['valid'] is True
        assert len(result['errors']) == 0

    def test_reject_without_password(self):
        data = {
            'username': 'testuser',
            'email': 'test@parcheck.com',
            'password': '',
        }
        result = validate_registration(data)

        assert result['valid'] is False
        assert any('contraseña' in e.lower() for e in result['errors'])

    def test_reject_password_too_short(self):
        data = {
            'username': 'testuser',
            'email': 'test@parcheck.com',
            'password': '1234567',  # 7 caracteres, mínimo es 8
        }
        result = validate_registration(data)

        assert result['valid'] is False
        assert any('8 caracteres' in e for e in result['errors'])