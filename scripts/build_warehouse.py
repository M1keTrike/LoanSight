from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import duckdb

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.warehouse.schema import create_schema, drop_all, get_db_path

RAW_CSV = REPO_ROOT / "data" / "raw" / "accepted_2007_to_2018Q4.csv.gz"

STAGING_SELECT = """
SELECT
    id                                                    AS loan_id,
    -- Tiempo: 'Dec-2015' -> año / mes (try_strptime tolera valores corruptos)
    CAST(EXTRACT(year  FROM try_strptime(issue_d, '%b-%Y')) AS INTEGER) AS anio,
    CAST(EXTRACT(month FROM try_strptime(issue_d, '%b-%Y')) AS INTEGER) AS mes,
    grade,
    purpose,
    addr_state,
    -- Antigüedad laboral: etiqueta legible + valor numérico 0..10
    COALESCE(NULLIF(emp_length, ''), 'n/a')               AS emp_length_label,
    CASE
        WHEN emp_length = '< 1 year'  THEN 0
        WHEN emp_length = '10+ years' THEN 10
        WHEN emp_length LIKE '%year%' THEN TRY_CAST(regexp_extract(emp_length, '[0-9]+') AS INTEGER)
        ELSE NULL
    END                                                   AS emp_length_years,
    -- '36 months' -> 36
    TRY_CAST(regexp_extract(term, '[0-9]+') AS INTEGER)   AS term_months,
    TRY_CAST(int_rate    AS DOUBLE)                       AS int_rate,
    TRY_CAST(loan_amnt   AS DOUBLE)                       AS loan_amnt,
    TRY_CAST(funded_amnt AS DOUBLE)                       AS funded_amnt,
    TRY_CAST(installment AS DOUBLE)                       AS installment,
    TRY_CAST(annual_inc  AS DOUBLE)                       AS annual_inc,
    TRY_CAST(dti         AS DOUBLE)                       AS dti,
    TRY_CAST(fico_range_low  AS INTEGER)                  AS fico_low,
    TRY_CAST(fico_range_high AS INTEGER)                  AS fico_high,
    loan_status,
    -- Objetivo de clasificación: 1 = default, 0 = pagado, NULL = en curso
    CASE
        WHEN loan_status = 'Charged Off' THEN 1
        WHEN loan_status = 'Fully Paid'  THEN 0
        ELSE NULL
    END                                                   AS is_default
FROM read_csv_auto(?, all_varchar=true)
"""

STAGING_WHERE = """
WHERE anio IS NOT NULL
  AND grade IS NOT NULL
  AND purpose IS NOT NULL
  AND addr_state IS NOT NULL
"""

def log(msg: str) -> None:
    print(f"[build_warehouse] {msg}", flush=True)

def build(limit: int | None = None) -> None:
    if not RAW_CSV.exists():
        raise FileNotFoundError(
            f"No se encontró el dataset en {RAW_CSV}. "
            "Descárgalo de Kaggle y colócalo en data/raw/ (ver README)."
        )

    db_path = Path(get_db_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)

    log(f"Conectando a {db_path}")
    con = duckdb.connect(str(db_path))
    t0 = time.time()

    try:
        log("Reconstruyendo esquema estrella…")
        drop_all(con)
        create_schema(con)

        limit_clause = f"LIMIT {int(limit)}" if limit else ""
        log("Cargando y limpiando CSV crudo a staging (puede tardar)…")
        con.execute("DROP TABLE IF EXISTS staging;")
        con.execute(
            f"CREATE TABLE staging AS {STAGING_SELECT} {STAGING_WHERE} {limit_clause}",
            [str(RAW_CSV)],
        )
        n = con.execute("SELECT count(*) FROM staging").fetchone()[0]
        log(f"Staging: {n:,} filas válidas")

        log("Poblando dimensiones…")
        con.execute("""
            INSERT INTO DIM_TIEMPO
            SELECT row_number() OVER (ORDER BY anio, mes) AS tiempo_sk,
                   anio, mes,
                   printf('%04d-%02d', anio, mes) AS anio_mes
            FROM (SELECT DISTINCT anio, mes FROM staging);
        """)
        con.execute("""
            INSERT INTO DIM_GRADO
            SELECT row_number() OVER (ORDER BY grade) AS grado_sk, grade
            FROM (SELECT DISTINCT grade FROM staging);
        """)
        con.execute("""
            INSERT INTO DIM_PROPOSITO
            SELECT row_number() OVER (ORDER BY purpose) AS proposito_sk, purpose
            FROM (SELECT DISTINCT purpose FROM staging);
        """)
        con.execute("""
            INSERT INTO DIM_ESTADO
            SELECT row_number() OVER (ORDER BY addr_state) AS estado_sk, addr_state
            FROM (SELECT DISTINCT addr_state FROM staging);
        """)
        con.execute("""
            INSERT INTO DIM_EMPLEO
            SELECT row_number() OVER (ORDER BY emp_length_years NULLS LAST) AS empleo_sk,
                   emp_length_label, emp_length_years
            FROM (SELECT DISTINCT emp_length_label, emp_length_years FROM staging);
        """)

        log("Poblando FACT_LOANS…")
        con.execute("""
            INSERT INTO FACT_LOANS
            SELECT
                row_number() OVER ()                       AS loan_sk,
                s.loan_id,
                t.tiempo_sk, g.grado_sk, p.proposito_sk, e.estado_sk, m.empleo_sk,
                s.loan_amnt, s.funded_amnt, s.int_rate, s.installment,
                s.annual_inc, s.dti, s.term_months, s.fico_low, s.fico_high,
                s.loan_status, s.is_default
            FROM staging s
            JOIN DIM_TIEMPO    t ON s.anio = t.anio AND s.mes = t.mes
            JOIN DIM_GRADO     g ON s.grade = g.grade
            JOIN DIM_PROPOSITO p ON s.purpose = p.purpose
            JOIN DIM_ESTADO    e ON s.addr_state = e.addr_state
            JOIN DIM_EMPLEO    m ON s.emp_length_label = m.emp_length_label;
        """)

        con.execute("DROP TABLE staging;")

        facts = con.execute("SELECT count(*) FROM FACT_LOANS").fetchone()[0]
        dims = {
            d: con.execute(f"SELECT count(*) FROM {d}").fetchone()[0]
            for d in ["DIM_TIEMPO", "DIM_GRADO", "DIM_PROPOSITO", "DIM_ESTADO", "DIM_EMPLEO"]
        }
        log(f"FACT_LOANS: {facts:,} filas")
        for d, c in dims.items():
            log(f"  {d}: {c:,}")
        log(f"Listo en {time.time() - t0:.1f}s -> {db_path}")
    finally:
        con.close()

def main() -> None:
    ap = argparse.ArgumentParser(description="Carga el warehouse LoanSight en DuckDB")
    ap.add_argument("--limit", type=int, default=None,
                    help="Cargar solo N filas (para pruebas rápidas)")
    args = ap.parse_args()
    build(limit=args.limit)

if __name__ == "__main__":
    main()
