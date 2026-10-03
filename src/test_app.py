"""Tests de los endpoints /api/* (issues #6 y #7)."""
import app as app_module
import main as main_module
import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    # La calculadora y el servicio de comentarios se reinician en cada test
    app_module.calculadora = main_module.Calculator(
        flag_provider=lambda key, default=False: main_module.configcat_flag(key, default)
    )
    app_module.comment_service = main_module.CommentService(
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


def test_potencia_con_flag_encendido(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/potencia?a=2&b=3")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 8}


def test_potencia_con_flag_apagado(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    resp = client.get("/api/potencia?a=2&b=3")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "feature_disabled"


def test_raiz_con_flag_encendido(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/raiz?a=9")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 3}


def test_raiz_con_flag_apagado(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    resp = client.get("/api/raiz?a=9")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "feature_disabled"


def test_raiz_numero_negativo(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/raiz?a=-9")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "numero_negativo"


def test_health_check_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
    assert resp.get_json()["app"] == "calculadora-web"


def test_multiplicacion_endpoint_alias(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/multiplicacion?a=6&b=7")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 42}


def test_division_endpoint_alias(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/division?a=20&b=4")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 5}


def test_division_endpoint_alias_por_cero(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/division?a=20&b=0")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "division_por_cero"


# ==============================================================================
# Tests de Endpoints del Sistema de Comentarios (Ejemplo 2)
# ==============================================================================

def test_post_comment_endpoint_con_flag_encendido(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    payload = {"author": "Tester", "content": "Gran artículo sobre CI/CD"}
    resp = client.post("/api/articles/1/comments", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "comment" in data
    assert data["comment"]["author"] == "Tester"
    assert data["comment"]["article_id"] == "1"


def test_post_comment_endpoint_con_flag_apagado(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    payload = {"author": "Tester", "content": "Gran artículo"}
    resp = client.post("/api/articles/1/comments", json=payload)
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "feature_disabled"


def test_post_comment_endpoint_datos_invalidos(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.post("/api/articles/1/comments", json={"author": "", "content": "Texto"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "invalid_params"


def test_get_comments_endpoint_con_flag_encendido(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp = client.get("/api/articles/1/comments")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "comments" in data
    assert len(data["comments"]) >= 1


def test_get_comments_endpoint_con_flag_apagado(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: False)
    resp = client.get("/api/articles/1/comments")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "feature_disabled"


def test_get_articles_endpoint(client):
    resp = client.get("/api/articles")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "articles" in data
    assert len(data["articles"]) >= 1
    assert data["articles"][0]["id"] == "1"


def test_post_nested_reply_endpoint(client, monkeypatch):
    monkeypatch.setattr(main_module, "configcat_flag", lambda key, default=False: True)
    resp_parent = client.post("/api/articles/1/comments", json={"author": "Padre", "content": "Comentario padre"})
    parent_id = resp_parent.get_json()["comment"]["id"]

    resp_reply = client.post("/api/articles/1/comments", json={
        "author": "Hijo",
        "content": "Respuesta anidada",
        "parent_id": parent_id
    })
    assert resp_reply.status_code == 201
    assert resp_reply.get_json()["comment"]["parent_id"] == parent_id


def test_blog_route_serves_html(client):
    resp = client.get("/blog")
    assert resp.status_code == 200
    assert b"Blog TBD" in resp.data
    assert b"comments_enabled" in resp.data


def test_post_comment_con_simulacion_header_y_query(client):
    # Test using live provider in app_module
    app_module.comment_service = main_module.CommentService(
        flag_provider=app_module._current_flag_provider
    )
    # 1. Simulación apagada (0%)
    resp_off = client.post(
        "/api/articles/1/comments?simulate_flags=0",
        json={"author": "Tester", "content": "Bloqueado"}
    )
    assert resp_off.status_code == 404

    # 2. Simulación encendida (100% / all)
    resp_on = client.post(
        "/api/articles/1/comments?simulate_flags=all",
        json={"author": "Tester", "content": "Permitido"}
    )
    assert resp_on.status_code == 201

    # 3. Simulación vía header
    resp_header = client.post(
        "/api/articles/1/comments",
        headers={"X-Simulate-Flags": "all"},
        json={"author": "Tester2", "content": "Permitido por Header"}
    )
    assert resp_header.status_code == 201

    # 4. Lectura en cohorte del 10% (Canary)
    resp_canary = client.get(
        "/api/articles/1/comments?simulate_flags=10"
    )
    assert resp_canary.status_code == 200
    assert len(resp_canary.get_json()["comments"]) >= 1

