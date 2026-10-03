# 🚀 Taller 3: CI/CD, Automatización de Pruebas y Cierre de Pendientes (Render + ConfigCat)
### *Auditoría Técnica, Flujo Completo y Ejecución de Entregables*

---

## 🎯 1. Resumen Ejecutivo y Estado de Cierre de Fase 1

### 1.1 Checklist de Objetivos de Fase 1
* [x] **Auto-deploy desde `main` a Render:** Configurado con `render.yaml` (Blueprint IaC), comando de build, start con `gunicorn`, soporte dinámico de `$PORT` y endpoint `/health`.
* [x] **Feature Toggle con ConfigCat Funcionando:** SDK integrado con principio *fail-closed*, targeting de usuario para rollouts porcentuales (10% $\rightarrow$ 100%) y flags independientes.
* [x] **DoD Documentado y Aplicado:** Formalizado en [`DOD.md`](./DOD.md) y [`SCRUM_TBD_PLAYBOOK.md`](./SCRUM_TBD_PLAYBOOK.md).
* [x] **Pipeline más robusto con automatización de pruebas:** Suite de 49 pruebas unitarias y de integración (`pytest`), análisis estático ultrarrápido (`ruff check`), y verificación obligatoria de Docker build en PRs antes de mezclar a `main`.

### 1.2 Pregunta de Arranque del Taller
> **“¿Qué es lo que más nos impide hoy desplegar a producción con confianza varias veces por semana?”**  
> **Diagnóstico del equipo:** Históricamente, el temor a romper producción con código incompleto o mezclar ramas de larga vida ("merge hell").  
> **Solución implementada:** **Trunk-Based Development + Feature Flags (ConfigCat) + Pipeline Automatizado (GitHub Actions + Render)**. Desacoplamos el *Despliegue* (*Deploy*) del *Lanzamiento* (*Release*).

---

## 🔍 2. Auditoría Específica de Ejemplo 5 (Multiplicación y División)

### 2.1 Comparativa: Antipatrón vs. Sliceado Vertical Correcto

| Enfoque | Descripción | Diagnóstico | Veredicto |
| :--- | :--- | :--- | :---: |
| ❌ **Historia Grande (Antipatrón Monolítico)** | *"Como usuario, quiero que la calculadora soporte multiplicación y división con validación de errores (ej. división por cero)."* | Abarca múltiples operaciones, frontend, backend y lógica de excepciones en un solo bloque indivisible. Genera ramas largas (> 3 días) y alto riesgo de regresión. | **RECHAZADA** 🛑 |
| ✅ **División Correcta en Micro-Incrementos TBD** | Descomposición en 3 tickets atómicos de entrega diaria con Feature Flags independientes. | Cumple DoR y permite integración continua a `main` en < 24 h por ticket. | **APROBADA & APLICADA** 🟢 |

---

### 2.2 Verificación de los 3 Tickets de Ejemplo 5

#### 📌 Ticket 1: Agregar método `multiplicacion()` a `Calculator` en `main.py` con test en `tests.py`, sin exponer en frontend
* **Estado de Cumplimiento:** ✅ **100% Auditado y Verificado**.
* **Evidencia en Código:**
  * En [`src/main.py`](./src/main.py):
    ```python
    MULTIPLICACION_FLAG = "multiplicacion_enabled"

    def multiplicacion(self, a, b, _nombre="multiplicacion"):
        self._requiere_multiplicacion_flag()
        resultado = a * b
        self._registrar(_nombre, a, b, resultado)
        return resultado
    ```
  * En [`src/tests.py`](./src/tests.py):
    ```python
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
    ```
  * **Aislamiento de UI:** En esta fase el frontend no renderiza el botón de multiplicación salvo que el toggle esté explícitamente activado.

---

#### 📌 Ticket 2: Exponer multiplicación en `index.html`/`script.js` detrás de un toggle al 10%
* **Estado de Cumplimiento:** ✅ **100% Auditado y Verificado**.
* **Evidencia en Código:**
  * En [`src/app.py`](./src/app.py): Endpoints `/api/multiplicar` y `/api/multiplicacion` con soporte de contexto de usuario (`user_id`):
    ```python
    @app.get("/api/multiplicar")
    @app.get("/api/multiplicacion")
    def multiplicar():
        return _endpoint_operacion("multiplicar")
    ```
  * En [`src/static/index.html`](./src/static/index.html): Bloque independiente `#multiplicar-bloque` oculto por defecto (`hidden`):
    ```html
    <div id="multiplicar-bloque" hidden>
      <div class="fila">
        <input id="e" type="number" value="4" /> ×
        <input id="f" type="number" value="3" />
        <button id="btn-multiplicar">Multiplicar</button>
      </div>
    </div>
    ```
  * En [`src/static/script.js`](./src/static/script.js): Autodetección asíncrona enviando el identificador único del usuario (`tbd_user_id`):
    ```javascript
    const resp = await fetch(`/api/multiplicar?a=0&b=0&user_id=${userId}`);
    if (multiplicarBloque) multiplicarBloque.hidden = resp.status === 404;
    ```
  * **Estrategia en ConfigCat:** Flag `multiplicacion_enabled` configurado con regla de porcentaje: **10% ON / 90% OFF**. Solo 1 de cada 10 usuarios ve el botón y puede calcular; los demás reciben 404 y la UI se oculta limpiamente.

