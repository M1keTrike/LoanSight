# AI_USAGE.md — LoanSight

Declaración de uso de inteligencia artificial por componente,  
según la política del curso (Sección 8 del enunciado).

---

## Criterio de clasificación

| Categoría | Descripción |
|---|---|
| **IA** | Generado principalmente con asistencia de IA (Claude) |
| **Propio** | Escrito y comprendido por el autor; puede haberse usado IA para sugerencias menores |
| **Mixto** | IA generó el andamiaje; el autor tomó las decisiones de fondo y puede explicarlas |

---

## Por componente

### Capa de datos — Warehouse (DuckDB)

| Artefacto | Autoría | Detalle |
|---|---|---|
| Diseño del esquema estrella | **Propio** | Decisión de qué variables se convierten en dimensiones y cuáles en hechos, justificada en el reporte |
| `scripts/build_warehouse.py` | Mixto | Estructura del script generada con Claude; lógica de carga y tipado revisada y ajustada manualmente |
| `backend/app/warehouse/schema.py` | Mixto | DDL generado con Claude; nombres de tablas y columnas decididos por el autor |
| `backend/app/warehouse/queries.py` | Mixto | Plantillas SQL generadas con Claude; parámetros y agregaciones definidos por el autor |

---

### Capa de análisis — EDA y preprocesamiento

| Artefacto | Autoría | Detalle |
|---|---|---|
| `notebooks/01_eda.ipynb` | **Propio** | Análisis exploratorio realizado por el autor; las decisiones de qué observar y qué concluir son propias |
| `notebooks/02_preprocessing.ipynb` | **Propio** | Decisiones de imputación, encoding y escalado tomadas por el autor con base en el EDA |
| `backend/app/preprocessing/pipeline.py` | Mixto | Código del `ColumnTransformer` generado con Claude a partir de las decisiones del notebook |

---

### Capa de modelado

| Artefacto | Autoría | Detalle |
|---|---|---|
| Selección de algoritmos y métricas | **Propio** | Decisión de qué algoritmos comparar, qué métricas son apropiadas dado el desbalanceo, y por qué |
| `notebooks/03_modeling.ipynb` | **Propio** | Experimentos, comparaciones y análisis de resultados realizados por el autor |
| `backend/app/models/train.py` | Mixto | Código de serialización generado con Claude; hiperparámetros y lógica de validación definidos por el autor |

---

### Capa de presentación — API y Frontend

| Artefacto | Autoría | Detalle |
|---|---|---|
| `backend/app/main.py` | **IA** | Generado con Claude |
| `backend/app/routers/olap.py` | **IA** | Generado con Claude |
| `backend/app/routers/predict.py` | **IA** | Generado con Claude; contratos de entrada/salida definidos por el autor |
| `frontend/src/pages/` (4 pantallas) | **IA** | Componentes React generados con Claude según wireframes del autor |
| `frontend/src/api/client.js` | **IA** | Generado con Claude |
| `docker-compose.yml` | **IA** | Generado con Claude |
| `Dockerfiles` | **IA** | Generados con Claude |

---

### Documentación

| Artefacto | Autoría | Detalle |
|---|---|---|
| `README.md` | Mixto | Estructura generada con Claude; pasos de reproducción verificados manualmente por el autor |
| Reporte técnico (PDF) | Mixto(Estructura por IA, redacción por autor) | Escrito íntegramente por el autor |
| Este archivo (`AI_USAGE.md`) | Mixto | Plantilla generada con Claude; contenido declarado honestamente por el autor |

---

## Herramientas de IA utilizadas

- **Claude (Anthropic)** — diseño del sistema, generación de código de backend, frontend e infraestructura
- **GitHub Copilot** — autocompletado durante la escritura de código en VSCode

---

## Declaración

El núcleo de minería de datos de este proyecto — EDA, diseño del warehouse, decisiones de modelado,
elección de métricas y manejo de fuga de datos — fue realizado y puede ser explicado por el autor.
El uso de IA se limitó al andamiaje de la aplicación, conforme a la política del curso.