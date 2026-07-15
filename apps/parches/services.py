import random
import string
from typing import Any, Dict

from django.core.exceptions import ValidationError

from apps.users.models import User

from .models import Membership, Parche


INVITE_CODE_LENGTH = 8
CREATOR_ROLE = 'creator'
MEMBER_ROLE = 'member'


def generate_invite_code(length: int = INVITE_CODE_LENGTH) -> str:
    """Generate a random invite code for a parche."""
    if length <= 0:
        raise ValueError('La longitud del código debe ser mayor que cero.')

    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


def create_parche(user: User, parche_data: Dict[str, Any]) -> Parche:
    """Create a parche with the requesting user as creator and membership owner."""
    invite_code = generate_invite_code()
    parche = Parche.objects.create(
        name=parche_data['name'],
        description=parche_data.get('description', ''),
        creator=user,
        invite_code=invite_code,
    )
    Membership.objects.create(parche=parche, user=user, role=CREATOR_ROLE)
    return parche


def join_parche(user: User, invite_code: str) -> Parche:
    """Join an existing parche using its invite code."""
    try:
        parche = Parche.objects.get(invite_code=invite_code)
    except Parche.DoesNotExist as exc:
        raise ValidationError('Código de invitación inválido') from exc

    if parche.memberships.filter(user=user).exists():
        raise ValidationError('Ya eres miembro de este parche')

    Membership.objects.create(parche=parche, user=user, role=MEMBER_ROLE)
    return parche
