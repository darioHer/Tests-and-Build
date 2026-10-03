# 📋 Backlog y Planificación de Sprints con Entregas Incrementales (Taller 4)
### *Implementación Práctica en el Repositorio `Tests-and-Build`*

---

## 🔍 1. Diagnóstico del Backlog Actual

### 1.1 Objetivo del Diagnóstico
Evaluar qué tan **"TBD-friendly"** se encuentra el Product Backlog del proyecto de la Calculadora Web, aplicando los 4 criterios fundamentales de Trunk-Based Development para garantizar integraciones diarias a `main` sin riesgo de romper producción.

### 1.2 Evaluación con los 4 Criterios TBD

| Criterio | Pregunta Clave |
| :--- | :--- |
| **1. Tamaño** | ¿Se puede integrar a `main` en $\le 1$ día de trabajo? |
| **2. Verticalidad** | ¿Entrega valor de negocio por sí sola (end-to-end o funcionalidad comprobable)? |
| **3. Feature Toggle** | ¿Tiene definido si necesita toggle y cómo se llama la clave en ConfigCat? |
| **4. Validación en Producción** | ¿Los Acceptance Criteria se pueden verificar de forma no destructiva una vez desplegado? |

---

### 1.3 Matriz de Diagnóstico y Semáforo de Historias

```
                        🚦 SALUD DEL BACKLOG
┌──────────────────────────────────────┬────────────────────────┬─────────────┐
│ Historia de Usuario                  │ Evaluación 4 Criterios │ Clasificación│
├──────────────────────────────────────┼────────────────────────┼─────────────┤
│ Historia #1: Operaciones Avanzadas   │ 🔴 Tamaño: > 3 días     │ 🔴 Requiere │
│ (Potencia + Raíz + UI + Historial)   │ 🟢 Vertical: Sí         │ Re-sliceado │
│                                      │ 🟡 Toggle: No definido │ Urgente     │
│                                      │ 🟡 AC: Genéricos       │             │
├──────────────────────────────────────┼────────────────────────┼─────────────┤
│ Historia #2: Aritmética Completa     │ 🔴 Tamaño: > 2 días     │ 🟡 Requiere │
│ (Resta, Multiplicar, Dividir + UI)   │ 🟢 Vertical: Sí         │ Re-sliceado │
│                                      │ 🟡 Toggle: Parcial     │             │
│                                      │ 🟢 AC: Claros          │             │
├──────────────────────────────────────┼────────────────────────┼─────────────┤
│ Historia #3: Historial en Memoria    │ 🟢 Tamaño: ≤ 1 día      │ 🟢 Lista    │
│ (Endpoint /api/historial + UI)       │ 🟢 Vertical: Sí         │ para TBD    │
│                                      │ 🟢 Toggle: N/A         │             │
│                                      │ 🟢 AC: Verificables    │             │
└──────────────────────────────────────┴────────────────────────┴─────────────┘
```

#### Resultado de la Clasificación:
* 🟢 **Listas para TBD:** Historia #3 (Historial en Memoria).
* 🟡 **Necesitan re-sliceado:** Historia #2 (Operaciones Aritméticas).
* 🔴 **Demasiado grandes / riesgosas:** Historia #1 (Operaciones Avanzadas en bloque monolítico).

---

## ✂️ 2. Técnicas de Sliceado Vertical para TBD

### 2.1 Slice Horizontal vs. Slice Vertical

```
       SLICE HORIZONTAL (Antipatrón en TBD)              SLICE VERTICAL (Patrón TBD Recomendado)
┌──────────────────────────────────────────────┐     ┌────────────┬────────────┬────────────┐
│               UI / Frontend                  │     │ Incremento │ Incremento │ Incremento │
├──────────────────────────────────────────────┤     │    #1      │    #2      │    #3      │
│               API / Endpoints                │     │   (Suma)   │  (Resta +  │ (Potencia+ │
├──────────────────────────────────────────────┤     │            │   Toggle)  │  Rollout)  │
│             Lógica de Negocio                │ ──► │  UI + API  │  UI + API  │  UI + API  │
├──────────────────────────────────────────────┤     │   + Lógica │   + Lógica │   + Lógica │
│            Persistencia / Datos              │     │   + Tests  │   + Tests  │   + Tests  │
└──────────────────────────────────────────────┘     └────────────┴────────────┴────────────┘
 (Genera ramas de larga vida y merge hell)               (Integrable diariamente a main)
```

### 2.2 Técnicas Aplicadas en el Proyecto
1. **Slice por Operación:** Separación de cada función matemática (`sum`, `resta`, `multiplicar`, `dividir`, `potencia`, `raiz_cuadrada`) en incrementos atómicos e independientes.
2. **Slice por Regla de Negocio:** Separar el camino feliz inicial (cálculos estándar) del tratamiento especializado de casos de borde (ej. error de división por cero `DivisionPorCeroError` y error de números negativos `NumeroNegativoError`).
3. **Slice por Experiencia de Usuario:** Desplegar primero la funcionalidad del backend y API, y luego exponer el elemento visual y su renderizado en la interfaz gráfica.
4. **Slice por Feature Toggle:** Desplegar código a `main` protegido por un toggle de ConfigCat apagado (`False`), realizar un rollout parcial (ej. 10%) para monitoreo y finalmente encender al 100% para todos los usuarios.

