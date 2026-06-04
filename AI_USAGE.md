# AI_USAGE.md — LoanSight

Declaración de uso de inteligencia artificial por componente,
según la política del curso (Sección 8 del enunciado).

---

## Criterio de clasificación

| Categoría | Descripción |
|---|---|
| **IA** | Generado principalmente con asistencia de IA (Claude) |
| **Propio** | Escrito y comprendido por el autor; puede haberse usado IA para sugerencias menores |
| **Mixto** | La IA generó el andamiaje; el autor tomó las decisiones de fondo y puede explicarlas |

---

## Por componente

### Capa de datos — Warehouse (DuckDB)

| Artefacto | Autoría | Detalle |
|---|---|---|
| Diseño del esquema estrella | **Propio** | Decisión de qué variables se convierten en dimensiones y cuáles en hechos, justificada en el reporte |
| `scripts/build_warehouse.py` | **Mixto** | Estructura del script generada con Claude; lógica de carga y tipado revisada y ajustada manualmente |
| `backend/app/warehouse/schema.py` | **Mixto** | DDL generado con Claude; nombres de tablas y columnas decididos por el autor |
| `backend/app/warehouse/queries.py` | **Mixto** | Plantillas SQL generadas con Claude; whitelist de dimensiones/métricas y agregaciones definidas por el autor |

---

### Capa de análisis — EDA y preprocesamiento

| Artefacto | Autoría | Detalle |
|---|---|---|
| `notebooks/01_eda.ipynb` | **Mixto** | Código del análisis generado con Claude; el autor decidió qué explorar, qué visualizar y qué concluir, y puede explicarlo |
| `notebooks/02_preprocessing.ipynb` | **Mixto** | Código generado con Claude; las decisiones de imputación, encoding y escalado las tomó el autor con base en el EDA |
| `backend/app/preprocessing/pipeline.py` | **Mixto** | Código del `ColumnTransformer` generado con Claude a partir de las decisiones del notebook |

---

### Capa de modelado

| Artefacto | Autoría | Detalle |
|---|---|---|
| Selección de algoritmos y métricas | **Propio** | Decisión de qué algoritmos comparar, qué métricas son apropiadas dado el desbalanceo, y por qué |
| `notebooks/03_modeling.ipynb` | **Mixto** | Código de experimentos generado con Claude; las comparaciones, la selección de modelo y el análisis de resultados son del autor |
| `backend/app/models/train.py` | **Mixto** | Código de serialización generado con Claude; hiperparámetros y lógica de validación definidos por el autor |

---

### Capa de presentación — API y Frontend

| Artefacto | Autoría | Detalle |
|---|---|---|
| `backend/app/main.py` | **IA** | App FastAPI, routers y CORS generados con Claude |
| `backend/app/db.py` | **IA** | Conexión a DuckDB (cursor por petición) generada con Claude |
| `backend/app/ml.py` | **IA** | Carga perezosa de artefactos `.joblib` generada con Claude |
| `backend/app/routers/olap.py` | **IA** | Endpoints `/olap/*` generados con Claude |
| `backend/app/routers/predict.py` | **Mixto** | Endpoints generados con Claude; los contratos de entrada/salida (las 6 *features* de la solicitud) los definió el autor |
| `frontend/src/pages/` (4 pantallas) | **Mixto** | Componentes React generados con Claude según los wireframes y el flujo de pantallas definidos por el autor |
| `frontend/src/components/` | **IA** | Layout y componentes de estado (carga/error/vacío) generados con Claude |
| `frontend/src/api/client.js` | **IA** | Cliente `fetch` hacia la API generado con Claude |
| `frontend/src/utils/format.js` | **IA** | Utilidades de formato generadas con Claude |

---

### Pruebas e infraestructura

| Artefacto | Autoría | Detalle |
|---|---|---|
| `backend/tests/test_api.py` | **Mixto** | Pruebas de humo generadas con Claude; el autor definió qué endpoints y casos cubrir y verificó los 9/9 resultados |
| `backend/requirements.txt` | **Mixto** | Generado con Claude; el autor fijó las versiones (`scikit-learn==1.8.0`, `numpy==2.4.4`, `pandas==3.0.3`) para garantizar la compatibilidad de los `.joblib` |
| `frontend/package.json` | **IA** | Dependencias del frontend generadas con Claude |
| `docker-compose.yml` | **IA** | Orquestación backend + frontend generada con Claude |
| `backend/Dockerfile`, `frontend/Dockerfile` | **IA** | Generados con Claude |

---

### Documentación

| Artefacto | Autoría | Detalle |
|---|---|---|
| `README.md` | **Mixto** | Estructura generada con Claude; pasos de reproducción verificados manualmente por el autor |
| Reporte técnico (PDF) | **Mixto** | Estructura, maquetación LaTeX y redacción inicial generadas con Claude a partir del contenido y las decisiones del autor; contenido, criterio, voz y revisión final del autor, que puede explicar cada parte |
| Este archivo (`AI_USAGE.md`) | **Mixto** | Plantilla generada con Claude; contenido declarado honestamente por el autor |

---

## Herramientas de IA utilizadas

- **Claude (Anthropic)** — diseño del sistema, generación de código de backend, frontend e infraestructura, y redacción de la documentación a partir del contenido del autor
- **GitHub Copilot** — autocompletado durante la escritura de código en VSCode

---

## Declaración

Las decisiones del núcleo de minería de datos — EDA, diseño del warehouse, decisiones de modelado,
elección de métricas y manejo de fuga de datos — las tomó el autor y puede explicarlas. El código que
las implementa, incluido el de los notebooks (`01_eda`, `02_preprocessing`, `03_modeling`), se generó
con asistencia de IA a partir de esas decisiones; el autor lo revisó, lo comprende y puede defender cada
decisión técnica reflejada en él. El uso de IA se concentró en generar ese código y el andamiaje de la
aplicación (API, frontend, infraestructura), así como en la redacción de la documentación a partir del
contenido del autor, conforme a la política del curso.