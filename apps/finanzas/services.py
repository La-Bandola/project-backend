from decimal import Decimal
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError

from apps.users.models import User

from .models import Transaccion


TRANSACTION_TYPES = {'pago', 'deuda', 'ingreso'}


def create_transaction(
    *,
    parche: Any,
    from_user: User,
    amount: Any,
    transaction_type: str,
    concept: str = '',
    destination_account: str = '',
    to_user: Optional[User] = None,
    evento: Optional[Any] = None,
) -> Transaccion:
    """Create a finance transaction with input validation."""
    if transaction_type not in TRANSACTION_TYPES:
        raise ValidationError('Tipo de transacción inválido')

    if not amount:
        raise ValidationError('El monto es obligatorio')

    normalized_amount = Decimal(str(amount))
    if normalized_amount <= 0:
        raise ValidationError('El monto debe ser mayor que cero')

    return Transaccion.objects.create(
        parche=parche,
        from_user=from_user,
        to_user=to_user,
        evento=evento,
        amount=normalized_amount,
        type=transaction_type,
        concept=concept,
        destination_account=destination_account,
    )


def pay_event_participant(*, participant: Any, amount: Any, concept: str, destination_account: str) -> Transaccion:
    """Create a payment transaction for an event participant."""
    if participant.user == participant.evento.responsible:
        raise ValidationError('El responsable del evento no necesita pagar')

    return create_transaction(
        parche=participant.evento.parche,
        from_user=participant.user,
        amount=amount,
        transaction_type='pago',
        concept=concept,
        destination_account=destination_account,
        to_user=participant.evento.responsible,
        evento=participant.evento,
    )
