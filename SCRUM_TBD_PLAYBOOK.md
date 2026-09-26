# 📘 Scrum + Trunk-Based Development (TBD) Playbook
### *Guía Práctica para Equipos de Alta Frecuencia de Despliegue y Entrega Continua*

---

## 🎯 1. Diagnóstico del Flujo de Trabajo Actual

### 1.1 Mapa Visual del Flujo de Entrega
El flujo de desarrollo e integración del equipo sigue una arquitectura de entrega continua automatizada y validada por cada cambio:

```
[ Developer Local ] ──► [ Commit en Rama Corta ] ──► [ Pull Request a main ]
                                                              │
                                                              ▼
[ GitHub Packages / GHCR ] ◄── [ Merge a main ] ◄── [ CI: Ruff + Pytest ] ◄── [ Code Review ]
            │
            ▼
[ Despliegue Continuo ] ──► [ Feature Flags (ConfigCat) ] ──► [ Usuarios en Producción ]
```

### 1.2 Análisis de Fricciones y Salud del Flujo (Semáforo de Diagnóstico)

| Etapa del Flujo | Estado | Diagnóstico | Fricción Identificada |
| :--- | :---: | :--- | :--- |
| **Commit & Rama Local** | 🟢 | Ramas de vida corta (< 1 día), cambios atómicos y enfocados. | Ninguna. Alta agilidad local. |
| **Pull Request (PR)** | 🟢 | PRs pequeños de 50–150 líneas orientados a micro-incrementos. | Revisión ágil sin sobrecarga cognitiva. |
| **CI Automatizado (Lint & Tests)** | 🟢 | Ruff + Pytest ejecutados en < 20s en GitHub Actions. | Ejecución rápida que evita cuellos de botella. |
| **Code Review** | 🟡 | Dependencia de disponibilidad de revisores para merges rápidos. | Fricción moderada si el revisor tarda más de 2 horas. |
| **Merge a Main** | 🟢 | Trunk-based estricto con branch protection y reglas automáticas. | Flujo limpio y sin ramas de larga duración desfasadas. |
| **Construcción Docker & GHCR** | 🟢 | Build y Push automatizado a GitHub Container Registry en cada push a `main`. | Contenedores inmutables listos para desplegar. |
| **Despliegue & Activación** | 🟡 | Despliegue continuo con control por Feature Toggles de ConfigCat. | Necesidad de mantener disciplina en la limpieza de flags antiguos. |

### 1.3 Respuestas al Diagnóstico del Equipo
* **¿Cuánto tiempo vive normalmente una rama?**
  * *Objetivo TBD cumplido:* Menos de 24 horas (habitualmente entre 2 y 6 horas de desarrollo y revisión).
* **¿Qué tan seguido integramos realmente a main?**
  * *Frecuencia:* Múltiples veces al día (1 a 4 integraciones diarias por desarrollador).
* **¿Nuestro DoD actual incluye "está en main y es desplegable"?**
  * *Sí:* Todo incremento terminado debe estar integrado en `main`, con CI verde, imagen Docker publicada y funcionalidad oculta o expuesta de forma segura mediante Feature Flags.

---

## 👥 2. Roles Adaptados a TBD + Continuous Deployment

La adopción de TBD y CD transforma las responsabilidades tradicionales de Scrum para eliminar el miedo a integrar directamente sobre la rama troncal:

```
                  ┌────────────────────────────────────────┐
                  │          PRODUCT OWNER (PO)            │
                  │  • Prioriza por valor, riesgo y lote   │
                  │  • Controla rollout en ConfigCat       │
                  │  • Co-diseña el sliceado vertical      │
                  └──────────────────┬─────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
┌────────────────┴───────────────────┐   ┌───────────────┴────────────────────┐
│         DEVELOPERS / TEAM          │   │           SCRUM MASTER             │
│  • Responsabilidad colectiva       │   │  • Facilita integración diaria     │
│  • Main siempre verde y releasable │   │  • Elimina fricción del pipeline   │
│  • TDD, ramas cortas y toggles     │   │  • Protege tiempo técnico / deuda  │
└────────────────────────────────────┘   └────────────────────────────────────┘
```

### 2.1 Responsabilidades por Rol

#### 👑 Product Owner (PO)
* **Priorización orientada al flujo:** Prioriza historias no solo por valor de negocio, sino considerando el riesgo técnico y el tamaño del lote (*batch size*).
* **Gestión de Feature Toggles:** Decide los porcentajes de rollout gradual (ej. 10% → 50% → 100%) y la activación/desactivación de features en ConfigCat sin necesidad de nuevos despliegues de código.
* **Sliceado Vertical Activo:** Participa activamente en el refinamiento para descomponer historias grandes en incrementos pequeños que entreguen valor comprobable.

