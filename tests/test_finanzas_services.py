from decimal import Decimal

import pytest

from apps.eventos.models import Evento, EventoParticipant
from apps.finanzas.models import Transaccion
from apps.finanzas.services import create_transaction, pay_event_participant
from apps.parches.models import Parche
from apps.users.models import User


@pytest.mark.django_db
def test_create_transaction_service_persists_a_transaction():
    creator = User.objects.create_user(username='creator', email='creator@example.com', password='password123')
    recipient = User.objects.create_user(username='recipient', email='recipient@example.com', password='password123')
    parche = Parche.objects.create(name='Test parche', creator=creator, invite_code='INVITE01')

    transaction = create_transaction(
        parche=parche,
        from_user=creator,
        amount='15.50',
        transaction_type='pago',
        concept='Dinner',
        destination_account='1234',
        to_user=recipient,
    )

    assert isinstance(transaction, Transaccion)
    assert transaction.parche == parche
    assert transaction.from_user == creator
    assert transaction.to_user == recipient
    assert transaction.amount == Decimal('15.50')


@pytest.mark.django_db
def test_pay_event_participant_service_creates_payment_transaction():
    responsible = User.objects.create_user(username='responsible', email='responsible@example.com', password='password123')
    participant_user = User.objects.create_user(username='participant', email='participant@example.com', password='password123')
    parche = Parche.objects.create(name='Evento parche', creator=responsible, invite_code='INVITE02')
    evento = Evento.objects.create(
        parche=parche,
        name='Dinner',
        total_amount=Decimal('100.00'),
        responsible=responsible,
    )
    participant = EventoParticipant.objects.create(
        evento=evento,
        user=participant_user,
        amount_owed=Decimal('50.00'),
    )

    transaction = pay_event_participant(
        participant=participant,
        amount='20.00',
        concept='Parcial',
        destination_account='4321',
    )

    assert transaction is not None
    assert transaction.from_user == participant_user
    assert transaction.to_user == responsible
    assert transaction.evento == evento
    assert transaction.amount == Decimal('20.00')
