import sys
import types

import pytest

from main import (
    COMMENTS_FLAG,
    DIVISION_FLAG,
    MULTIPLICACION_FLAG,
    RESTA_FLAG,
    Calculator,
    Comment,
    CommentService,
    DivisionPorCeroError,
    FeatureDisabledError,
    NumeroNegativoError,
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


def test_potencia_con_flag_encendido():
    assert Calculator(flag_provider=flag_on).potencia(2, 3) == 8


def test_potencia_con_flag_apagado_lanza_error():
    with pytest.raises(FeatureDisabledError):
        Calculator(flag_provider=flag_off).potencia(2, 3)


def test_raiz_cuadrada_con_flag_encendido():
    assert Calculator(flag_provider=flag_on).raiz_cuadrada(9, None) == 3


def test_raiz_cuadrada_con_flag_apagado_lanza_error():
    with pytest.raises(FeatureDisabledError):
        Calculator(flag_provider=flag_off).raiz_cuadrada(9, None)


def test_raiz_cuadrada_negativo_lanza_error_especifico():
    with pytest.raises(NumeroNegativoError):
        Calculator(flag_provider=flag_on).raiz_cuadrada(-4, None)


# --- Tests de Ejemplo 5 (Tickets 1, 2 y 3) ---

def test_ticket1_multiplicacion_metodo_con_flag_encendido():
    assert Calculator(flag_provider=flag_on).multiplicacion(4, 3) == 12


def test_ticket1_multiplicacion_metodo_con_flag_apagado_lanza_error():
    with pytest.raises(FeatureDisabledError):
        Calculator(flag_provider=flag_off).multiplicacion(4, 3)


def test_ticket1_multiplicacion_consulta_flag_multiplicacion_enabled():
    pedidos = []

    def spy(key, default=False):
        pedidos.append(key)
        return True

    Calculator(flag_provider=spy).multiplicacion(2, 3)
    assert pedidos[0] == MULTIPLICACION_FLAG


def test_ticket3_division_metodo_con_flag_encendido():
    assert Calculator(flag_provider=flag_on).division(10, 2) == 5.0


def test_ticket3_division_metodo_por_cero_lanza_error():
    with pytest.raises(DivisionPorCeroError):
        Calculator(flag_provider=flag_on).division(10, 0)


def test_ticket3_division_metodo_con_flag_apagado_lanza_error():
    with pytest.raises(FeatureDisabledError):
        Calculator(flag_provider=flag_off).division(10, 2)


def test_ticket3_division_consulta_flag_division_enabled():
    pedidos = []

    def spy(key, default=False):
        pedidos.append(key)
        return True

    Calculator(flag_provider=spy).division(8, 2)
    assert pedidos[0] == DIVISION_FLAG


# ==============================================================================
# Tests Ejemplo 2 — Sistema de Comentarios en Blog (Tickets 1, 2 y 3)
# ==============================================================================

def test_ejemplo2_ticket1_guardar_comentario_con_flag_encendido():
    service = CommentService(flag_provider=flag_on)
    c = service.add_comment(article_id="10", author="Tester", content="Comentario válido")
    assert c.id.startswith("c_")
    assert c.article_id == "10"
    assert c.author == "Tester"
    assert c.content == "Comentario válido"
    assert c.parent_id is None


def test_ejemplo2_ticket1_guardar_comentario_con_flag_apagado_lanza_error():
    service = CommentService(flag_provider=flag_off)
    with pytest.raises(FeatureDisabledError):
        service.add_comment(article_id="10", author="Tester", content="No debe guardarse")


def test_ejemplo2_ticket1_guardar_comentario_valida_autor_y_contenido():
    service = CommentService(flag_provider=flag_on)
    with pytest.raises(ValueError):
        service.add_comment(article_id="10", author="", content="Texto")
    with pytest.raises(ValueError):
        service.add_comment(article_id="10", author="Autor", content="   ")


def test_ejemplo2_ticket2_obtener_comentarios_con_flag_encendido():
    service = CommentService(flag_provider=flag_on)
    comments = service.get_comments("1")
    assert len(comments) >= 1
    # Verifica que el comentario raíz tiene el contenido del seed
    assert comments[0]["author"] == "Carlos Dev"
    assert len(comments[0]["replies"]) >= 1
    assert comments[0]["replies"][0]["author"] == "Ana Tech"


def test_ejemplo2_ticket2_obtener_comentarios_con_flag_apagado_lanza_error():
    service = CommentService(flag_provider=flag_off)
    with pytest.raises(FeatureDisabledError):
        service.get_comments("1")


def test_ejemplo2_ticket3_respuesta_anidada_con_parent_id():
    service = CommentService(flag_provider=flag_on)
    parent = service.add_comment(article_id="2", author="Laura", content="Pregunta sobre CI/CD")
    reply = service.add_comment(article_id="2", author="Dario", content="Respuesta detallada", parent_id=parent.id)

    comments = service.get_comments("2")
    assert len(comments) == 1
    assert comments[0]["id"] == parent.id
    assert len(comments[0]["replies"]) == 1
    assert comments[0]["replies"][0]["id"] == reply.id
    assert comments[0]["replies"][0]["parent_id"] == parent.id


def test_ejemplo2_ticket1_comment_consulta_flag_comments_enabled():
    pedidos = []

    def spy(key, default=False):
        pedidos.append(key)
        return True

    CommentService(flag_provider=spy).add_comment("1", "Tester", "Contenido")
    assert pedidos[0] == COMMENTS_FLAG


def test_comment_model_properties():
    c = Comment(id="c_99", article_id="1", author="Ana", content="Hola")
    assert c.id == "c_99"
    assert c.author == "Ana"
    assert c.to_dict()["id"] == "c_99"

