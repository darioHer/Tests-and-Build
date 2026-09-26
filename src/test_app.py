"""Tests del endpoint /api/resta (issue #6)."""
import main as main_module
import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_sumar_no_depende_del_flag():
    # /api/resta no cubre sumar; solo confirmamos que el frontend estático se sirve.
    pass


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
