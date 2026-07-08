import pytest


# ---------------------------------------------------------------------------
# Lógica de validación de Feedback (RF_30)
# ---------------------------------------------------------------------------

TIPOS_VALIDOS = {'opinion', 'reclamo', 'sugerencia'}
MAX_MESSAGE_LENGTH = 2000


def validar_feedback(data: dict) -> dict:
    """Simula la validación del FeedbackSerializer."""
    errores = []

    tipo    = data.get('type', '').strip().lower()
    mensaje = data.get('message', '').strip()

    if not tipo:
        errores.append("El tipo es requerido.")
    elif tipo not in TIPOS_VALIDOS:
        errores.append(f"Tipo no válido. Opciones: {', '.join(sorted(TIPOS_VALIDOS))}")

    if not mensaje:
        errores.append("El mensaje es requerido.")
    elif len(mensaje) > MAX_MESSAGE_LENGTH:
        errores.append(f"El mensaje no puede superar {MAX_MESSAGE_LENGTH} caracteres.")

    return {
        'valido':  len(errores) == 0,
        'errores': errores,
    }


class TestFeedback:

    def test_aceptar_opinion_valida(self):
        result = validar_feedback({'type': 'opinion', 'message': 'Me gusta la app'})
        assert result['valido'] is True

    def test_aceptar_reclamo(self):
        result = validar_feedback({'type': 'reclamo', 'message': 'Hay un error en el balance'})
        assert result['valido'] is True

    def test_aceptar_sugerencia(self):
        result = validar_feedback({'type': 'sugerencia', 'message': 'Agregar modo oscuro'})
        assert result['valido'] is True

    def test_rechazar_tipo_invalido(self):
        result = validar_feedback({'type': 'queja', 'message': 'No me gusta'})
        assert result['valido'] is False
        assert any('Tipo no válido' in e for e in result['errores'])

    def test_rechazar_mensaje_vacio(self):
        result = validar_feedback({'type': 'opinion', 'message': ''})
        assert result['valido'] is False
        assert any('mensaje' in e.lower() for e in result['errores'])

    def test_rechazar_tipo_vacio(self):
        result = validar_feedback({'type': '', 'message': 'Hola'})
        assert result['valido'] is False
        assert any('tipo' in e.lower() for e in result['errores'])

    def test_rechazar_mensaje_muy_largo(self):
        long_msg = 'x' * (MAX_MESSAGE_LENGTH + 1)
        result = validar_feedback({'type': 'opinion', 'message': long_msg})
        assert result['valido'] is False
        assert any('superar' in e for e in result['errores'])

    def test_ambos_campos_vacios_dos_errores(self):
        result = validar_feedback({'type': '', 'message': ''})
        assert result['valido'] is False
        assert len(result['errores']) == 2
