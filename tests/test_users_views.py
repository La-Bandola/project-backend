import pytest


BANCOS_PERMITIDOS = ['nequi', 'daviplata', 'bancolombia', 'otro']


def validar_cuenta_bancaria(data: dict) -> dict:
    errores = []

    bank   = data.get('bank', '').strip().lower()
    number = data.get('number', '').strip()

    if not bank:
        errores.append("El banco es requerido")
    elif bank not in BANCOS_PERMITIDOS:
        errores.append(f"Banco no permitido. Opciones: {', '.join(BANCOS_PERMITIDOS)}")

    if not number:
        errores.append("El número o llave de cuenta es requerido")
    elif len(number) < 5:
        errores.append("El número de cuenta debe tener al menos 5 caracteres")

    return {
        'valido':  len(errores) == 0,
        'errores': errores,
    }


class TestCuentasBancarias:

    def test_aceptar_cuenta_con_datos_validos(self):

        data = {
            'bank':       'nequi',
            'number':     '3001234567',
            'is_primary': True,
        }
        result = validar_cuenta_bancaria(data)

        assert result['valido']       is True
        assert len(result['errores']) == 0

    def test_rechazar_banco_no_permitido(self):

        data = {
            'bank':   'bbva',
            'number': '3001234567',
        }
        result = validar_cuenta_bancaria(data)

        assert result['valido'] is False
        assert any('no permitido' in e for e in result['errores'])

    def test_rechazar_numero_vacio(self):

        data = {
            'bank':   'nequi',
            'number': '',
        }
        result = validar_cuenta_bancaria(data)

        assert result['valido'] is False
        assert any('número' in e.lower() or 'llave' in e.lower() for e in result['errores'])