#### 💻 Developers (Equipo de Desarrollo)
* **Responsabilidad colectiva:** `main` es sagrado. Si el pipeline de CI se rompe, la máxima prioridad del equipo es arreglarlo (*Stop the Line / Andon Cord*).
* **Micro-incrementos y Ramas Efímeras:** Desarrollan en ramas de corta vida (< 1 día), usando toggles para código incompleto o experimental.
* **Ownership del Pipeline:** Mantenimiento de tests unitarios/integración rápidos y configuraciones de linters para garantizar feedback en segundos.

#### 🛡️ Scrum Master (SM)
* **Guardián de la cadencia de integración:** Monitorea que no existan ramas abiertas por más de 1 día y facilita el desbloqueo inmediato de revisiones de código.
* **Cultura sin culpa (*Blameless*):** Fomenta la experimentación y elimina el miedo a romper `main` promoviendo la reversión rápida (*revert-first*) y el desacoplamiento mediante toggles.
* **Protección de la deuda técnica del pipeline:** Asegura capacidad en el sprint para optimizar tiempos de build, pruebas y automatizaciones de entrega.

### 2.2 Compromisos de Acción Individual (*Post-its del Equipo*)
* 🎯 **Product Owner:** *"A partir de mañana, definiré los criterios de aceptación pensando en validaciones directas en producción con toggles apagados al inicio."*
* ⚡ **Developer:** *"A partir de mañana, no mantendré ninguna rama abierta por más de 1 día; si la funcionalidad no está completa, la integraré a main protegida con un feature flag."*
* 🛡️ **Scrum Master:** *"A partir de mañana, en cada Daily preguntaré qué se integrará hoy a main y protegeré tiempo para resolver cualquier fricción del pipeline de CI."*

---

## 🔄 3. Artefactos y Ceremonias Adaptados

| Artefacto / Ceremonia | Versión Clásica de Scrum | Adaptación a TBD + Continuous Deployment |
| :--- | :--- | :--- |
| **Product Backlog** | Lista de historias grandes agrupadas por épicas. | Historias re-sliceadas verticalmente en micro-incrementos con plan de Feature Flag y AC validables en producción. |
| **Sprint Backlog** | Paquete cerrado de tareas comprometidas para entregar al final de 2 semanas. | Flujo continuo de incrementos priorizados por valor, riesgo y orden de integración diaria a `main`. |
| **Incremento** | Paquete entregable al final del Sprint tras la Review. | Cada commit/PR mergeado en `main` que supera el pipeline de CI es un incremento potencialmente desplegable. |
| **Daily Scrum** | ¿Qué hice ayer? ¿Qué haré hoy? ¿Qué impedimentos tengo? | **¿Qué voy a integrar hoy a main y qué necesito para que sea seguro y pase el pipeline?** |
| **Sprint Review** | Demostración en ambiente local/staging de lo construido en 2 semanas. | Demostración de lo que ya está en producción (o tras toggle) con telemetría, métricas reales y feedback de usuarios. |
| **Sprint Retrospective** | Discusión general sobre procesos y relaciones de equipo. | Foco riguroso en métricas DORA, flujo de valor, cuellos de botella en Code Review/CI y salud de los Feature Flags. |

---

## 📜 4. Principios y Reglas de Oro de TBD

### 4.1 Los 5 Principios Fundamentales del Equipo
1. **Trunk es la única fuente de la verdad:** Todo el trabajo converge diariamente en la rama `main`.
2. **Desacoplar Despliegue de Lanzamiento:** Desplegar código a producción (*Deploy*) no significa activarlo para el usuario final (*Release*). Los Feature Flags permiten desplegar continuamente código en progreso sin impacto negativo.
3. **Calidad integrada en el origen (*Shift-Left Testing*):** Pruebas unitarias y linters se ejecutan localmente y en CI antes de cualquier merge.
4. **Cultura de Reversión Rápida (*Revert-First*):** Ante una falla en `main`, se revierte de inmediato el commit problemático para restaurar la salud del tronco, investigando la causa posteriormente.
5. **Revisión de Código Continua y Exprés:** Las revisiones de PRs pequeños tienen prioridad máxima en el día a día del equipo.

