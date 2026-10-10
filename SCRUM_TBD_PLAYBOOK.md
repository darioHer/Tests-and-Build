# 📘 Scrum + Trunk-Based Development (TBD) Playbook (Versión 3.0)
### *Guía Oficial de Adaptación a Continuous Deployment, Ceremonias y Liberación Segura*
> **Aprobado por el Equipo de Ingeniería & Producto**  
> *Prerrequisito completado: Talleres 1 al 6 completados + Pipeline CI/CD en Render + ConfigCat + DoD 100% activo.*

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
[ Despliegue Continuo (Render) ] ──► [ Feature Flags (ConfigCat) ] ──► [ Usuarios en Producción ]
```

### 1.2 Análisis de Fricciones y Salud del Flujo (Semáforo de Diagnóstico)

| Etapa del Flujo | Estado | Diagnóstico | Fricción Identificada |
| :--- | :---: | :--- | :--- |
| **Commit & Rama Local** | 🟢 | Ramas de vida corta (< 1 día), cambios atómicos y enfocados. | Ninguna. Alta agilidad local. |
| **Pull Request (PR)** | 🟢 | PRs pequeños de 50–150 líneas orientados a micro-incrementos. | Revisión ágil sin sobrecarga cognitiva. |
| **CI Automatizado (Lint & Tests)** | 🟢 | Ruff + Pytest ejecutados en < 20s en GitHub Actions. | Ejecución rápida que evita cuellos de botella. |
| **Code Review** | 🟢 | Regla de revisión en < 2 horas. PRs pequeños se revisan de inmediato. | Fluidez continua sin bloqueos prolongados. |
| **Merge a Main** | 🟢 | Trunk-based estricto con branch protection y reglas automáticas. | Flujo limpio y sin ramas de larga duración desfasadas. |
| **Construcción Docker & GHCR** | 🟢 | Build y Push automatizado a GHCR solo en push a `main`. | Contenedores inmutables listos para desplegar. |
| **Despliegue Continuo (Render)** | 🟢 | Auto-deploy disparado por webhook al mergear en `main`. | Comprobación de salud en `/health` antes de recibir tráfico. |
| **Liberación por Toggles** | 🟢 | Control de activación desacoplado mediante ConfigCat. | Monitoreo en tiempo real y política de retiro de flags. |

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
│  • Main siempre verde y releasable │   │  • Elimina miedo a romper main     │
│  • TDD, ramas cortas y toggles     │   │  • Protege tiempo del pipeline     │
└────────────────────────────────────┘   └────────────────────────────────────┘
```

### 2.1 Responsabilidades por Rol

#### 👑 Product Owner (PO)
* **Priorización orientada al flujo:** Prioriza historias considerando el riesgo técnico, impacto de negocio y tamaño del batch.
* **Control de Lanzamiento (Release):** Decide los porcentajes de rollout gradual (0% $\rightarrow$ 20% $\rightarrow$ 100%) y la activación de features en ConfigCat sin depender de despliegues de infraestructura.
* **Sliceado Vertical Activo:** Participa activamente en el refinamiento para descomponer historias grandes en incrementos pequeños que entreguen valor comprobable en producción.

#### 💻 Developers (Equipo de Desarrollo)
* **Responsabilidad colectiva:** `main` es sagrado. Si el pipeline de CI se rompe, la máxima prioridad del equipo es arreglarlo (*Stop the Line / Andon Cord*).
* **Micro-incrementos y Ramas Efímeras:** Desarrollan en ramas de corta vida (< 1 día), usando toggles para código incompleto o experimental.
* **Ownership del Pipeline:** Mantenimiento de tests rápidos, cobertura y telemetría de errores antes de encender cualquier flag.

#### 🛡️ Scrum Master (SM)
* **Guardián de la cadencia de integración:** Facilita la disciplina de integración diaria. Elimina el miedo a romper `main` mediante la cultura blameless y reversión rápida.
* **Protección del tiempo técnico:** Asegura capacidad en el sprint para optimizar pipelines, eliminar tests flaky y limpiar toggles obsoletos.

