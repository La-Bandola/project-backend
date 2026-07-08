import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# Lógica de negocio de Ahorros (RF_20)
# ---------------------------------------------------------------------------

def calcular_progreso(goal_amount, current_amount) -> float:
    """Simula EspacioAhorro.progress_percentage."""
    if goal_amount <= 0:
        return 0
    return round((current_amount / goal_amount) * 100, 2)


def acumular_aporte(current_amount, new_aporte) -> Decimal:
    """Simula la actualización de current_amount en AporteAhorroCreateView."""
    return Decimal(str(current_amount)) + Decimal(str(new_aporte))


class TestEspacioAhorro:

    def test_progreso_al_inicio_es_cero(self):
        assert calcular_progreso(1000, 0) == 0.0

    def test_progreso_al_50_porciento(self):
        assert calcular_progreso(1000, 500) == 50.0

    def test_progreso_completo_100_porciento(self):
        assert calcular_progreso(500, 500) == 100.0

    def test_progreso_supera_meta(self):
        # Permite aportes que superan la meta
        assert calcular_progreso(100, 150) == 150.0

    def test_meta_cero_devuelve_cero(self):
        assert calcular_progreso(0, 100) == 0

    def test_aporte_acumula_correctamente(self):
        nuevo = acumular_aporte(current_amount='200.00', new_aporte='50.50')
        assert nuevo == Decimal('250.50')

    def test_aporte_desde_cero(self):
        nuevo = acumular_aporte(0, 75)
        assert nuevo == Decimal('75')


class TestValidacionAporte:

    def validar_aporte(self, amount) -> dict:
        try:
            valor = Decimal(str(amount))
            if valor <= 0:
                return {'valido': False, 'error': 'El monto debe ser mayor a 0.'}
            return {'valido': True, 'error': None}
        except Exception:
            return {'valido': False, 'error': 'Monto inválido.'}

    def test_aceptar_monto_positivo(self):
        assert self.validar_aporte('100.00')['valido'] is True

    def test_rechazar_monto_cero(self):
        result = self.validar_aporte(0)
        assert result['valido'] is False

    def test_rechazar_monto_negativo(self):
        result = self.validar_aporte(-50)
        assert result['valido'] is False

    def test_rechazar_monto_texto(self):
        result = self.validar_aporte('abc')
        assert result['valido'] is False