---

### 2.3 Ejercicio Práctico: Re-sliceado de Historias

#### 📦 Historia Original #1: Soporte de Operaciones Matemáticas Avanzadas (Potencia y Raíz)

```yaml
Historia original: #1 - Operaciones Avanzadas (Potencia y Raíz Cuadrada)
```

##### 🔹 Incremento 1: Potencia en Backend con Feature Flag
* **Descripción:** Implementar el método `potencia(a, b)` en la clase `Calculator` de `main.py`, protegido por el feature flag `potencia_enabled` en ConfigCat (apagado por defecto), junto con tests unitarios.
* **¿Se puede integrar en $\le 1$ día?:** Sí (estimado: 2 horas de desarrollo y testing).
* **¿Necesita Feature Toggle?:** Sí $\rightarrow$ `potencia_enabled` (valor por defecto: `False`).
* **Acceptance Criteria verificables en prod/staging:**
  * Si `potencia_enabled=False`, invocar `calc.potencia(2, 3)` lanza `FeatureDisabledError`.
  * Si `potencia_enabled=True`, `calc.potencia(2, 3)` retorna `8`.
  * Suite de `pytest tests.py` pasa al 100% y linter `ruff check .` queda limpio.

##### 🔹 Incremento 2: Exposición de Potencia en Endpoint REST y UI con Rollout al 10%
* **Descripción:** Crear el endpoint `GET /api/potencia?a=<i>&b=<j>` en `app.py`, y agregar los campos de entrada y botón en `index.html` y `script.js` con visibilidad controlada dinámicamente según el estado del flag en ConfigCat.
* **¿Se puede integrar en $\le 1$ día?:** Sí (estimado: 3 horas).
* **¿Necesita Feature Toggle?:** Sí $\rightarrow$ `potencia_enabled` (activación al 10% de usuarios vía ConfigCat).
* **Acceptance Criteria verificables en prod/staging:**
  * `GET /api/potencia?a=2&b=3` responde `200 {"result": 8}` cuando el flag está activo para el usuario.
  * Si el flag está inactivo, responde `404 {"error": "feature_disabled"}` y la UI oculta el bloque de potencia sin generar errores de consola.
  * Si los parámetros son inválidos, responde `400 {"error": "invalid_params"}`.

##### 🔹 Incremento 3: Raíz Cuadrada en Backend con Manejo de Números Negativos
* **Descripción:** Implementar el método `raiz_cuadrada(a)` en `Calculator`, protegido por el feature flag `raiz_enabled` (apagado por defecto), validando que $a \ge 0$ o lanzando `NumeroNegativoError`.
* **¿Se puede integrar en $\le 1$ día?:** Sí (estimado: 2 horas).
* **¿Necesita Feature Toggle?:** Sí $\rightarrow$ `raiz_enabled` (valor por defecto: `False`).
* **Acceptance Criteria verificables en prod/staging:**
  * Si `raiz_enabled=True` y $a=9$, retorna `3.0`.
  * Si `raiz_enabled=True` y $a < 0$, lanza `NumeroNegativoError` con mensaje `"No se puede calcular la raíz cuadrada de un número negativo."`.
  * Si `raiz_enabled=False`, lanza `FeatureDisabledError`.

##### 🔹 Incremento 4: Raíz Cuadrada en Endpoint, UI y Rollout al 100%
* **Descripción:** Añadir endpoint `GET /api/raiz?a=<k>`, integrar botón en la interfaz web, registrar el cálculo en el historial visual y elevar los flags a disponibilidad general (100%).
* **¿Se puede integrar en $\le 1$ día?:** Sí (estimado: 3 horas).
* **¿Necesita Feature Toggle?:** Sí $\rightarrow$ `raiz_enabled` y `potencia_enabled` al 100% en ConfigCat.
* **Acceptance Criteria verificables en prod/staging:**
  * `GET /api/raiz?a=16` retorna `200 {"result": 4.0}`.
  * `GET /api/raiz?a=-4` retorna `400 {"error": "numero_negativo"}`.
  * La operación $\sqrt{16} = 4.0$ se agrega automáticamente a la lista visual de historial.

---

## 🏃 3. Planificación de Sprint Orientada a Flujo

### 3.1 Sprint Goal Orientado a TBD
> *"Al final del sprint, los usuarios podrán realizar cálculos exponenciales (potencia), calcular raíces cuadradas con control estricto de números negativos y consultar su historial interactivo en la interfaz web, manteniendo las funcionalidades avanzadas bajo control dinámico de Feature Flags con despliegue diario continuo a `main`."*

### 3.2 Selección y Ordenamiento del Trabajo

El trabajo se prioriza aplicando la fórmula: **Mayor Valor + Menor Batch Size + Mitigación Temprana de Riesgos**:

