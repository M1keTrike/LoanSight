# LoanSight — Análisis y Riesgo Crediticio

Pipeline full stack de minería de datos sobre el dataset Lending Club.  
Curso Minería de Datos · Ingeniería de Software · 9.º semestre · UPCh · 2026A

---

## Descripción

LoanSight es un sistema completo de análisis de riesgo crediticio que cubre:

- **Warehouse dimensional** (esquema estrella en DuckDB) con soporte OLAP
- **EDA y preprocesamiento** reproducible con scikit-learn Pipeline
- **Dos tareas de ML**: regresión (tasa de interés) y clasificación (default)
- **API REST** con FastAPI que sirve consultas OLAP e inferencia en vivo
- **Frontend React** que consume la API — no resultados precocinados

---

## Preguntas que responde

| Tarea | Pregunta | Variable objetivo |
|---|---|---|
| Regresión | ¿Cuál será la tasa de interés asignada a un préstamo? | `int_rate` |
| Clasificación | ¿Este préstamo terminará en default? | `loan_status` (Fully Paid vs. Charged Off) |

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Warehouse | DuckDB 0.10 |
| EDA / ML | Python 3.11 · pandas · scikit-learn · matplotlib · seaborn |
| Backend | FastAPI · Uvicorn · joblib |
| Frontend | React 18 · Vite · Recharts |
| Infra | Docker · Docker Compose |

---

## Estructura del repositorio

```
loansight/
├── backend/
│   ├── app/
│   │   ├── main.py               # Entrada FastAPI
│   │   ├── routers/
│   │   │   ├── olap.py           # GET /olap/query, /olap/dimensions
│   │   │   └── predict.py        # POST /predict/classification, /predict/regression
│   │   ├── warehouse/
│   │   │   ├── schema.py         # Creación del esquema estrella en DuckDB
│   │   │   └── queries.py        # Consultas OLAP parametrizadas
│   │   ├── preprocessing/
│   │   │   └── pipeline.py       # ColumnTransformer + Pipeline de sklearn
│   │   └── models/
│   │       ├── train.py          # Entrenamiento y serialización con joblib
│   │       └── artifacts/        # Modelos serializados (.joblib) — generados al entrenar
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx     # Pantalla 1 — métricas globales
│   │   │   ├── Explorer.jsx      # Pantalla 2 — explorador OLAP
│   │   │   ├── Predictor.jsx     # Pantalla 3 — predicción en vivo
│   │   │   └── Models.jsx        # Pantalla 4 — métricas de modelos
│   │   ├── components/           # Componentes reutilizables
│   │   └── api/
│   │       └── client.js         # Wrapper fetch → FastAPI
│   ├── package.json
│   └── Dockerfile
├── notebooks/
│   ├── 01_eda.ipynb              # Análisis exploratorio
│   ├── 02_preprocessing.ipynb    # Decisiones de preprocesamiento
│   └── 03_modeling.ipynb         # Entrenamiento y evaluación de modelos
├── data/
│   ├── raw/                      # Dataset original (no versionado en Git)
│   └── processed/                # Dataset limpio generado por el pipeline
├── scripts/
│   └── build_warehouse.py        # Carga datos crudos → DuckDB
├── docker-compose.yml
├── .gitignore
├── README.md                     # Este archivo
└── AI_USAGE.md
```

---

## Requisitos previos

- Docker >= 24.0 y Docker Compose >= 2.20
- Python 3.11 (solo para el paso de descarga del dataset)
- Cuenta en Kaggle (para descargar el dataset)

---

## Reproducción paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/M1keTrike/LoanSight.git
cd loansight
```

### 2. Descargar el dataset

Ve a https://www.kaggle.com/datasets/wordsforthewise/lending-club y descarga `accepted_2007_to_2018Q4.csv.gz`.  
Coloca el archivo en `data/raw/`:

```bash
mv ~/Downloads/accepted_2007_to_2018Q4.csv.gz data/raw/
```

### 3. Construir el warehouse

```bash
pip install duckdb pandas
python scripts/build_warehouse.py
```

Esto crea `data/processed/loansight.duckdb` con el esquema estrella cargado.

### 4. Entrenar los modelos

```bash
pip install -r backend/requirements.txt
python backend/app/models/train.py
```

Genera los archivos `.joblib` en `backend/app/models/artifacts/`.

### 5. Levantar la aplicación

```bash
docker compose up --build
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend (API docs) | http://localhost:8000/docs |

---

## Endpoints principales de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/olap/query` | Consulta OLAP parametrizada sobre el warehouse |
| GET | `/olap/dimensions` | Lista de dimensiones y valores disponibles |
| POST | `/predict/classification` | Predice probabilidad de default |
| POST | `/predict/regression` | Predice tasa de interés estimada |
| GET | `/models/metrics` | Métricas de evaluación de todos los modelos |

Documentación interactiva completa en `http://localhost:8000/docs`.

---

## Notas de reproducibilidad

- `random_state=42` en todos los splits y modelos.
- El pipeline de preprocesamiento se ajusta **solo sobre el conjunto de entrenamiento** (sin fuga de datos).
- Los modelos serializados incluyen el pipeline completo (transformaciones + modelo).
- Semilla fija en DuckDB para muestras reproducibles.

---

## Autor

Matrícula: `233371`  
Nombre: `Molina Gómez Miguel Ángel`  
Curso: Minería de Datos · UPCh · 2026A