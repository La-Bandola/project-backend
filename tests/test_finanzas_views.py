
from decimal import Decimal
import pytest


def calcular_division_igual(total_amount, participant_ids):

    if not participant_ids:
        raise ValueError("Debe haber al menos un participante")
    if total_amount < 0:
        raise ValueError("El monto total no puede ser negativo")

    total  = Decimal(str(total_amount))
    count  = len(participant_ids)
    monto  = total / count

    return {uid: monto for uid in participant_ids}


class TestDivisionGastos:

    def test_dividir_monto_entre_participantes(self):

        result = calcular_division_igual(150000, [1, 2, 3])

        assert result[1] == Decimal('50000')
        assert result[2] == Decimal('50000')
        assert result[3] == Decimal('50000')

    def test_rechazar_sin_participantes(self):

        with pytest.raises(ValueError, match="al menos un participante"):
            calcular_division_igual(150000, [])

    def test_suma_partes_igual_total(self):

        result = calcular_division_igual(100000, [1, 2, 3])
        suma   = sum(result.values())

        assert suma == Decimal('100000') / 3 * 3 

def calcular_balance(transacciones, user_id):

    pagado   = Decimal('0')
    recibido = Decimal('0')
    deudas   = Decimal('0')

    for tx in transacciones:
        amount = Decimal(str(tx['amount']))

        if tx['type'] == 'pago':
            if tx['from_user_id'] == user_id:
                pagado += amount
            elif tx['to_user_id'] == user_id:
                recibido += amount

        elif tx['type'] == 'deuda':
            if tx['from_user_id'] == user_id:
                deudas += amount

    return {
        'pagado':   pagado,
        'recibido': recibido,
        'deudas':   deudas,
        'neto':     recibido - pagado - deudas,
    }


class TestBalanceFinanciero:

    def test_balance_neto_con_pagos_en_ambas_direcciones(self):
        transacciones = [
            {'from_user_id': 1, 'to_user_id': 2, 'amount': 50000, 'type': 'pago'},
            {'from_user_id': 2, 'to_user_id': 1, 'amount': 80000, 'type': 'pago'},
        ]
        result = calcular_balance(transacciones, user_id=1)

        assert result['pagado']   == Decimal('50000')
        assert result['recibido'] == Decimal('80000')
        assert result['neto']     == Decimal('30000')

    def test_balance_neto_cero_cuando_pagado_igual_recibido(self):
       
        transacciones = [
            {'from_user_id': 1, 'to_user_id': 2, 'amount': 50000, 'type': 'pago'},
            {'from_user_id': 2, 'to_user_id': 1, 'amount': 50000, 'type': 'pago'},
        ]
        result = calcular_balance(transacciones, user_id=1)

        assert result['neto'] == Decimal('0')

    def test_deudas_reducen_el_neto(self):
        
            transacciones = [
                {'from_user_id': 2, 'to_user_id': 1, 'amount': 100000, 'type': 'pago'},
                {'from_user_id': 1, 'to_user_id': 2, 'amount': 40000,  'type': 'deuda'},
            ]
            result = calcular_balance(transacciones, user_id=1)

            assert result['recibido'] == Decimal('100000')
            assert result['deudas']   == Decimal('40000')
            assert result['neto']     == Decimal('60000')
