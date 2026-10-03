# ✅ Definition of Done (DoD) — Calculadora Web & CI/CD
> **Documento Oficial del Equipo de Ingeniería**  
> *Aplicable a todo incremento, Pull Request y commit integrado a `main`.*

---

## 🎯 1. Propósito de la Definition of Done en Trunk-Based Development
En un flujo de **Trunk-Based Development (TBD)** y **Continuous Deployment**, la rama `main` debe ser **siempre desplegable** (*releasable*) en cualquier instante.  
La *Definition of Done (DoD)* es el contrato de calidad inquebrantable acordado por el equipo para garantizar que ningún código rompa producción ni degrade la experiencia de usuario.

---

## 📋 2. Criterios de Aceptación Técnicos Obligatorios

| # | Dimensión | Criterio de Calidad | Verificación Local / CI |
| :-: | :--- | :--- | :--- |
| **1** | **Código Limpio & Linter** | Cero errores o advertencias de linter y formato según estándares PEP 8. | `ruff check src/` pasa en verde sin warnings. |
| **2** | **Pruebas Unitarias & Cobertura** | 100% de tests unitarios de la lógica de dominio pasando satisfactoriamente. Cobertura obligatoria de caminos felices y excepciones de borde. | `pytest src/tests.py` pasa al 100%. |
| **3** | **Pruebas de Integración API** | Todos los endpoints REST (`/api/*`, `/health`) validados con códigos de respuesta HTTP adecuados (`200`, `400`, `404`). | `pytest src/test_app.py` pasa al 100%. |
| **4** | **Construcción de Contenedor Docker** | El `Dockerfile` debe construir limpiamente una imagen ejecutable, sin dependencias huérfanas ni errores de empaquetado. | `docker build ./src` ejecuta exitosamente. |
| **5** | **Branch Protection & Code Review** | Todo cambio proviene de una rama de vida corta (< 24 h) y cuenta con aprobación de al menos un revisor antes del merge a `main`. | Pull Request en GitHub verificado y aprobado. |
| **6** | **Pipeline de CI Verde** | Los workflows de GitHub Actions (`ci.yaml`) se ejecutan con éxito de principio a fin. | Badge verde en GitHub Actions (`Test and Build`). |
| **7** | **Artefacto Inmutable Publicado** | Para cada merge en `main`, la imagen Docker queda etiquetada y publicada en GitHub Container Registry (GHCR). | `ghcr.io/darioher/tests-and-build:latest` actualizada. |

---

## 🚩 3. Criterios de Feature Flags y Rollout Seguro (ConfigCat)

| # | Dimensión | Criterio de Control | Verificación en ConfigCat |
| :-: | :--- | :--- | :--- |
| **8** | **Protección de Funcionalidad Incompleta** | Toda nueva operación o cambio no apto para GA debe estar protegido detrás de un Feature Flag. | SDK ConfigCat integrado en backend y frontend. |
| **9** | **Principio Fail-Closed** | Si el SDK no tiene API Key o ConfigCat no responde, la funcionalidad queda **desactivada por defecto** (`False`). Jamás se activa por error. | Tests de fallo de red (`sin_sdk_key`, `configcat_falla`) en verde. |
| **10** | **Estrategia de Rollout Definida** | Se establece explícitamente el porcentaje de activación: `0%` (desarrollo), `10%` (canary / testing con usuarios reales) o `100%` (GA). | Configurado en el Dashboard de ConfigCat. |
| **11** | **Permisos de Gestión Claros** | La activación o cambio de porcentaje de rollout es potestad del **Product Owner (PO)** en acuerdo con el equipo técnico. | Gestión de usuarios y roles en ConfigCat. |

---

## 🚀 4. Criterios de Despliegue Continuo (Render)

| # | Dimensión | Criterio de Despliegue | Verificación en Render |
| :-: | :--- | :--- | :--- |
| **12** | **Auto-deploy desde Main** | Al mergearse un cambio en `main`, Render dispara automáticamente el build y deploy del servicio. | Verificado en el historial de eventos de Render. |
| **13** | **Health Check Operativo** | El orquestador de Render sondea `/health` y el servicio responde `200 OK` antes de recibir tráfico de producción. | `GET /health` $\rightarrow$ `{"status": "ok"}`. |
| **14** | **Capacidad de Rollback Inmediato** | En caso de anomalía no contenida por Feature Flag, el equipo puede re-desplegar la versión previa en < 3 minutos. | Probado mediante botón "Rollback to this deploy" en Render. |

---

## 🛑 5. Acuerdo de Equipo: "Stop the Line" (Andon Cord)
> **Regla de Oro:** *"Si el CI de `main` está en rojo, se detiene inmediatamente la mezcla de nuevas funcionalidades hasta que la rama principal esté verde y saludable."*

1. **Prioridad Absoluta:** Arreglar el pipeline o revertir el commit causante (*Revert-First*) tiene precedencia sobre cualquier tarea del Sprint.
2. **Tiempo Máximo de Resolución:** Si un fallo en `main` no se repara en menos de 10 minutos, se realiza un `git revert` inmediato del commit causante.
3. **Cultura Sin Culpa (*Blameless*):** Los errores son oportunidades de robustecer las pruebas automáticas y el DoD.
