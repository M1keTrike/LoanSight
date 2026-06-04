from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SAMPLE_LOAN = {
    "loan_amnt": 15000,
    "term": 36,
    "annual_inc": 65000,
    "dti": 18.4,
    "emp_length": 5,
    "purpose": "debt_consolidation",
}

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"

def test_dimensions():
    r = client.get("/olap/dimensions")
    assert r.status_code == 200
    names = {d["name"] for d in r.json()["dimensions"]}
    assert {"grado", "proposito", "estado", "empleo", "tiempo"} <= names

def test_olap_query_default_rate_by_grade():
    r = client.get("/olap/query", params={
        "dimension": "grado", "metric": "default_rate",
        "year_from": 2015, "year_to": 2018,
    })
    assert r.status_code == 200
    rows = r.json()["rows"]

    assert len(rows) == 7
    by_grade = {row["dimension_value"]: row["metric_value"] for row in rows}
    assert by_grade["A"] < by_grade["G"]

def test_olap_query_invalid_dimension():
    r = client.get("/olap/query", params={"dimension": "xxx", "metric": "loan_count"})
    assert r.status_code == 400

def test_kpis():
    r = client.get("/olap/kpis", params={"year_from": 2015, "year_to": 2018})
    assert r.status_code == 200
    body = r.json()
    assert body["total_loans"] > 0
    assert 0.0 <= body["default_rate"] <= 1.0

def test_predict_classification():
    r = client.post("/predict/classification", json=SAMPLE_LOAN)
    assert r.status_code == 200
    body = r.json()
    assert body["prediction"] in {"Fully Paid", "Charged Off"}
    assert 0.0 <= body["probability_default"] <= 1.0
    assert body["model"]

def test_predict_regression():
    r = client.post("/predict/regression", json=SAMPLE_LOAN)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 < body["predicted_int_rate"] < 100.0

def test_predict_validation_error():
    bad = dict(SAMPLE_LOAN, loan_amnt=-5)
    r = client.post("/predict/classification", json=bad)
    assert r.status_code == 422

def test_model_metrics():
    r = client.get("/models/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "classification" in body and "regression" in body
    assert body["classification"]["best_model"]
