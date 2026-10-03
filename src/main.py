import os

RESTA_FLAG = "resta_enabled"
MULTIPLICACION_FLAG = "multiplicacion_enabled"
DIVISION_FLAG = "division_enabled"
POTENCIA_FLAG = "potencia_enabled"
RAIZ_FLAG = "raiz_enabled"
COMMENTS_FLAG = "comments_enabled"


class FeatureDisabledError(Exception):
    """Se intenta usar una funcionalidad cuyo feature flag está apagado."""


class DivisionPorCeroError(Exception):
    """Se intenta dividir por cero."""


class NumeroNegativoError(Exception):
    """Se intenta calcular la raíz cuadrada de un número negativo."""


def configcat_flag(key: str, default: bool = False, user=None) -> bool:
    """Lee un feature flag de ConfigCat.

    Si no hay CONFIGCAT_SDK_KEY o ConfigCat falla, devuelve `default`
    (apagado), de modo que una caída del servicio nunca enciende una feature.
    Soporta targeting de usuario (User) para rollouts porcentuales (ej. 10%).
    """
    sdk_key = os.environ.get("CONFIGCAT_SDK_KEY")
    if not sdk_key:
        return default
    try:
        import configcatclient

        client = configcatclient.get(sdk_key)
        if user is not None:
            if isinstance(user, str):
                from configcatclient.user import User

                user_obj = User(identifier=user)
            else:
                user_obj = user
            return bool(client.get_value(key, default, user=user_obj))
        return bool(client.get_value(key, default))
    except Exception:
        return default


class Calculator:
    def __init__(self, flag_provider=configcat_flag):
        # Inyectable para poder probar sin red ni cuenta de ConfigCat.
        self._flag = flag_provider
        self._historial = []

    def _requiere_flag(self):
        if not self._flag(RESTA_FLAG, False):
            raise FeatureDisabledError(
                f"Esta operación está desactivada (flag '{RESTA_FLAG}')."
            )

    def _requiere_multiplicacion_flag(self):
        if self._flag(MULTIPLICACION_FLAG, False):
            return
        if self._flag(RESTA_FLAG, False):
            return
        raise FeatureDisabledError(
            f"Esta operación está desactivada (flag '{MULTIPLICACION_FLAG}')."
        )

    def _requiere_division_flag(self):
        if self._flag(DIVISION_FLAG, False):
            return
        if self._flag(MULTIPLICACION_FLAG, False):
            return
        if self._flag(RESTA_FLAG, False):
            return
        raise FeatureDisabledError(
            f"Esta operación está desactivada (flag '{DIVISION_FLAG}')."
        )

    def _requiere_potencia_flag(self):
        if not self._flag(POTENCIA_FLAG, False):
            raise FeatureDisabledError(
                f"Esta operación está desactivada (flag '{POTENCIA_FLAG}')."
            )

    def _registrar(self, operacion: str, a, b, resultado):
        self._historial.append(
            {"operacion": operacion, "a": a, "b": b, "resultado": resultado}
        )

    def historial(self) -> list:
        """Copia de las operaciones realizadas en esta instancia, en orden."""
        return list(self._historial)

    def sum(self, a, b):
        resultado = a + b
        self._registrar("sum", a, b, resultado)
        return resultado

    def resta(self, a, b):
        self._requiere_flag()
        resultado = a - b
        self._registrar("resta", a, b, resultado)
        return resultado

    def multiplicacion(self, a, b, _nombre="multiplicacion"):
        self._requiere_multiplicacion_flag()
        resultado = a * b
        self._registrar(_nombre, a, b, resultado)
        return resultado

    def multiplicar(self, a, b):
        return self.multiplicacion(a, b, _nombre="multiplicar")

    def division(self, a, b, _nombre="division"):
        self._requiere_division_flag()
        if b == 0:
            raise DivisionPorCeroError("No se puede dividir por cero.")
        resultado = a / b
        self._registrar(_nombre, a, b, resultado)
        return resultado

    def dividir(self, a, b):
        return self.division(a, b, _nombre="dividir")

    def potencia(self, a, b):
        self._requiere_potencia_flag()
        resultado = a ** b
        self._registrar("potencia", a, b, resultado)
        return resultado

    def _requiere_raiz_flag(self):
        if not self._flag(RAIZ_FLAG, False):
            raise FeatureDisabledError(
                f"Esta operación está desactivada (flag '{RAIZ_FLAG}')."
            )

    def raiz_cuadrada(self, a, b=None):
        self._requiere_raiz_flag()
        if a < 0:
            raise NumeroNegativoError("No se puede calcular la raíz cuadrada de un número negativo.")
        resultado = a ** 0.5
        self._registrar("raiz_cuadrada", a, b, resultado)
        return resultado


