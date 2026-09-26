"""API mínima para exponer resta() en el frontend (issue #6).

GET /api/resta?a=<num>&b=<num>
  200 {"result": <num>}                     si el flag resta_enabled está encendido
  404 {"error": "feature_disabled", ...}     si está apagado (así el frontend
                                              puede ocultar el botón sin filtrar
                                              que la función existe pero está bloqueada)
  400 {"error": "invalid_params"}            si faltan o no son numéricos a/b
"""
from flask import Flask, jsonify, request, send_from_directory

import main
from main import Calculator, FeatureDisabledError

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


@app.get("/api/resta")
def resta():
    try:
        a = _parse_number(request.args.get("a"), "a")
        b = _parse_number(request.args.get("b"), "b")
    except ValueError as exc:
        return jsonify(error="invalid_params", message=str(exc)), 400

    try:
        # Se pasa explícito (en vez de usar el default del parámetro) para
        # que siempre lea la versión actual de main.configcat_flag: así los
        # tests pueden sustituirla con monkeypatch sin reiniciar el proceso.
        resultado = Calculator(flag_provider=main.configcat_flag).resta(a, b)
    except FeatureDisabledError:
        return jsonify(error="feature_disabled"), 404

    return jsonify(result=resultado)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
