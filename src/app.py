"""API mínima de la calculadora (issues #6 y #7).

GET /api/sumar?a=<num>&b=<num>          siempre disponible
GET /api/resta?a=<num>&b=<num>          detrás del flag resta_enabled
GET /api/multiplicar?a=<num>&b=<num>    detrás del flag resta_enabled
GET /api/dividir?a=<num>&b=<num>        detrás del flag resta_enabled
GET /api/historial                      operaciones realizadas en este proceso

  200 {"result": <num>}                     éxito
  404 {"error": "feature_disabled"}          flag apagado (el frontend oculta
                                              el botón sin filtrar que existe)
  400 {"error": "invalid_params"}            faltan o no son numéricos a/b
  400 {"error": "division_por_cero"}         b == 0 en /api/dividir
"""
from flask import Flask, jsonify, request, send_from_directory

import main
from main import Calculator, DivisionPorCeroError, FeatureDisabledError

# Una sola instancia para toda la app: así el historial acumula operaciones
# entre requests dentro del mismo proceso (se pierde si el proceso reinicia).
calculadora = Calculator(flag_provider=lambda key, default=False: main.configcat_flag(key, default))

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


def _endpoint_operacion(nombre_metodo):
    try:
        a = _parse_number(request.args.get("a"), "a")
        b = _parse_number(request.args.get("b"), "b")
    except ValueError as exc:
        return jsonify(error="invalid_params", message=str(exc)), 400

    try:
        metodo = getattr(calculadora, nombre_metodo)
        resultado = metodo(a, b)
    except FeatureDisabledError:
        return jsonify(error="feature_disabled"), 404
    except DivisionPorCeroError as exc:
        return jsonify(error="division_por_cero", message=str(exc)), 400

    return jsonify(result=resultado)


@app.get("/api/sumar")
def sumar():
    return _endpoint_operacion("sum")


@app.get("/api/resta")
def resta():
    return _endpoint_operacion("resta")


@app.get("/api/multiplicar")
def multiplicar():
    return _endpoint_operacion("multiplicar")


@app.get("/api/dividir")
def dividir():
    return _endpoint_operacion("dividir")


@app.get("/api/historial")
def historial():
    return jsonify(historial=calculadora.historial())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)