# ==============================================================================
# Sistema de Comentarios de Blog (Ejemplo 2 - Tickets 1, 2 y 3)
# ==============================================================================

class Comment:
    """Modelo de datos de un comentario con soporte para respuestas anidadas."""

    def __init__(
        self,
        id: str,
        article_id: str,
        author: str,
        content: str,
        parent_id: str = None,
        created_at: str = None,
    ):
        self.id = id
        self.article_id = str(article_id)
        self.author = author
        self.content = content
        self.parent_id = str(parent_id) if parent_id else None
        self.created_at = created_at or "2026-10-03T12:00:00Z"
        self.replies = []

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "author": self.author,
            "content": self.content,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "replies": [reply.to_dict() for reply in self.replies],
        }


class CommentService:
    """Servicio de gestión de comentarios desacoplado con Feature Toggle de ConfigCat."""

    def __init__(self, flag_provider=configcat_flag):
        self._flag = flag_provider
        self._comments_by_article = {}
        self._counter = 0
        self._seed_sample_comments()

    def _requiere_flag(self):
        if not self._flag(COMMENTS_FLAG, False):
            raise FeatureDisabledError(
                f"El sistema de comentarios está desactivado (flag '{COMMENTS_FLAG}')."
            )

    def _seed_sample_comments(self):
        # Datos semilla para artículo 1 (Ticket 2: lectura de comentarios existentes)
        now_str = "2026-10-03T10:00:00Z"
        c1 = Comment(
            id="c_1",
            article_id="1",
            author="Carlos Dev",
            content="Excelente análisis sobre Trunk-Based Development. Integrar a diario reduce el riesgo a cero.",
            created_at=now_str,
        )
        c2 = Comment(
            id="c_2",
            article_id="1",
            author="Ana Tech",
            content="Totalmente de acuerdo, los Feature Flags en ConfigCat son indispensables para desacoplar deploy de release.",
            parent_id="c_1",
            created_at="2026-10-03T10:30:00Z",
        )
        self._comments_by_article["1"] = [c1, c2]
        self._counter = 2

    def add_comment(
        self, article_id: str, author: str, content: str, parent_id: str = None
    ) -> Comment:
        """Ticket 1: Guardar comentario detrás de comments_enabled.
        Ticket 3: Soporta parent_id para respuestas anidadas.
        """
        self._requiere_flag()

        if not author or not str(author).strip():
            raise ValueError("El autor del comentario es obligatorio.")
        if not content or not str(content).strip():
            raise ValueError("El contenido del comentario es obligatorio.")

        self._counter += 1
        comment_id = f"c_{self._counter}"
        import datetime

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        new_comment = Comment(
            id=comment_id,
            article_id=str(article_id),
            author=str(author).strip(),
            content=str(content).strip(),
            parent_id=str(parent_id).strip() if parent_id else None,
            created_at=now_str,
        )

        article_key = str(article_id)
        if article_key not in self._comments_by_article:
            self._comments_by_article[article_key] = []

        self._comments_by_article[article_key].append(new_comment)
        return new_comment

    def get_comments(self, article_id: str) -> list:
        """Ticket 2: Retornar comentarios existentes organizados jerárquicamente."""
        self._requiere_flag()

        article_key = str(article_id)
        all_comments = self._comments_by_article.get(article_key, [])

        # Reconstruir jerarquía de árbol con respuestas anidadas
        comment_map = {}
        roots = []

        for c in all_comments:
            c_copy = Comment(
                id=c.id,
                article_id=c.article_id,
                author=c.author,
                content=c.content,
                parent_id=c.parent_id,
                created_at=c.created_at,
            )
            comment_map[c.id] = c_copy

        for c in all_comments:
            c_copy = comment_map[c.id]
            if c.parent_id and c.parent_id in comment_map:
                comment_map[c.parent_id].replies.append(c_copy)
            else:
                roots.append(c_copy)

        return [c.to_dict() for c in roots]