1. **Día 1 (Regla de Oro):** Integración de Incremento 1 (Potencia Backend con flag).
2. **Día 2:** Integración de Incremento 2 (Endpoint y UI de Potencia con rollout al 10%).
3. **Día 3:** Integración de Incremento 3 (Raíz Cuadrada Backend con manejo de negativos y flag).
4. **Día 4:** Integración de Incremento 4 (Endpoint, UI de Raíz Cuadrada, Historial y Rollout al 100%).
5. **Día 5:** Limpieza de deuda técnica, pruebas de carga y verificación del pipeline de CI/CD.

### 3.3 Plan de Integración Diaria (Tablero de Flujo)

```
┌────────────────────────────────┬────────────────────────────────┬────────────────────────────────┐
│            DÍA 1 - 2           │            DÍA 3 - 4           │             DÍA 5+             │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ 🚀 [Merge Día 1]               │ 🚀 [Merge Día 3]               │ 🚀 [Merge Día 5]               │
│ • Inc. 1: Potencia Backend     │ • Inc. 3: Raíz Cuadrada Backend│ • Inc. 4: Raíz Cuadrada UI     │
│   (flag: potencia_enabled=off) │   (flag: raiz_enabled=off)     │   + Historial Web Dinámico     │
│ • Pruebas unitarias pytest     │ • Manejo NumeroNegativoError   │ • Rollout al 100% ConfigCat    │
│                                │                                │                                │
│ 🚀 [Merge Día 2]               │ 🚀 [Merge Día 4]               │ 🧹 [Tareas de Cierre]          │
│ • Inc. 2: /api/potencia + UI   │ • /api/raiz con validaciones   │ • Verificación GHCR Docker     │
│ • Rollout gradual 10%          │ • Pruebas de integración Flask │ • Plan de retiro de flags      │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

### 3.4 Capacidad Realista y Mitigación de Fricciones
Para garantizar que cada incremento se integre en $\le 1$ día, se contemplan los siguientes amortiguadores de capacidad:
* **Tiempo de Code Review:** Máximo 2 horas de espera. Los PRs de menos de 100 líneas tienen prioridad de revisión inmediata entre pares.
* **Tiempo de Pipeline de CI:** Optimizado para tardar menos de 30 segundos (Ruff + Pytest con caché de pip).
* **Mitigación de Pipeline Roto:** Protocolo *Revert-First*; si un commit rompe `main`, se revierte en $< 5$ minutos y se diagnostica en local.

---

## 📌 4. Definition of Ready (DoR) Orientada a TBD

Toda historia o incremento debe cumplir obligatoriamente los 5 criterios de DoR antes de ser aceptado en la planificación del sprint:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   🎯 CHECKLIST DE DEFINITION OF READY                  │
├────────────────────────────────────────────────────────────────────────┤
│ [x] 1. Tamaño acotado: Estimado para desarrollarse e integrarse en     │
│        menos de 24 horas (≤ 1 día de trabajo).                         │
│ [x] 2. Acceptance Criteria verificables en producción tras el despliegue.│
│ [x] 3. Nombre del Feature Flag definido (ej. potencia_enabled,         │
│        raiz_enabled) con valor inicial desactivado (False).            │
│ [x] 4. Cero dependencias bloqueantes externas o infraestructura ausente.│
│ [x] 5. Estrategia de pruebas unitarias y de integración acordada por el│
│        equipo antes de iniciar la codificación.                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 5. Cierre y Actualización del Playbook

### 5.1 Acuerdos Incorporados al Playbook
1. **Orden del Sprint Backlog:** El backlog se ordena por secuencia cronológica de integración a `main` (Día 1, Día 2, Día 3...). El primer ítem debe poder integrarse en el Día 1 obligatoriamente.
2. **Formato de Sprint Goal:** Redactado separando explícitamente la entrega de valor funcional de la activación mediante Feature Toggles.
3. **DoR Estricto:** Ninguna historia entra al sprint si no puede integrarse en $\le 1$ día o carece de definición de feature toggle cuando involucra código en progreso.

### 5.2 Tres Acciones Concretas para el Próximo Sprint
1. 🛡️ **Acción 1:** Toda nueva historia deberá ser sometida a la matriz de los 4 criterios TBD durante el Refinamiento antes de ingresar a la Sprint Planning.
2. ⚡ **Acción 2:** Ningún Pull Request podrá superar las 200 líneas de código modificado para asegurar revisiones de menos de 2 horas.
3. 🚩 **Acción 3:** Al inicio de cada sprint, se creará una tarea de limpieza técnica para remover los feature flags que hayan alcanzado el 100% de rollout en el sprint anterior.

### 5.3 Ronda Final: *¿Qué cambia en nuestra próxima Planning después de este taller?*
> *"Nuestra próxima Planning ya no se enfocará en comprometer paquetes cerrados de código para entregarlos al último día del sprint con miedo a los merges. Ahora planificaremos en términos de **integraciones continuas diarias**, donde cada día un desarrollador hace merge a `main`, el pipeline de CI valida automáticamente la calidad, y el Product Owner tiene el control en tiempo real para activar o desactivar funcionalidades desde ConfigCat sin requerir nuevos despliegues."*
