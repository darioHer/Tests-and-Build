"""API mínima de la calculadora (issues #6 y #7).

GET /api/sumar?a=<num>&b=<num>          siempre disponible
GET /api/resta?a=<num>&b=<num>          detrás del flag resta_enabled
GET /api/multiplicar?a=<num>&b=<num>    detrás del flag resta_enabled
GET /api/dividir?a=<num>&b=<num>        detrás del flag resta_enabled
GET /api/potencia?a=<num>&b=<num>       detrás del flag potencia_enabled
GET /api/historial                      operaciones realizadas en este proceso

  200 {"result": <num>}                     éxito
  404 {"error": "feature_disabled"}          flag apagado (el frontend oculta
                                              el botón sin filtrar que existe)
  400 {"error": "invalid_params"}            faltan o no son numéricos a/b
  400 {"error": "division_por_cero"}         b == 0 en /api/dividir
"""
import os
from flask import Flask, jsonify, request, send_from_directory

import main
from main import (
    PAGOS_EXPRESS_FLAG,
    Calculator,
    CommentService,
    DivisionPorCeroError,
    FeatureDisabledError,
    NumeroNegativoError,
    PagosExpressService,
)


def _current_flag_provider(key, default=False):
    # Soporte para entorno local o simulador en UI (query param, header o body JSON)
    sim = None
    try:
        sim = request.args.get("simulate_flags") or request.headers.get("X-Simulate-Flags")
        if not sim and request.is_json:
            json_body = request.get_json(silent=True) or {}
            sim = json_body.get("simulate_flags")
    except Exception:
        pass

    if sim in ("all", "on", "true", "100"):
        return True
    if sim in ("10", "canary_10"):
        return key in ("resta_enabled", "multiplicacion_enabled", "comments_enabled")
    if sim in ("20", "canary", "canary_20"):
        return key in (
            "resta_enabled",
            "multiplicacion_enabled",
            "comments_enabled",
            "pagos_express_enabled",
            "pagos-express-v1",
        )
    if sim in ("off", "0", "false"):
        return False

    if os.environ.get("LOCAL_FLAGS", "").lower() in ("true", "1", "on", "all"):
        return True

    # Si no se configuró CONFIGCAT_SDK_KEY (ejecución local offline),
    # permitir funcionalidad para desarrollo local sin requerir credenciales externas
    if not os.environ.get("CONFIGCAT_SDK_KEY"):
        return True

    user_id = None
    try:
        user_id = request.args.get("user_id") or request.headers.get("X-User-ID") or request.remote_addr
    except Exception:
        pass
    try:
        return main.configcat_flag(key, default, user=user_id)
    except TypeError:
        return main.configcat_flag(key, default)


# Instancias compartidas para toda la app (calculadora, comentarios y pagos express)
calculadora = Calculator(flag_provider=_current_flag_provider)
comment_service = CommentService(flag_provider=_current_flag_provider)
pagos_service = PagosExpressService(flag_provider=_current_flag_provider)

app = Flask(__name__, static_folder="static", static_url_path="")


def _parse_number(raw, name):
    if raw is None:
        raise ValueError(f"falta el parámetro '{name}'")
    try:
        return float(raw)
    except ValueError:
        raise ValueError(f"'{name}' debe ser numérico") from None


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    """Endpoint de comprobación de salud para Render y orquestadores."""
    return jsonify(status="ok", app="calculadora-web", version="1.0.0"), 200


def _endpoint_operacion(nombre_metodo):
    try:
        a = _parse_number(request.args.get("a"), "a")
        b = _parse_number(request.args.get("b", 0), "b") if nombre_metodo == "raiz_cuadrada" and request.args.get("b") is None else _parse_number(request.args.get("b"), "b")
    except ValueError as exc:
        return jsonify(error="invalid_params", message=str(exc)), 400

    try:
        metodo = getattr(calculadora, nombre_metodo)
        resultado = metodo(a, b)
    except FeatureDisabledError:
        return jsonify(error="feature_disabled"), 404
    except DivisionPorCeroError as exc:
        return jsonify(error="division_por_cero", message=str(exc)), 400
    except NumeroNegativoError as exc:
        return jsonify(error="numero_negativo", message=str(exc)), 400

    return jsonify(result=resultado)


@app.get("/api/sumar")
def sumar():
    return _endpoint_operacion("sum")


@app.get("/api/resta")
def resta():
    return _endpoint_operacion("resta")


@app.get("/api/multiplicar")
@app.get("/api/multiplicacion")
def multiplicar():
    return _endpoint_operacion("multiplicar")


@app.get("/api/dividir")
@app.get("/api/division")
def dividir():
    return _endpoint_operacion("dividir")


@app.get("/api/potencia")
def potencia():
    return _endpoint_operacion("potencia")


@app.get("/api/historial")
def historial():
    return jsonify(historial=calculadora.historial())


@app.get("/api/raiz")
def raiz():
    return _endpoint_operacion("raiz_cuadrada")


# ==============================================================================
# Rutas del Blog y Sistema de Comentarios (Ejemplo 2)
# ==============================================================================