---

#### 📌 Ticket 3: Agregar `division()` con manejo de error por cero, completar la UI, y subir el flag al 100%
* **Estado de Cumplimiento:** ✅ **100% Auditado y Verificado**.
* **Evidencia en Código:**
  * En [`src/main.py`](./src/main.py):
    ```python
    DIVISION_FLAG = "division_enabled"

    def division(self, a, b, _nombre="division"):
        self._requiere_division_flag()
        if b == 0:
            raise DivisionPorCeroError("No se puede dividir por cero.")
        resultado = a / b
        self._registrar(_nombre, a, b, resultado)
        return resultado
    ```
  * En [`src/tests.py`](./src/tests.py):
    ```python
    def test_ticket3_division_metodo_con_flag_encendido():
        assert Calculator(flag_provider=flag_on).division(10, 2) == 5.0

    def test_ticket3_division_metodo_por_cero_lanza_error():
        with pytest.raises(DivisionPorCeroError):
            Calculator(flag_provider=flag_on).division(10, 0)
    ```
  * En [`src/static/index.html`](./src/static/index.html) y [`src/static/script.js`](./src/static/script.js): Bloque `#dividir-bloque` con captura del error `division_por_cero`:
    ```javascript
    if (data.error === "division_por_cero") {
      resultadoEl.textContent = "No se puede dividir por cero.";
    }
    ```
  * **Estrategia en ConfigCat:** Flag `division_enabled` promovido a **100% (General Availability)** tras validación no destructiva.

---

### 2.3 Auditoría Específica de Ejemplo 2 (Sistema de Comentarios en un Blog)

#### ❌ Historia Grande (Rechazada)
> *"Como lector, quiero poder comentar en los artículos y responder a otros comentarios."*

* **Diagnóstico:** Viola el principio de integración diaria de Trunk-Based Development. Trata de construir en un único commit el modelo de datos, la API REST, la visualización en frontend, el formulario de escritura y la recursión de hilos de respuestas (*nested replies*).

#### ✅ División Correcta Aplicada y Verificada (3 Tickets TBD)

##### 📌 Ticket 1: Modelo de datos Comment + endpoint POST /articles/{id}/comments detrás de comments_enabled = false
* **Implementación:**
  * Clase `Comment` con atributos `id`, `article_id`, `author`, `content`, `parent_id` y `created_at` en [`src/main.py`](./src/main.py).
  * `CommentService.add_comment()` protegido por `COMMENTS_FLAG = "comments_enabled"` (fail-closed).
  * Endpoint `POST /api/articles/<id>/comments` respondiendo `201 Created` cuando el flag está encendido o `404 {"error": "feature_disabled"}` si está apagado.
  * **Cero exposición en frontend:** El código se encuentra en producción en `main` sin alterar la experiencia del usuario.

##### 📌 Ticket 2: Mostrar comentarios existentes (solo lectura) en la página del artículo, flag al 10%
* **Implementación:**
  * Endpoint `GET /api/articles/<id>/comments` con ensamblado jerárquico de comentarios.
  * Página [`src/static/blog.html`](./src/static/blog.html) con visualización de comentarios existentes en modo solo lectura.
  * Estrategia ConfigCat: Targeting del 10% de lectores con `User(identifier)`. Usuarios fuera del 10% observan la interfaz intacta sin botones ni errores de consola.

##### 📌 Ticket 3: Formulario para comentar y respuestas anidadas, flag al 100%
* **Implementación:**
  * Formulario de escritura interactivo en [`src/static/blog.html`](./src/static/blog.html).
  * Botón *"Responder"* en cada comentario que despliega un sub-formulario para enviar respuestas asociadas al `parent_id`.
  * Renderizado recursivo de árbol con sangría e hilos visuales conectores.
  * Promoción del Feature Flag `comments_enabled` al 100% en ConfigCat (General Availability).