### 4.2 Las 5 Reglas de Oro de Integración a Main
```
┌────────────────────────────────────────────────────────────────────────┐
│               ✨ LAS 5 REGLAS DE ORO DE INTEGRACIÓN A MAIN             │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Tamaño del lote ≤ 1 día: Ninguna rama vive más de 24 horas.         │
│ 2. Main siempre verde: Si el CI falla, arreglar main es prioridad #1. │
│ 3. Feature Flags obligatorios para features incompletas o riesgosas.  │
│ 4. Cobertura de pruebas automatizadas al 100% en nuevos endpoints/código│
│ 5. Code Review en < 2 horas: PRs pequeños se revisan de inmediato.    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ 5. Definition of Ready (DoR) y Definition of Done (DoD)

### 5.1 Definition of Ready (DoR) Orientada a TBD
Una historia o incremento está **Ready** para entrar al Sprint si cumple con:
* [x] **Sliceado Vertical:** Está dividida en un incremento integrable a `main` en $\le 1$ día de trabajo.
* [x] **Criterios de Aceptación Verificables:** Los AC son claros y pueden validarse en producción/staging.
* [x] **Estrategia de Feature Flag:** Se definió si requiere Feature Flag, indicando el nombre de la clave en ConfigCat (ej. `raiz_enabled`) y su valor inicial (`False`).
* [x] **Sin dependencias bloqueantes externas:** No requiere la finalización previa de servicios de terceros no disponibles.
* [x] **Estrategia de pruebas clara:** El equipo comprende qué pruebas unitarias y de integración validarán el incremento.

### 5.2 Definition of Done (DoD) Preliminar (Técnico + Negocio)
Un incremento se considera **Done** cuando:
* [x] **Código y Linting:** Código implementado, formateado y sin advertencias con `ruff check .`.
* [x] **Suite de Pruebas:** Pruebas unitarias e integración ejecutadas y aprobadas al 100% con `pytest`.
* [x] **Revisión de Código:** PR revisado y aprobado por al menos un compañero de equipo.
* [x] **Integración a Main:** Código mergeado satisfactoriamente en `main`.
* [x] **CI/CD Exitoso:** Workflow de GitHub Actions ejecutado con éxito, generando la imagen Docker en GHCR (`ghcr.io/darioher/tests-and-build:latest`).
* [x] **Configuración de Feature Flag:** Flag registrado y verificado en ConfigCat (apagado o con el porcentaje de rollout acordado).
* [x] **Validación de Negocio:** Comportamiento validado en ambiente desplegado de acuerdo a los criterios de aceptación.

---

## 🚩 6. Estrategia de Feature Flags con ConfigCat

### 6.1 Nomenclatura y Convenciones
* Nombres descriptivos en minúsculas con sufijo `_enabled`:
  * `resta_enabled`: Habilita operaciones de resta, multiplicación y división.
  * `potencia_enabled`: Habilita la operación de cálculo exponencial.
  * `raiz_enabled`: Habilita la operación de raíz cuadrada.

### 6.2 Ciclo de Vida del Feature Toggle
```
[ 1. Creación ] ──► [ 2. Desarrollo Backend ] ──► [ 3. Exposición UI (Rollout 10%) ]
(Flag en False)       (Integrado a main)             (Monitoreo de errores)
                                                              │
                                                              ▼
[ 5. Limpieza de Deuda ] ◄── [ 4. Rollout Total ] ◄───────────┘
(Eliminar flag del código)    (100% de usuarios)
```

1. **Creación:** Flag registrado en ConfigCat con valor inicial `False`.
2. **Desarrollo Backend:** Código integrado a `main` protegido por `if not self._flag(...)`.
3. **Exposición Frontend & Rollout Gradual:** Activación progresiva (10% $\rightarrow$ 50% $\rightarrow$ 100%) validando estabilidad y telemetría.
4. **General Availability (GA):** Flag al 100% encendido para todos los usuarios.
5. **Retiro y Limpieza Técnica:** Al sprint siguiente de la estabilización, se programa una tarea técnica de limpieza para eliminar el flag y las bifurcaciones condicionales del código.

---

## 📊 7. Métricas de Rendimiento del Flujo (Métricas DORA)

Para evaluar y mejorar continuamente el desempeño del equipo, se realiza seguimiento de las 4 métricas DORA:

1. **Deployment Frequency (Frecuencia de Despliegue):** Múltiples despliegues por día a través de merges a `main`.
2. **Lead Time for Changes (Tiempo de Entrega de Cambios):** Menos de 4 horas desde el primer commit hasta la imagen Docker disponible en GHCR.
3. **Change Failure Rate (Tasa de Fallos en Cambios):** Menor al 5%, mitigado inmediatamente mediante desactivación de Feature Flags en tiempo real o reversión automática.
4. **Time to Restore Service (Tiempo de Restauración del Servicio):** Menos de 5 minutos mediante el apagado del flag en el dashboard de ConfigCat sin requerir re-despliegue de código.
