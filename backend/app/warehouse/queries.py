from __future__ import annotations

from typing import Any

ALLOWED_DIMENSIONS: dict[str, dict[str, str]] = {
    "grado": {
        "table": "DIM_GRADO", "sk": "grado_sk",
        "label_col": "grade", "order_by": "grade",
        "title": "Grado del préstamo",
    },
    "proposito": {
        "table": "DIM_PROPOSITO", "sk": "proposito_sk",
        "label_col": "purpose", "order_by": "purpose",
        "title": "Propósito del préstamo",
    },
    "estado": {
        "table": "DIM_ESTADO", "sk": "estado_sk",
        "label_col": "addr_state", "order_by": "addr_state",
        "title": "Estado geográfico",
    },
    "empleo": {
        "table": "DIM_EMPLEO", "sk": "empleo_sk",
        "label_col": "emp_length_label", "order_by": "emp_length_years NULLS LAST",
        "title": "Antigüedad laboral",
    },
    "tiempo": {
        "table": "DIM_TIEMPO", "sk": "tiempo_sk",
        "label_col": "anio", "order_by": "anio",
        "title": "Año de emisión",
    },
}

ALLOWED_METRICS: dict[str, dict[str, Any]] = {
    "default_rate": {
        "expr": "AVG(f.is_default)", "completed_only": True,
        "title": "Tasa de default", "format": "percent",
    },
    "avg_int_rate": {
        "expr": "AVG(f.int_rate)", "completed_only": False,
        "title": "Tasa de interés promedio", "format": "percent_points",
    },
    "loan_count": {
        "expr": "COUNT(*)", "completed_only": False,
        "title": "Número de préstamos", "format": "integer",
    },
    "total_funded": {
        "expr": "SUM(f.funded_amnt)", "completed_only": False,
        "title": "Monto total financiado", "format": "currency",
    },
    "avg_loan_amnt": {
        "expr": "AVG(f.loan_amnt)", "completed_only": False,
        "title": "Monto promedio del préstamo", "format": "currency",
    },
}

class OlapError(ValueError):
    pass

def _validate(dimension: str, metric: str) -> None:
    if dimension not in ALLOWED_DIMENSIONS:
        raise OlapError(
            f"Dimensión '{dimension}' no válida. "
            f"Opciones: {sorted(ALLOWED_DIMENSIONS)}"
        )
    if metric not in ALLOWED_METRICS:
        raise OlapError(
            f"Métrica '{metric}' no válida. "
            f"Opciones: {sorted(ALLOWED_METRICS)}"
        )

def build_olap_sql(
    dimension: str, metric: str,
    year_from: int | None = None, year_to: int | None = None,
) -> tuple[str, list[Any]]:
    _validate(dimension, metric)
    dim = ALLOWED_DIMENSIONS[dimension]
    met = ALLOWED_METRICS[metric]

    where: list[str] = []
    params: list[Any] = []
    if met["completed_only"]:
        where.append("f.is_default IS NOT NULL")
    if year_from is not None:
        where.append("t.anio >= ?")
        params.append(year_from)
    if year_to is not None:
        where.append("t.anio <= ?")
        params.append(year_to)
    where_clause = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
        SELECT
            d.{dim['label_col']}      AS dimension_value,
            {met['expr']}             AS metric_value,
            COUNT(*)                  AS loan_count
        FROM FACT_LOANS f
        JOIN {dim['table']} d ON f.{dim['sk']} = d.{dim['sk']}
        JOIN DIM_TIEMPO     t ON f.tiempo_sk   = t.tiempo_sk
        {where_clause}
        GROUP BY d.{dim['label_col']}, d.{dim['order_by'].split()[0]}
        ORDER BY d.{dim['order_by']}
    """
    return sql, params

def run_olap_query(
    con, dimension: str, metric: str,
    year_from: int | None = None, year_to: int | None = None,
) -> list[dict[str, Any]]:
    sql, params = build_olap_sql(dimension, metric, year_from, year_to)
    rows = con.execute(sql, params).fetchall()
    out = []
    for value, metric_value, count in rows:
        out.append({
            "dimension_value": str(value),
            "metric_value": None if metric_value is None else float(metric_value),
            "loan_count": int(count),
        })
    return out

def get_dimensions(con) -> list[dict[str, Any]]:
    result = []
    for name, dim in ALLOWED_DIMENSIONS.items():
        values = con.execute(
            f"SELECT DISTINCT {dim['label_col']} AS v "
            f"FROM {dim['table']} ORDER BY {dim['order_by']}"
        ).fetchall()
        result.append({
            "name": name,
            "title": dim["title"],
            "values": [str(v[0]) for v in values],
        })
    return result

def get_metrics() -> list[dict[str, Any]]:
    return [
        {"name": name, "title": m["title"], "format": m["format"]}
        for name, m in ALLOWED_METRICS.items()
    ]

def get_year_range(con) -> dict[str, int]:
    row = con.execute("SELECT MIN(anio), MAX(anio) FROM DIM_TIEMPO").fetchone()
    return {"min": int(row[0]), "max": int(row[1])}

def get_kpis(con, year_from: int | None = None, year_to: int | None = None) -> dict[str, Any]:
    where: list[str] = []
    params: list[Any] = []
    if year_from is not None:
        where.append("t.anio >= ?")
        params.append(year_from)
    if year_to is not None:
        where.append("t.anio <= ?")
        params.append(year_to)
    where_clause = ("WHERE " + " AND ".join(where)) if where else ""

    row = con.execute(f"""
        SELECT
            COUNT(*)                                          AS total_loans,
            SUM(f.funded_amnt)                                AS total_funded,
            AVG(f.int_rate)                                   AS avg_int_rate,
            AVG(f.loan_amnt)                                  AS avg_loan_amnt,
            COUNT(*) FILTER (WHERE f.is_default IS NOT NULL)  AS completed_loans,
            AVG(f.is_default)                                 AS default_rate
        FROM FACT_LOANS f
        JOIN DIM_TIEMPO t ON f.tiempo_sk = t.tiempo_sk
        {where_clause}
    """, params).fetchone()

    return {
        "total_loans": int(row[0] or 0),
        "total_funded": float(row[1] or 0.0),
        "avg_int_rate": float(row[2] or 0.0),
        "avg_loan_amnt": float(row[3] or 0.0),
        "completed_loans": int(row[4] or 0),
        "default_rate": float(row[5] or 0.0),
    }
