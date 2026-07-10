import pytest

from apps.parches.models import Parche
from apps.parches.services import create_parche, join_parche
from apps.users.models import User


@pytest.mark.django_db
def test_create_parche_service_creates_parche_and_creator_membership():
    user = User.objects.create_user(
        username='owner',
        email='owner@example.com',
        password='password123',
    )

    parche = create_parche(user, {'name': 'Trip', 'description': 'Weekend plan'})

    assert isinstance(parche, Parche)
    assert parche.name == 'Trip'
    assert parche.creator == user
    assert parche.invite_code
    assert parche.memberships.filter(user=user, role='creator').exists()


@pytest.mark.django_db
def test_join_parche_service_creates_member_membership():
    owner = User.objects.create_user(
        username='owner2',
        email='owner2@example.com',
        password='password123',
    )
    member = User.objects.create_user(
        username='member',
        email='member@example.com',
        password='password123',
    )

    parche = create_parche(owner, {'name': 'Dinner'})

    joined_parche = join_parche(member, parche.invite_code)

    assert joined_parche == parche
    assert parche.memberships.filter(user=member, role='member').exists()
