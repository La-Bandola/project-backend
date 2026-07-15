import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# Tests de cálculo de montos (RF_26)
# ---------------------------------------------------------------------------

def calcular_montos_igual(total, n_participantes):
    """Simula la lógica de split_type='equal' del EventoSerializer."""
    if n_participantes <= 0:
        raise ValueError("Debe haber al menos un participante.")
    return [Decimal(str(total)) / n_participantes] * n_participantes


def calcular_montos_custom(custom_amounts: dict):
    """Simula la lógica de split_type='custom' del EventoSerializer."""
    return {uid: Decimal(str(monto)) for uid, monto in custom_amounts.items()}


class TestCalculoEventos:

    def test_split_equal_divide_correctamente(self):
        montos = calcular_montos_igual(90, 3)
        assert all(m == Decimal('30') for m in montos)

    def test_split_equal_redondeo_decimal(self):
        montos = calcular_montos_igual(10, 3)
        suma = sum(montos)
        # La suma puede diferir por decimales, pero debe estar cerca del total
        assert abs(suma - Decimal('10')) < Decimal('0.01')

    def test_split_equal_rechaza_cero_participantes(self):
        with pytest.raises(ValueError):
            calcular_montos_igual(100, 0)

    def test_split_custom_asigna_montos_correctos(self):
        custom = {1: '50.00', 2: '30.00', 3: '20.00'}
        result = calcular_montos_custom(custom)
        assert result[1] == Decimal('50.00')
        assert result[2] == Decimal('30.00')
        assert result[3] == Decimal('20.00')


# ---------------------------------------------------------------------------
# Tests de estado de evento (RF_15, RF_16)
# ---------------------------------------------------------------------------

def determinar_estado_evento(pay_immediately: bool) -> str:
    """Simula la lógica de asignación de estado al crear un evento."""
    return 'active' if pay_immediately else 'waiting'


class TestEstadoEvento:

    def test_pago_inmediato_estado_active(self):
        assert determinar_estado_evento(True) == 'active'

    def test_pago_posterior_estado_waiting(self):
        assert determinar_estado_evento(False) == 'waiting'


# ---------------------------------------------------------------------------
# Tests de validación de soporte de pago (RF_32)
# ---------------------------------------------------------------------------

EXTENSIONES_VALIDAS = {'.jpg', '.jpeg', '.png', '.pdf'}


def validar_soporte_pago(filename: str) -> dict:
    import os
    ext = os.path.splitext(filename)[1].lower()
    if not filename:
        return {'valido': False, 'error': 'El archivo es requerido.'}
    if ext not in EXTENSIONES_VALIDAS:
        return {'valido': False, 'error': f'Extensión no permitida: {ext}'}
    return {'valido': True, 'error': None}


class TestSoportePago:

    def test_aceptar_jpg(self):
        assert validar_soporte_pago('recibo.jpg')['valido'] is True

    def test_aceptar_pdf(self):
        assert validar_soporte_pago('comprobante.pdf')['valido'] is True

    def test_rechazar_extension_invalida(self):
        result = validar_soporte_pago('virus.exe')
        assert result['valido'] is False
        assert 'Extensión no permitida' in result['error']

    def test_rechazar_archivo_vacio(self):
        result = validar_soporte_pago('')
        assert result['valido'] is False
