import sys
import types

import pytest

from main import (
    RESTA_FLAG,
    Calculator,
    DivisionPorCeroError,
    FeatureDisabledError,
    configcat_flag,
)


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


def test_multiplicar_con_flag_encendido():
    assert Calculator(flag_provider=flag_on).multiplicar(4, 3) == 12


def test_multiplicar_con_flag_apagado_lanza_error():
    with pytest.raises(FeatureDisabledError):
        Calculator(flag_provider=flag_off).multiplicar(4, 3)


def test_dividir_con_flag_encendido():
    assert Calculator(flag_provider=flag_on).dividir(10, 2) == 5


def test_dividir_con_flag_apagado_lanza_error():
    with pytest.raises(FeatureDisabledError):
        Calculator(flag_provider=flag_off).dividir(10, 2)


def test_dividir_por_cero_lanza_error_especifico():
    with pytest.raises(DivisionPorCeroError):
        Calculator(flag_provider=flag_on).dividir(10, 0)


def test_sum_no_depende_del_flag():
    # sum() siempre estuvo disponible, no debe requerir el flag.
    assert Calculator(flag_provider=flag_off).sum(2, 2) == 4


def test_historial_registra_operaciones_exitosas_en_orden():
    calc = Calculator(flag_provider=flag_on)
    calc.sum(2, 2)
    calc.resta(5, 3)
    calc.multiplicar(4, 3)
    calc.dividir(10, 2)

    assert calc.historial() == [
        {"operacion": "sum", "a": 2, "b": 2, "resultado": 4},
        {"operacion": "resta", "a": 5, "b": 3, "resultado": 2},
        {"operacion": "multiplicar", "a": 4, "b": 3, "resultado": 12},
        {"operacion": "dividir", "a": 10, "b": 2, "resultado": 5.0},
    ]


def test_historial_no_registra_operaciones_bloqueadas_por_el_flag():
    calc = Calculator(flag_provider=flag_off)
    calc.sum(1, 1)
    with pytest.raises(FeatureDisabledError):
        calc.resta(5, 3)

    assert calc.historial() == [{"operacion": "sum", "a": 1, "b": 1, "resultado": 2}]


def test_historial_no_registra_division_por_cero():
    calc = Calculator(flag_provider=flag_on)
    with pytest.raises(DivisionPorCeroError):
        calc.dividir(5, 0)

    assert calc.historial() == []


def test_historial_es_una_copia_independiente():
    calc = Calculator(flag_provider=flag_on)
    calc.sum(1, 1)
    copia = calc.historial()
    copia.append({"operacion": "falsa", "a": 0, "b": 0, "resultado": 0})

    assert calc.historial() == [{"operacion": "sum", "a": 1, "b": 1, "resultado": 2}]