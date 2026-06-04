from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    roc_curve,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

THIS = Path(__file__).resolve()
BACKEND_ROOT = THIS.parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

from app.preprocessing.pipeline import (
    MODEL_COLUMNS,
    NUMERIC_FEATURES,
    ONEHOT_FEATURES,
    TARGET_CLASSIFICATION,
    TARGET_REGRESSION,
    build_model_pipeline,
)
from app.warehouse.schema import get_db_path

RANDOM_STATE = 42
ARTIFACTS_DIR = THIS.parent / "artifacts"
DEFAULT_SAMPLE = 150_000

def log(msg: str) -> None:
    print(f"[train] {msg}", flush=True)

def load_dataframe(con) -> pd.DataFrame:
    sql = """
        SELECT
            f.loan_amnt,
            f.term_months,
            f.annual_inc,
            f.dti,
            m.emp_length_years,
            p.purpose,
            g.grade,
            f.int_rate,
            f.is_default
        FROM FACT_LOANS f
        JOIN DIM_PROPOSITO p ON f.proposito_sk = p.proposito_sk
        JOIN DIM_EMPLEO    m ON f.empleo_sk    = m.empleo_sk
        JOIN DIM_GRADO     g ON f.grado_sk     = g.grado_sk
    """
    return con.execute(sql).df()

def reproducible_sample(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if len(df) <= n:
        return df
    return df.sample(n=n, random_state=RANDOM_STATE)

def train_regression(df: pd.DataFrame, sample: int) -> tuple[dict, object, str]:
    data = df.dropna(subset=[TARGET_REGRESSION]).copy()
    data = reproducible_sample(data, sample)
    X = data[MODEL_COLUMNS]
    y = data[TARGET_REGRESSION]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    log(f"Regresión: train={len(X_train):,} test={len(X_test):,}")

    candidates = {
        "LinearRegression": LinearRegression(),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100, max_depth=12, min_samples_leaf=50,
            n_jobs=-1, random_state=RANDOM_STATE
        ),
    }

    results = []
    fitted = {}
    for name, est in candidates.items():
        t0 = time.time()
        pipe = build_model_pipeline(est)
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        rmse = float(root_mean_squared_error(y_test, pred))
        mae = float(mean_absolute_error(y_test, pred))
        r2 = float(r2_score(y_test, pred))
        results.append({"model": name, "rmse": rmse, "mae": mae, "r2": r2})
        fitted[name] = pipe
        log(f"  {name}: RMSE={rmse:.3f} MAE={mae:.3f} R2={r2:.3f} ({time.time()-t0:.1f}s)")

    best = min(results, key=lambda r: r["rmse"])["model"]
    summary = {
        "target": TARGET_REGRESSION,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "best_model": best,
        "models": results,
    }
    return summary, fitted[best], best

def train_classification(df: pd.DataFrame, sample: int) -> tuple[dict, object, str]:

    data = df.dropna(subset=[TARGET_CLASSIFICATION]).copy()
    data[TARGET_CLASSIFICATION] = data[TARGET_CLASSIFICATION].astype(int)
    data = reproducible_sample(data, sample)
    X = data[MODEL_COLUMNS]
    y = data[TARGET_CLASSIFICATION]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    log(f"Clasificación: train={len(X_train):,} test={len(X_test):,} "
        f"default_rate_train={y_train.mean():.3f}")

    candidates = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "KNeighborsClassifier": KNeighborsClassifier(
            n_neighbors=25, n_jobs=-1
        ),
        "DecisionTreeClassifier": DecisionTreeClassifier(
            max_depth=8, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=120, max_depth=14, min_samples_leaf=20,
            class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE
        ),
    }

    results = []
    fitted = {}
    for name, est in candidates.items():
        t0 = time.time()
        pipe = build_model_pipeline(est)
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        proba = pipe.predict_proba(X_test)[:, 1]

        auc = float(roc_auc_score(y_test, proba))
        f1 = float(f1_score(y_test, pred))
        precision = float(precision_score(y_test, pred, zero_division=0))
        recall = float(recall_score(y_test, pred))
        acc = float(accuracy_score(y_test, pred))
        cm = confusion_matrix(y_test, pred).tolist()

        fpr, tpr, _ = roc_curve(y_test, proba)
        idx = np.linspace(0, len(fpr) - 1, num=min(100, len(fpr))).astype(int)
        roc = {"fpr": fpr[idx].round(4).tolist(), "tpr": tpr[idx].round(4).tolist()}

        results.append({
            "model": name, "auc": auc, "f1": f1, "precision": precision,
            "recall": recall, "accuracy": acc,
            "confusion_matrix": cm, "roc_curve": roc,
        })
        fitted[name] = pipe
        log(f"  {name}: AUC={auc:.3f} F1={f1:.3f} P={precision:.3f} "
            f"R={recall:.3f} Acc={acc:.3f} ({time.time()-t0:.1f}s)")

    best = max(results, key=lambda r: r["auc"])["model"]
    summary = {
        "target": TARGET_CLASSIFICATION,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "default_rate_train": float(y_train.mean()),
        "best_model": best,
        "models": results,
    }
    return summary, fitted[best], best

def build_metadata(df: pd.DataFrame) -> dict:
    purposes = sorted(df["purpose"].dropna().unique().tolist())
    num = df[NUMERIC_FEATURES].describe().to_dict()
    ranges = {
        feat: {
            "min": float(num[feat]["min"]),
            "max": float(num[feat]["max"]),
            "median": float(df[feat].median()),
        }
        for feat in NUMERIC_FEATURES
    }
    return {
        "numeric_features": NUMERIC_FEATURES,
        "onehot_features": ONEHOT_FEATURES,
        "purpose_options": purposes,
        "feature_ranges": ranges,
    }

def main() -> None:
    ap = argparse.ArgumentParser(description="Entrena los modelos de LoanSight")
    ap.add_argument("--sample", type=int, default=DEFAULT_SAMPLE,
                    help="Tamaño de muestra reproducible por tarea")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    db_path = get_db_path()
    if not Path(db_path).exists():
        raise FileNotFoundError(
            f"No existe el warehouse en {db_path}. "
            "Ejecuta primero: python scripts/build_warehouse.py"
        )

    log(f"Leyendo warehouse {db_path}")
    con = duckdb.connect(db_path, read_only=True)
    try:
        df = load_dataframe(con)
    finally:
        con.close()
    log(f"Filas totales: {len(df):,} (muestra por tarea: {args.sample:,})")

    t0 = time.time()
    reg_summary, reg_best_pipe, reg_best = train_regression(df, args.sample)
    clf_summary, clf_best_pipe, clf_best = train_classification(df, args.sample)
    metadata = build_metadata(df)

    joblib.dump(reg_best_pipe, ARTIFACTS_DIR / "reg_model.joblib")
    joblib.dump(clf_best_pipe, ARTIFACTS_DIR / "clf_model.joblib")
    log(f"Mejor regresión: {reg_best}  |  Mejor clasificación: {clf_best}")

    metrics = {
        "random_state": RANDOM_STATE,
        "sample_size": args.sample,
        "regression": reg_summary,
        "classification": clf_summary,
    }
    (ARTIFACTS_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    (ARTIFACTS_DIR / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    log(f"Artefactos en {ARTIFACTS_DIR}")
    log(f"Entrenamiento completo en {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