### 2.2 Compromisos de Acción Individual (*Post-its del Equipo*)
* 🎯 **Product Owner:** *"A partir de mañana, definiré los criterios de aceptación pensando en validaciones directas en producción con toggles apagados al inicio."*
* ⚡ **Developer:** *"A partir de mañana, no mantendré ninguna rama abierta por más de 1 día; si la funcionalidad no está completa, la integraré a main protegida con un feature flag."*
* 🛡️ **Scrum Master:** *"A partir de mañana, en cada Daily preguntaré qué se integrará hoy a main y protegeré tiempo para resolver cualquier fricción del pipeline de CI."*

---

## 🔄 3. Artefactos y Ceremonias Adaptados a CD + TBD

| Artefacto / Ceremonia | Versión Clásica de Scrum | Adaptación a TBD + Continuous Deployment (v3.0) |
| :--- | :--- | :--- |
| **Product Backlog** | Lista de historias grandes agrupadas por épicas. | Historias sliceadas verticalmente + plan de Feature Toggle + AC validables en producción. |
| **Sprint Backlog** | Trabajo del sprint en bloque cerrado de 2 semanas. | Trabajo que se planea integrar a main diariamente priorizado por valor y riesgo. |
| **Incremento** | Paquete entregable al final del sprint. | Cualquier commit en main que pase CI y se despliegue es un incremento potencial. |
| **Daily Scrum** | ¿Qué hice ayer? ¿Qué haré hoy? ¿Qué impedimentos? | **¿Qué voy a integrar hoy a main y qué necesito para que sea seguro?** |
| **Sprint Review** | Demo del incremento del sprint en ambiente local/staging. | **Demo de lo que ya está (o puede estar) en producción + feedback real con telemetría.** |
| **Sprint Retrospective** | Discusión general sobre procesos. | **Mejorar flujo de valor + salud del pipeline + disciplina de TBD.** |

---

## 🎬 4. Formato Oficial del Nuevo Sprint Review (Punto 1 del Taller 6)

### 4.1 Principios del Review en CD + TBD
1. **Demostración en Producción Real:** La demo se realiza sobre el ambiente desplegado en **Render**, no en localhost.
2. **Valor Incremental con Toggles:** Se muestra la funcionalidad con el Feature Toggle encendido y se demuestra el comportamiento seguro (*Fail-Closed*) cuando está apagado.
3. **Telemetría y Datos Reales:** Se acompaña la demo funcional con métricas de salud (latencia, tasa de errores y tasa de conversión).
4. **Enfoque en Valor Percibido:** La conversación con los stakeholders se centra en: *"¿Qué valor recibieron realmente los usuarios con este incremento?"* en vez de *"¿Cuántas líneas de código escribimos?"*.

### 4.2 Estructura Obligatoria de Cada Demostración (4–5 min por ítem)
Para cada incremento presentado, el presentador debe seguir estrictamente este guion:
1. **¿Qué problema de usuario resuelve?** (Contexto y dolor de negocio mitigado).
2. **¿Está activo para todos o detrás de toggle?** (Estado del rollout: 0%, 20% canary, o 100% GA).
3. **Demo en vivo en Render:** Demostración práctica de la funcionalidad (con toggle ON/OFF para validar aislamiento).
4. **Métrica o evidencia de valor:** Datos de telemetría (ej. latencia promedio, tasa de éxito, errores 5xx).
5. **Pregunta al stakeholder / PO:** *"¿Esto genera el valor esperado?"* para capturar feedback inmediato.

### 4.3 Roles durante la Simulación del Review
* **Developer:** Realiza la demostración técnica en vivo sobre el servicio desplegado.
* **Product Owner:** Facilita las preguntas de negocio y valida la retroalimentación de los interesados.
* **Scrum Master y Observadores:** Anotan oportunidades de mejora en el formato y tiempos de la sesión.

---

## 🔄 5. Formato Oficial de la Nueva Sprint Retrospective (Punto 2 del Taller 6)

### 5.1 Los 3 Nuevos Focos Obligatorios de Inspección
La Retrospectiva audita formalmente tres dimensiones cuantitativas y cualitativas del flujo:

```
┌────────────────────────────────────────────────────────────────────────┐
│               🔍 LOS 3 NUEVOS FOCOS DE LA RETROSPECTIVA TBD            │
├────────────────────────────────────────────────────────────────────────┤
│ 1. SALUD DEL PIPELINE:                                                 │
│    • ¿Cuántas veces se rompió el CI?                                  │
│    • ¿Cuánto tardó el deploy promedio a Render?                        │
│    • ¿Hubo rollbacks o caídas de health check?                         │
│                                                                        │
│ 2. DISCIPLINA TBD:                                                     │
│    • ¿Cuántas integraciones diarias a main logramos?                   │
│    • ¿Alguna rama vivió más de 1 día?                                  │
│    • ¿Usamos Feature Toggles correctamente sin acumular deuda?         │
│                                                                        │
│ 3. FLUJO DE VALOR:                                                     │
│    • Lead Time (desde el primer commit hasta código en producción).   │
│    • ¿El valor llegó realmente a los usuarios finales?                 │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Dinámica de Retrospectiva (Estructura de 4 Columnas en Miro)
El equipo debate y organiza los hallazgos en cuatro cuadrantes:
1. 🟢 **Lo que funcionó bien en el flujo:** Éxitos de automatización, tests rápidos, builds verdes.
2. 🟡 **Lo que generó fricción:** Retrasos en Code Reviews, tests intermitentes (*flaky*), acumulación de toggles.
3. 🔴 **Lo que rompió el flujo o generó miedo:** Fallos en health check, falta de observabilidad, presiones comerciales prematuras.
4. 🎯 **Acciones de mejora:** **Regla de oro: Máximo 3 acciones concretas, asignables y medibles.**

### 5.3 Preguntas Guía del Facilitador
* ¿Qué nos impidió integrar más veces al día a `main`?
* ¿El auto-deploy nos dio más confianza o más miedo?
* ¿Los Feature Toggles nos ayudaron a mitigar riesgos o se están volviendo deuda técnica acumulada?
* ¿El Definition of Done (DoD) se respetó realmente en cada commit?

---

## 🛡️ 6. Política Oficial de Liberación Segura de Valor (Punto 3 del Taller 6)

### 6.1 Principio de Desacoplamiento (Deploy $\neq$ Release)
El código se despliega a producción en el instante en que pasa los tests y se mergea a `main`. Sin embargo, la exposición a los usuarios finales es un evento de negocio gobernado por ConfigCat.

### 6.2 Estrategia de Rollout Progresivo (Canary Release)
Toda funcionalidad de impacto crítico sigue un proceso de liberación en 4 etapas:
1. **Fase 0 — Inactivo (0% OFF):** Código en producción, validado por tests automatizados pero invisible para usuarios generales.
2. **Fase 1 — Rollout Interno / Canary (5% – 20%):** Activación para empleados internos y cohorte beta. Se recopila telemetría de pasarela, latencia y errores.
3. **Fase 2 — Monitoreo Activo (24–48 horas):** Observación estricta de las métricas clave antes de proceder a la apertura general.
4. **Fase 3 — General Availability (100% GA):** Apertura total una vez verificada la estabilidad.

### 6.3 Criterios de Corte y Kill Switch Inmediato (< 1 segundo)
Si durante una fase de liberación ocurre cualquiera de las siguientes condiciones:
* Tasa de error transaccional $> 1.0\%$.
* Latencia promedio en p95 $> 500\text{ ms}$.
* Caída del endpoint de salud `/health`.

**Acción Obligatoria:** Se dispara inmediatamente el **Kill Switch** (desactivando el Feature Toggle en el dashboard de ConfigCat a `False`). La funcionalidad queda deshabilitada en menos de 1 segundo sin requerir re-compilaciones, pipelines ni re-despliegues de contenedores Docker.

### 6.4 Higiene y Limpieza Obligatoria de Feature Toggles
* **Límite de Vida Útil:** Un Feature Toggle no debe permanecer en el código más de **30 días** tras alcanzar 100% GA.
* **Prohibición de Toggles Fantasma:** Queda terminantemente prohibido mantener flags por más de 45 días.
* **Ticket Técnico Automático:** Al encender un flag al 100%, se crea automáticamente un issue en GitHub con la etiqueta `tech-debt:cleanup-toggle` para eliminar las bifurcaciones condicionales `if/else` en el sprint siguiente.

---

## 💼 7. Resolución del Caso Práctico: "Pagos Express en Main" (Taller 6)

Durante el taller se analizó el caso crítico: *"La funcionalidad de 'Pagos Express' ya está en main, pero nadie se atreve a activarla"*. El equipo acordó las siguientes soluciones formales a los 7 hechos problemáticos:

| # | Hecho Problemático del Caso | Decisión y Acuerdo del Equipo en Playbook v3.0 |
| :-: | :--- | :--- |
| **1** | PO quiere activar al 20% un viernes por presión comercial. | **Política de No-Releases en Viernes:** Los rollouts canary sólo se inician de lunes a jueves en horario laboral con equipo de guardia disponible. |
| **2** | Último deploy falló health check 11 min y requirió rollback. | **Auditoría de Health Checks:** El endpoint `/health` debe probarse en el pipeline antes de enrutar tráfico. No se activan toggles en servicios inestables. |
| **3** | 3 Feature Toggles llevan más de 45 días sin limpiar. | **Saneamiento Inmediato:** Se auditaron y crearon PRs de limpieza para retirar los 3 toggles antiguos (`promo_verano_2026`, `dark_mode_beta`, `checkout_v0_legacy`). |
| **4** | Solo 4 integraciones a main en el sprint. | **Sliceado Fino Obligatorio:** Ninguna tarea puede superar 1 día de desarrollo. Se refuerza la integración diaria asistida por toggles. |
| **5** | Rama viva 4 días por test flaky en CI. | **Cero Tolerancia a Tests Flaky:** Test inestable se aísla o corrige de inmediato. Ninguna rama puede esperar más de 24 horas por fallos espurios. |
| **6** | Cero métricas de conversión o errores de pago. | **Telemetría Obligatoria:** Se implementó `PagosExpressService.obtener_metricas()` con tracking en tiempo real de tasa de error, latencia y conversión antes de tocar el flag. |
| **7** | Negocio anunció internamente que ya está listo. | **Alineación PO-Stakeholders:** El PO comunica formalmente el estado de canary (20%) y no declara GA hasta completar las 48h de observación segura. |

---

## 📋 8. Checklist Oficial de Fase 1 (100% Cerrado y Validado)

Con el cierre del Taller 6, el equipo valida que el 100% de los acuerdos y artefactos de la Fase 1 están completamente operativos:

- [x] **1. Pipeline CI con Jobs Separados:** Job `test` (Ruff + Pytest) corre en cada PR; job `build_and_push` corre únicamente en push a `main`.
- [x] **2. Ruleset de Branch Protection:** Rama `main` protegida contra pushes directos, exigiendo PR, checks automáticos verdes y aprobación.
- [x] **3. Despliegue Continuo Automatizado:** Servicio desplegado en **Render** con auto-deploy activo y monitoreo en `/health`.
- [x] **4. Gestión de Feature Flags con ConfigCat:** Integración con arquitectura Fail-Closed (`default=False`), targeting de usuarios y simulación de canary.
- [x] **5. Adaptación Oficial del Sprint Review:** Formato probado basado en demostraciones en producción real, valor incremental y métricas.
- [x] **6. Adaptación Oficial de la Sprint Retrospective:** Dinámica de 4 columnas centrada en salud del pipeline, disciplina TBD y máx 3 acciones.
- [x] **7. Política de Liberación Segura:** Procedimiento establecido de rollout canary (20%), observación de 24-48h, Kill Switch y limpieza de toggles.

---

## 💬 9. Ronda Final de Cierre del Taller 6

> **Pregunta de Cierre:** *"En una frase: ¿Qué cambia en nuestro próximo Review y Retro después de este taller?"*
> 
> **Respuesta Unánime del Equipo:**  
> *"Nunca más llegaremos a una Review a mostrar diapositivas o código local sin desplegar: mostramos lo que ya corre en producción tras toggles con métricas reales. Y en cada Retro, antes de hablar de percepciones, auditaremos primero la salud del pipeline, el tiempo de los deploys y la disciplina de integrar a main cada día."*
