import os

RESTA_FLAG = "resta_enabled"
MULTIPLICACION_FLAG = "multiplicacion_enabled"
DIVISION_FLAG = "division_enabled"
POTENCIA_FLAG = "potencia_enabled"
RAIZ_FLAG = "raiz_enabled"


class FeatureDisabledError(Exception):
    """Se intenta usar una funcionalidad cuyo feature flag está apagado."""


class DivisionPorCeroError(Exception):
    """Se intenta dividir por cero."""


class NumeroNegativoError(Exception):
    """Se intenta calcular la raíz cuadrada de un número negativo."""


def configcat_flag(key: str, default: bool = False, user=None) -> bool:
    """Lee un feature flag de ConfigCat.

    Si no hay CONFIGCAT_SDK_KEY o ConfigCat falla, devuelve `default`
    (apagado), de modo que una caída del servicio nunca enciende una feature.
    Soporta targeting de usuario (User) para rollouts porcentuales (ej. 10%).
    """
    sdk_key = os.environ.get("CONFIGCAT_SDK_KEY")
    if not sdk_key:
        return default
    try:
        import configcatclient

        client = configcatclient.get(sdk_key)
        if user is not None:
            if isinstance(user, str):
                from configcatclient.user import User

                user_obj = User(identifier=user)
            else:
                user_obj = user
            return bool(client.get_value(key, default, user=user_obj))
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

    def _requiere_multiplicacion_flag(self):
        if self._flag(MULTIPLICACION_FLAG, False):
            return
        if self._flag(RESTA_FLAG, False):
            return
        raise FeatureDisabledError(
            f"Esta operación está desactivada (flag '{MULTIPLICACION_FLAG}')."
        )

    def _requiere_division_flag(self):
        if self._flag(DIVISION_FLAG, False):
            return
        if self._flag(MULTIPLICACION_FLAG, False):
            return
        if self._flag(RESTA_FLAG, False):
            return
        raise FeatureDisabledError(
            f"Esta operación está desactivada (flag '{DIVISION_FLAG}')."
        )

    def _requiere_potencia_flag(self):
        if not self._flag(POTENCIA_FLAG, False):
            raise FeatureDisabledError(
                f"Esta operación está desactivada (flag '{POTENCIA_FLAG}')."
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

    def multiplicacion(self, a, b, _nombre="multiplicacion"):
        self._requiere_multiplicacion_flag()
        resultado = a * b
        self._registrar(_nombre, a, b, resultado)
        return resultado

    def multiplicar(self, a, b):
        return self.multiplicacion(a, b, _nombre="multiplicar")

    def division(self, a, b, _nombre="division"):
        self._requiere_division_flag()
        if b == 0:
            raise DivisionPorCeroError("No se puede dividir por cero.")
        resultado = a / b
        self._registrar(_nombre, a, b, resultado)
        return resultado

    def dividir(self, a, b):
        return self.division(a, b, _nombre="dividir")

    def potencia(self, a, b):
        self._requiere_potencia_flag()
        resultado = a ** b
        self._registrar("potencia", a, b, resultado)
        return resultado

    def _requiere_raiz_flag(self):
        if not self._flag(RAIZ_FLAG, False):
            raise FeatureDisabledError(
                f"Esta operación está desactivada (flag '{RAIZ_FLAG}')."
            )

    def raiz_cuadrada(self, a, b=None):
        self._requiere_raiz_flag()
        if a < 0:
            raise NumeroNegativoError("No se puede calcular la raíz cuadrada de un número negativo.")
        resultado = a ** 0.5
        self._registrar("raiz_cuadrada", a, b, resultado)
        return resultado