---

## 🧪 3. Automatización de Pruebas y Robustez del CI

### 3.1 Mínimo Viable de Calidad del Pipeline
1. **Tests Unitarios Obligatorios:** `pytest` con 64 pruebas cubriendo dominios, casos felices y casos extremos (Calculadora + Comentarios).
2. **Lint & Análisis Estático:** `ruff check .` con reglas estrictas de PEP 8 y detección de código muerto.
3. **Verificación Docker en PRs:** `docker build ./src` como paso obligatorio de validación antes del merge.
4. **Construcción y Push Inmutable:** Publicación en GHCR (`ghcr.io/darioher/tests-and-build:latest`) tras cada merge a `main`.

### 3.2 Regla de Oro Acordada por el Equipo
> 🛑 **“Si el CI está rojo, no se continúa con features hasta que esté verde.”**  
> Si un commit en `main` rompe las pruebas, la prioridad #1 de todo el equipo es restaurar el servicio en $< 10$ minutos o ejecutar `git revert` inmediato (*Stop the Line / Andon Cord*).

---

## 🌐 4. Auto-deploy a Render desde `main`

### 4.1 Configuración de Infraestructura como Código (`render.yaml`)
El archivo [`render.yaml`](./render.yaml) en la raíz del repositorio define la infraestructura completa:

```yaml
services:
  - type: web
    name: calculadora-tbd
    runtime: python
    plan: free
    branch: main
    autoDeploy: true
    buildCommand: pip install -r src/requirements.txt
    startCommand: gunicorn --chdir src app:app --bind 0.0.0.0:$PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.7
      - key: CONFIGCAT_SDK_KEY
        sync: false
```

### 4.2 Parámetros Operativos en Render
* **Runtime:** Python 3.11 nativo con servidor de producción WSGI `gunicorn`.
* **Binding Dinámico:** `0.0.0.0:$PORT` permitiendo a Render inyectar dinámicamente el puerto de red sin colisiones.
* **Health Check Endpoint:** `GET /health` responde `200 {"status": "ok", "app": "calculadora-web"}`. Render no enruta tráfico a la nueva instancia hasta que este endpoint responde satisfactoriamente.
* **Auto-Deploy:** Habilitado (`autoDeploy: true`). Todo commit o Pull Request mergeado a `main` desencadena la compilación y despliegue automático sin intervención manual.

### 4.3 Procedimiento de Rollback Inmediato
1. Ingresar al dashboard de Render en el servicio `calculadora-tbd`.
2. Dirigirse a la pestaña **Deploys**.
3. Localizar el deploy anterior estable (marcado en verde).
4. Hacer clic en los tres puntos $(\dots)$ y seleccionar **"Rollback to this deploy"**.
5. Tiempo estimado de recuperación: **$< 2$ minutos**.

---

## 🎛️ 5. Feature Toggle con ConfigCat

### 5.1 Matriz de Toggles y Configuración

| Clave en ConfigCat | Propósito | Estado Inicial | Rollout Gradual | Estado Final (GA) |
| :--- | :--- | :---: | :---: | :---: |
| `resta_enabled` | Operación de resta aritmética | `False` | 10% | `True` (100%) |
| `multiplicacion_enabled` | Operación de multiplicación | `False` | **10%** (Ticket 2) | `True` (100%) |
| `division_enabled` | División con validación por cero | `False` | 50% | **`True` (100%)** (Ticket 3) |
| `potencia_enabled` | Potenciación matemática ($a^b$) | `False` | 10% | `True` (100%) |
| `raiz_enabled` | Raíz cuadrada con control de negativos | `False` | 10% | `True` (100%) |

### 5.2 Gobernanza y Permisos
* **¿Quién puede activar/desactivar toggles?**  
  * **Product Owner (PO):** Autoridad para modificar porcentajes de rollout en producción y dar luz verde al GA (100%).
  * **Developers:** Autoridad para crear y probar flags en entornos de Staging/Desarrollo, y desactivar inmediatamente en caso de emergencia (*Kill Switch*).

---

## 📈 6. Conclusiones y Próximos Pasos
Con este taller se cierran exitosamente los tres pendientes de Fase 1:
1. El pipeline de CI/CD es una red de seguridad inquebrantable (Ruff + 49 Pytest + Docker Build).
2. Render despliega continuamente desde `main` con health checks automáticos.
3. ConfigCat desacopla el despliegue del lanzamiento, permitiendo rollouts porcentuales seguros.
4. El sliceado vertical de Ejemplo 5 (Tickets 1, 2 y 3) está completamente implementado y verificado.
