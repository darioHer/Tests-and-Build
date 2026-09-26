import os

RESTA_FLAG = "resta_enabled"


class FeatureDisabledError(Exception):
    """Se intenta usar una funcionalidad cuyo feature flag está apagado."""


class DivisionPorCeroError(Exception):
    """Se intenta dividir por cero."""


def configcat_flag(key: str, default: bool = False) -> bool:
    """Lee un feature flag de ConfigCat.

    Si no hay CONFIGCAT_SDK_KEY o ConfigCat falla, devuelve `default`
    (apagado), de modo que una caída del servicio nunca enciende una feature.
    """
    sdk_key = os.environ.get("CONFIGCAT_SDK_KEY")
    if not sdk_key:
        return default
    try:
        import configcatclient

        client = configcatclient.get(sdk_key)
        return bool(client.get_value(key, default))
    except Exception:
        return default


class Calculator:
    def __init__(self, flag_provider=configcat_flag):
        # Inyectable para poder probar sin red ni cuenta de ConfigCat.
        self._flag = flag_provider
        self._historial = []

    def _requiere_flag(self):
        if not self._flag(RESTA_FLAG, False):
            raise FeatureDisabledError(
                f"Esta operación está desactivada (flag '{RESTA_FLAG}')."
            )

    def _registrar(self, operacion: str, a, b, resultado):
        self._historial.append(
            {"operacion": operacion, "a": a, "b": b, "resultado": resultado}
        )

    def historial(self) -> list:
        """Copia de las operaciones realizadas en esta instancia, en orden."""
        return list(self._historial)

    def sum(self, a, b):
        resultado = a + b
        self._registrar("sum", a, b, resultado)
        return resultado

    def resta(self, a, b):
        self._requiere_flag()
        resultado = a - b
        self._registrar("resta", a, b, resultado)
        return resultado

    def multiplicar(self, a, b):
        self._requiere_flag()
        resultado = a * b
        self._registrar("multiplicar", a, b, resultado)
        return resultado

    def dividir(self, a, b):
        self._requiere_flag()
        if b == 0:
            raise DivisionPorCeroError("No se puede dividir por cero.")
        resultado = a / b
        self._registrar("dividir", a, b, resultado)
        return resultado