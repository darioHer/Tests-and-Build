import sys
import types

import pytest

from main import RESTA_FLAG, Calculator, FeatureDisabledError, configcat_flag


def flag_on(key, default=False):
    return True


def flag_off(key, default=False):
    return False


def test_sums_2_numbers():
    assert Calculator().sum(2, 2) == 4


def test_resta_2_numbers_con_flag_encendido():
    assert Calculator(flag_provider=flag_on).resta(5, 3) == 2


def test_resta_con_flag_apagado_lanza_error():
    with pytest.raises(FeatureDisabledError):
        Calculator(flag_provider=flag_off).resta(5, 3)


def test_resta_consulta_el_flag_correcto():
    pedidos = []

    def spy(key, default=False):
        pedidos.append(key)
        return True

    Calculator(flag_provider=spy).resta(1, 1)
    assert pedidos == [RESTA_FLAG]


def test_sin_sdk_key_el_flag_esta_apagado(monkeypatch):
    monkeypatch.delenv("CONFIGCAT_SDK_KEY", raising=False)
    assert configcat_flag(RESTA_FLAG) is False
    with pytest.raises(FeatureDisabledError):
        Calculator().resta(5, 3)


def test_configcat_encendido(monkeypatch):
    class FakeClient:
        def get_value(self, key, default):
            return True

    fake = types.SimpleNamespace(get=lambda sdk_key: FakeClient())
    monkeypatch.setenv("CONFIGCAT_SDK_KEY", "fake-key")
    monkeypatch.setitem(sys.modules, "configcatclient", fake)
    assert configcat_flag(RESTA_FLAG) is True


def test_si_configcat_falla_el_flag_queda_apagado(monkeypatch):
    def boom(sdk_key):
        raise RuntimeError("sin red")

    monkeypatch.setenv("CONFIGCAT_SDK_KEY", "fake-key")
    monkeypatch.setitem(sys.modules, "configcatclient", types.SimpleNamespace(get=boom))
    assert configcat_flag(RESTA_FLAG) is False
