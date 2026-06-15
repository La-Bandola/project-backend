
import re
import string
import random
import pytest


def generate_invite_code(length=8):
    
    if length <= 0:
        raise ValueError("La longitud debe ser mayor a 0")
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def validate_invite_code(code):
    

    if not code or not isinstance(code, str):
        return False
    if len(code) < 6 or len(code) > 12:
        return False
    return bool(re.match(r'^[A-Z0-9]+$', code))


class TestInviteCode:

    def test_generate_correct_format_code(self):
        for _ in range(100):
            code = generate_invite_code()
            assert len(code) == 8
            assert re.match(r'^[A-Z0-9]+$', code), f"Formato inválido: {code}"

    def test_reject_invalid_characters_code(self):
        
        invalid_codes = [
            "abc12345",   # minúsculas
            "ABC 123",    # espacios
            "ABC-1234",   # guion
            "ABC@1234",   # arroba
            "abc!1234",   # especial
        ]
        for code in invalid_codes:
            assert validate_invite_code(code) is False, f"Debió rechazar: {code}"

    def test_reject_empty_code(self):
        
        assert validate_invite_code("")    is False
        assert validate_invite_code(None)  is False
        assert validate_invite_code("   ") is False