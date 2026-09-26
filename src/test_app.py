"""Tests de los endpoints /api/* (issues #6 y #7)."""
import app as app_module
import main as main_module
import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    # La calculadora es compartida entre requests (para acumular historial),
    # así que se reinicia en cada test para que no se pisen entre sí.
    app_module.calculadora = main_module.Calculator(
        flag_provider=lambda key, default=False: main_module.configcat_flag(key, default)
    )
    return app.test_client()


def test_resta_con_flag_encendido(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/resta?a=5&b=3")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 2}


def test_resta_con_flag_apagado(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    resp = client.get("/api/resta?a=5&b=3")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "feature_disabled"


def test_resta_parametros_invalidos(client):
    resp = client.get("/api/resta?a=5")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "invalid_params"

    resp = client.get("/api/resta?a=x&b=1")
    assert resp.status_code == 400


def test_index_sirve_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Calculadora" in resp.data


def test_sumar_no_depende_del_flag(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    resp = client.get("/api/sumar?a=2&b=2")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 4}


def test_multiplicar_con_flag_encendido(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/multiplicar?a=4&b=3")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 12}


def test_multiplicar_con_flag_apagado(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    resp = client.get("/api/multiplicar?a=4&b=3")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "feature_disabled"


def test_dividir_con_flag_encendido(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/dividir?a=10&b=2")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 5}


def test_dividir_por_cero(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/dividir?a=10&b=0")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "division_por_cero"


def test_historial_acumula_entre_requests(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    client.get("/api/resta?a=5&b=3")
    client.get("/api/multiplicar?a=2&b=2")

    resp = client.get("/api/historial")
    assert resp.status_code == 200
    operaciones = [item["operacion"] for item in resp.get_json()["historial"]]
    assert operaciones == ["resta", "multiplicar"]


def test_historial_vacio_no_registra_bloqueadas(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    client.get("/api/resta?a=5&b=3")  # bloqueada, no debe registrarse

    resp = client.get("/api/historial")
    assert resp.get_json()["historial"] == []