SAMPLE_ARTICLES = [
    {
        "id": "1",
        "title": "Trunk-Based Development & Feature Flags en Producción",
        "author": "Ingeniería de Software",
        "date": "2026-10-03",
        "summary": "Cómo pasar de ramas eternas y dolorosas a integraciones continuas diarias desplegando a producción con ConfigCat y Render.",
        "content": """Trunk-Based Development (TBD) es el estándar de oro en ingeniería de software moderna para entrega continua.
En lugar de mantener ramas de características que viven durante semanas o meses acumulando discrepancias, los desarrolladores integran ramas de vida corta (< 24 horas) directamente sobre la rama principal `main`.

El secreto para integrar código incompleto o experimental sin romper la experiencia del usuario radica en los Feature Flags (o Feature Toggles).
Con herramientas como ConfigCat, desacoplamos completamente el Despliegue (*Deploy*) del Lanzamiento (*Release*).
Esto permite realizar rollouts canary (10% -> 50% -> 100%) y activar funcionalidades al instante desde un dashboard central sin tener que re-compilar ni re-desplegar contenedores Docker.""",
    }
]


@app.get("/blog")
def blog():
    """Sirve la página web del Blog con interfaz de comentarios."""
    return send_from_directory(app.static_folder, "blog.html")


@app.get("/api/articles")
def get_articles():
    """Retorna la lista de artículos del blog."""
    return jsonify(articles=SAMPLE_ARTICLES)


@app.get("/api/articles/<article_id>")
def get_article(article_id):
    """Retorna un artículo específico por su ID."""
    article = next((a for a in SAMPLE_ARTICLES if a["id"] == str(article_id)), None)
    if not article:
        return jsonify(error="article_not_found"), 404
    return jsonify(article=article)


@app.post("/articles/<article_id>/comments")
@app.post("/api/articles/<article_id>/comments")
def post_comment(article_id):
    """Ticket 1: Guardar comentario detrás del flag comments_enabled.
    Ticket 3: Admite parent_id para respuestas anidadas.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    author = data.get("author")
    content = data.get("content")
    parent_id = data.get("parent_id")

    try:
        new_comment = comment_service.add_comment(
            article_id=article_id,
            author=author,
            content=content,
            parent_id=parent_id,
        )
        return jsonify(comment=new_comment.to_dict()), 201
    except FeatureDisabledError:
        return jsonify(error="feature_disabled", message="Comentarios desactivados."), 404
    except ValueError as exc:
        return jsonify(error="invalid_params", message=str(exc)), 400


@app.get("/articles/<article_id>/comments")
@app.get("/api/articles/<article_id>/comments")
def get_comments_endpoint(article_id):
    """Ticket 2: Retorna comentarios existentes (solo lectura) detrás del flag."""
    try:
        comments = comment_service.get_comments(article_id)
        return jsonify(comments=comments), 200
    except FeatureDisabledError:
        return jsonify(error="feature_disabled", message="Comentarios desactivados."), 404


# ==============================================================================
# Rutas de Pagos Express & Liberación Segura (Taller 6)
# ==============================================================================


@app.get("/sprint-review")
def sprint_review():
    """Página interactiva de simulación de Sprint Review y Liberación Segura."""
    return send_from_directory(app.static_folder, "sprint_review.html")


@app.post("/api/pagos-express")
def post_pago_express():
    """Taller 6: Endpoint de pago con 1 solo clic detrás del toggle pagos_express_enabled."""
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    user_id = data.get("user_id") or request.headers.get("X-User-ID") or "user_demo"
    monto = data.get("monto", 49.99)
    item_id = data.get("item_id", "prod-express-01")
    simulate_error = bool(data.get("simulate_error", False))

    try:
        tx = pagos_service.procesar_pago(
            user_id=user_id,
            monto=monto,
            item_id=item_id,
            simulate_error=simulate_error,
        )
        return jsonify(status="approved", transaction=tx), 201
    except FeatureDisabledError:
        return (
            jsonify(
                error="feature_disabled",
                message=f"La función de Pagos Express está inactiva (flag '{PAGOS_EXPRESS_FLAG}').",
            ),
            404,
        )
    except ValueError as exc:
        return jsonify(error="invalid_params", message=str(exc)), 400
    except RuntimeError as exc:
        return jsonify(error="gateway_error", message=str(exc)), 502


@app.get("/api/pagos-express/status")
def get_pagos_status():
    """Taller 6: Telemetría de liberación segura, observabilidad y auditoría de toggles."""
    metricas = pagos_service.obtener_metricas()
    toggles_obsoletos = pagos_service.auditar_toggles_obsoletos()
    return jsonify(metrics=metricas, obsolete_toggles=toggles_obsoletos), 200


@app.post("/api/pagos-express/toggle")
def post_pagos_toggle():
    """Control administrativo del toggle para pruebas y simulación en vivo."""
    data = request.get_json(silent=True) or {}
    if "circuit_breaker" in data:
        pagos_service.set_circuit_breaker(bool(data["circuit_breaker"]))
    if "rollout_pct" in data:
        pagos_service.set_rollout_pct(int(data["rollout_pct"]))
    return jsonify(status="updated", metrics=pagos_service.obtener_metricas()), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)