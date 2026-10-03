# 🚀 Calculadora Web con Trunk-Based Development & CI/CD
> Repositorio oficial para la implementación práctica de **Scrum + Trunk-Based Development (TBD)**, **Feature Flags con ConfigCat** y **Pipelines Automatizados de CI/CD**.

[![Test and Build](https://github.com/darioHer/Tests-and-Build/actions/workflows/ci.yaml/badge.svg)](https://github.com/darioHer/Tests-and-Build/actions/workflows/ci.yaml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Linter: Ruff](https://img.shields.io/badge/linter-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-green.svg)](https://pytest.org/)
[![Feature Flags: ConfigCat](https://img.shields.io/badge/feature__flags-ConfigCat-blueviolet.svg)](https://configcat.com/)

---

## 📚 Documentación de Talleres y Metodología

El repositorio contiene los artefactos completos desarrollados para la adopción de ingeniería de software moderna:

* 🛠️ [**Taller 3: CI/CD, Render y ConfigCat (`TALLER_3_CI_CD_RENDER_CONFIGCAT.md`)**](./TALLER_3_CI_CD_RENDER_CONFIGCAT.md): Guía completa de auto-deploy a Render, pruebas de calidad, auditoría de Ejemplo 5 (Tickets 1, 2 y 3) y feature toggles en producción.
* ✅ [**Definition of Done (`DOD.md`)**](./DOD.md): Criterios de calidad, pruebas obligatorias, linters, Docker, CI/CD y políticas "Stop the Line".
* 📘 [**Scrum + TBD Playbook (`SCRUM_TBD_PLAYBOOK.md`)**](./SCRUM_TBD_PLAYBOOK.md): Guía metodológica completa con diagnóstico de flujo, roles adaptados (PO, Developers, Scrum Master), ceremonias adaptadas (Daily, Review, Retro), principios, 5 Reglas de Oro, DoR, DoD y métricas DORA.
* 📋 [**Backlog y Planificación de Sprints con Entregas Incrementales (`BACKLOG_Y_PLANIFICACION_SPRINT.md`)**](./BACKLOG_Y_PLANIFICACION_SPRINT.md): Diagnóstico del Backlog con semáforo 🟢🟡🔴, técnicas de sliceado vertical aplicadas, auditoría de Ejemplo 5, plantillas de incrementos, Sprint Goal TBD y plan de integración diaria.

---

## 🛠️ Arquitectura y Tecnologías

* **Backend:** Python 3.11 + Flask (API REST) + Gunicorn WSGI.
* **Lógica de Dominio:** Clase `Calculator` desacoplada con soporte de historial y manejo de excepciones de dominio (`DivisionPorCeroError`, `NumeroNegativoError`, `FeatureDisabledError`).
* **Feature Flags:** Integración con SDK de **ConfigCat** con inyección de dependencias para testing desacoplado y seguro (*fail-closed*), con targeting por usuario para rollouts porcentuales (10% $\rightarrow$ 100%).
* **Frontend:** HTML5 semántico + CSS3 responsivo + Vanilla JavaScript asíncrono con autodetección de flags activos.
* **Calidad & Linter:** `ruff` (linter ultrarrápido) y `pytest` (suite completa de 49 pruebas unitarias y de integración).
* **CI/CD & Empaquetado:** GitHub Actions con ejecución de pruebas automáticas, verificación de Docker build en PRs y publicación de imagen Docker inmutable en **GitHub Container Registry (GHCR)**.
* **Despliegue Continuo (CD):** Auto-deploy continuo desde `main` a **Render** vía `render.yaml` con health check en `/health`.

---

## 🎛️ Feature Flags Configurados

| Feature Flag | Operaciones Afectadas | Estado / Rollout | Comportamiento si está apagado |
| :--- | :--- | :---: | :--- |
| `resta_enabled` | Resta ($a - b$) | 100% (GA) | Retorna `404 {"error": "feature_disabled"}` y oculta controles en UI. |
| `multiplicacion_enabled` | Multiplicación ($a \times b$) | 10% (Canary) / 100% (GA) | Retorna `404 {"error": "feature_disabled"}` y oculta controles en UI. |
| `division_enabled` | División ($a / b$) con control de cero | 100% (GA) | Retorna `404 {"error": "feature_disabled"}` y oculta controles en UI. |
| `potencia_enabled` | Potenciación ($a^b$) | 100% (GA) | Retorna `404 {"error": "feature_disabled"}` y oculta controles en UI. |
| `raiz_enabled` | Raíz Cuadrada ($\sqrt{a}$) | 100% (GA) | Retorna `404 {"error": "feature_disabled"}` y oculta controles en UI. |
| `comments_enabled` | Sistema de Comentarios en Blog | 0% (Ticket 1) $\rightarrow$ 10% (Ticket 2) $\rightarrow$ 100% (Ticket 3) | Retorna `404 {"error": "feature_disabled"}` y oculta formulario/comentarios. |

---

## 🚦 Endpoints de la API REST

| Método | Endpoint | Parámetros | Descripción | Código Éxito |
| :--- | :--- | :--- | :--- | :---: |
| `GET` | `/` | Ninguno | Sirve la interfaz web estática de la calculadora | `200 OK` |
| `GET` | `/blog` | Ninguno | Sirve la interfaz interactiva del Blog con comentarios TBD | `200 OK` |
| `GET` | `/health` | Ninguno | Health check para orquestadores y Render | `200 OK` |
| `GET` | `/api/sumar` | `?a=<num>&b=<num>` | Suma de dos números (siempre disponible) | `200 OK` |
| `GET` | `/api/resta` | `?a=<num>&b=<num>` | Resta ($a - b$) detrás de `resta_enabled` | `200 OK` |
| `GET` | `/api/multiplicar` | `?a=<num>&b=<num>&user_id=<id>` | Multiplicación ($a \times b$) detrás de `multiplicacion_enabled` | `200 OK` |
| `GET` | `/api/dividir` | `?a=<num>&b=<num>&user_id=<id>` | División ($a / b$) con validación $b \ne 0$ detrás de `division_enabled` | `200 OK` |
| `GET` | `/api/potencia` | `?a=<num>&b=<num>&user_id=<id>` | Potenciación ($a^b$) detrás de `potencia_enabled` | `200 OK` |
| `GET` | `/api/raiz` | `?a=<num>&user_id=<id>` | Raíz cuadrada ($\sqrt{a}$) con validación $a \ge 0$ | `200 OK` |
| `GET` | `/api/historial` | Ninguno | Retorna el historial de operaciones realizadas | `200 OK` |
| `GET` | `/api/articles` | Ninguno | Retorna los artículos del Blog | `200 OK` |
| `POST` | `/api/articles/{id}/comments` | `{"author", "content", "parent_id"}` | Guarda comentario (Ticket 1 & 3) detrás de `comments_enabled` | `201 Created` |
| `GET` | `/api/articles/{id}/comments` | `?user_id=<id>` | Retorna comentarios anidados (Ticket 2 & 3) | `200 OK` |


---

## 💻 Ejecución Local y Pruebas

### 1. Clonar e Instalar Dependencias
```bash
git clone https://github.com/darioHer/Tests-and-Build.git
cd Tests-and-Build
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r src/requirements.txt
```

### 2. Ejecutar Linter y Pruebas
```bash
# Ejecutar verificación de estilo y linters
ruff check src/

# Ejecutar la suite completa de 38 pruebas unitarias y de integración
pytest src/
```

### 3. Iniciar el Servidor de Desarrollo
```bash
python src/app.py
# Acceder a http://localhost:5000 en el navegador
```

---

## 🐳 Ejecución con Docker

```bash
# Construir la imagen localmente
docker build -t calculadora-app ./src

# Ejecutar el contenedor
docker run -p 5000:5000 calculadora-app
```
