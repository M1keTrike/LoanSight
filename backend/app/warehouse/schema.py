from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "processed" / "loansight.duckdb"

def get_db_path() -> str:
    return os.environ.get("DB_PATH", str(DEFAULT_DB_PATH))

DDL_STATEMENTS: list[str] = [

    """
    CREATE TABLE IF NOT EXISTS DIM_TIEMPO (
        tiempo_sk   INTEGER PRIMARY KEY,
        anio        INTEGER NOT NULL,
        mes         INTEGER NOT NULL,
        anio_mes    VARCHAR NOT NULL   -- 'YYYY-MM' para etiquetas
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS DIM_GRADO (
        grado_sk    INTEGER PRIMARY KEY,
        grade       VARCHAR NOT NULL   -- 'A' .. 'G'
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS DIM_PROPOSITO (
        proposito_sk INTEGER PRIMARY KEY,
        purpose      VARCHAR NOT NULL   -- 'debt_consolidation', 'credit_card', ...
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS DIM_ESTADO (
        estado_sk   INTEGER PRIMARY KEY,
        addr_state  VARCHAR NOT NULL   -- 'CA', 'NY', 'TX', ...
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS DIM_EMPLEO (
        empleo_sk        INTEGER PRIMARY KEY,
        emp_length_label VARCHAR NOT NULL,  -- '< 1 year', '5 years', '10+ years', 'n/a'
        emp_length_years INTEGER            -- 0..10, NULL si 'n/a'
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS FACT_LOANS (
        loan_sk      BIGINT PRIMARY KEY,
        loan_id      VARCHAR,
        -- Claves foráneas hacia las dimensiones
        tiempo_sk    INTEGER REFERENCES DIM_TIEMPO(tiempo_sk),
        grado_sk     INTEGER REFERENCES DIM_GRADO(grado_sk),
        proposito_sk INTEGER REFERENCES DIM_PROPOSITO(proposito_sk),
        estado_sk    INTEGER REFERENCES DIM_ESTADO(estado_sk),
        empleo_sk    INTEGER REFERENCES DIM_EMPLEO(empleo_sk),
        -- Medidas (hechos numéricos)
        loan_amnt    DOUBLE,
        funded_amnt  DOUBLE,
        int_rate     DOUBLE,
        installment  DOUBLE,
        annual_inc   DOUBLE,
        dti          DOUBLE,
        term_months  INTEGER,
        fico_low     INTEGER,
        fico_high    INTEGER,
        -- Atributos degenerados / objetivo
        loan_status  VARCHAR,
        is_default   INTEGER   -- 1 = Charged Off, 0 = Fully Paid, NULL = en curso
    );
    """,
]

DIMENSIONS = ["DIM_TIEMPO", "DIM_GRADO", "DIM_PROPOSITO", "DIM_ESTADO", "DIM_EMPLEO"]
FACT_TABLE = "FACT_LOANS"
ALL_TABLES = [FACT_TABLE] + DIMENSIONS

def create_schema(con) -> None:
    for stmt in DDL_STATEMENTS:
        con.execute(stmt)

def drop_all(con) -> None:

    con.execute(f"DROP TABLE IF EXISTS {FACT_TABLE};")
    for dim in DIMENSIONS:
        con.execute(f"DROP TABLE IF EXISTS {dim};")
