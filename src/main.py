import os

RESTA_FLAG = "resta_enabled"


class FeatureDisabledError(Exception):
    """Se intenta usar una funcionalidad cuyo feature flag está apagado."""


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

    def sum(self, a: int, b: int) -> int:
        return a + b

    def resta(self, a: int, b: int) -> int:
        if not self._flag(RESTA_FLAG, False):
            raise FeatureDisabledError(
                f"La función resta está desactivada (flag '{RESTA_FLAG}')."
            )
        return a - b
