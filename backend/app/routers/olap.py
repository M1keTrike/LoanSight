from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..db import get_cursor
from ..warehouse import queries as q

router = APIRouter(prefix="/olap", tags=["olap"])

@router.get("/dimensions")
def list_dimensions(con=Depends(get_cursor)):
    return {"dimensions": q.get_dimensions(con)}

@router.get("/metrics")
def list_metrics():
    return {"metrics": q.get_metrics()}

@router.get("/year-range")
def year_range(con=Depends(get_cursor)):
    return q.get_year_range(con)

@router.get("/kpis")
def kpis(
    year_from: int | None = Query(None, description="Año inicial (inclusive)"),
    year_to: int | None = Query(None, description="Año final (inclusive)"),
    con=Depends(get_cursor),
):
    return q.get_kpis(con, year_from, year_to)

@router.get("/query")
def olap_query(
    dimension: str = Query(..., description="grado | proposito | estado | empleo | tiempo"),
    metric: str = Query(..., description="default_rate | avg_int_rate | loan_count | total_funded | avg_loan_amnt"),
    year_from: int | None = Query(None),
    year_to: int | None = Query(None),
    con=Depends(get_cursor),
):
    try:
        rows = q.run_olap_query(con, dimension, metric, year_from, year_to)
    except q.OlapError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "dimension": dimension,
        "metric": metric,
        "year_from": year_from,
        "year_to": year_to,
        "rows": rows,
    }
