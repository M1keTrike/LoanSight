from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from .preprocessing.pipeline import API_TO_FEATURE, MODEL_COLUMNS

ARTIFACTS_DIR = Path(__file__).resolve().parent / "models" / "artifacts"

_cache: dict[str, Any] = {}

class ArtifactsMissing(RuntimeError):
    pass

def _load_joblib(name: str):
    path = ARTIFACTS_DIR / name
    if not path.exists():
        raise ArtifactsMissing(
            f"No se encontró {name}. Ejecuta: python backend/app/models/train.py"
        )
    if name not in _cache:
        _cache[name] = joblib.load(path)
    return _cache[name]

def _load_json(name: str) -> Any:
    path = ARTIFACTS_DIR / name
    if not path.exists():
        raise ArtifactsMissing(
            f"No se encontró {name}. Ejecuta: python backend/app/models/train.py"
        )
    key = f"json:{name}"
    if key not in _cache:
        _cache[key] = json.loads(path.read_text(encoding="utf-8"))
    return _cache[key]

def get_regression_model():
    return _load_joblib("reg_model.joblib")

def get_classification_model():
    return _load_joblib("clf_model.joblib")

def get_metrics() -> dict:
    return _load_json("metrics.json")

def get_metadata() -> dict:
    return _load_json("metadata.json")

def best_model_name(task: str) -> str:
    return get_metrics()[task]["best_model"]

def artifacts_ready() -> bool:
    return (ARTIFACTS_DIR / "reg_model.joblib").exists() and \
           (ARTIFACTS_DIR / "clf_model.joblib").exists()

def features_to_frame(payload: dict) -> pd.DataFrame:
    row = {model_col: payload[api_field] for api_field, model_col in API_TO_FEATURE.items()}
    return pd.DataFrame([row])[MODEL_COLUMNS]
