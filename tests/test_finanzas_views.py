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