from __future__ import annotations

from pathlib import Path

import duckdb

from .warehouse.schema import get_db_path

_connection: duckdb.DuckDBPyConnection | None = None

def _ensure_connection() -> duckdb.DuckDBPyConnection:
    global _connection
    if _connection is None:
        db_path = get_db_path()
        if not Path(db_path).exists():
            raise FileNotFoundError(
                f"Warehouse no encontrado en {db_path}. "
                "Ejecuta: python scripts/build_warehouse.py"
            )
        _connection = duckdb.connect(db_path, read_only=True)
    return _connection

def get_cursor() -> duckdb.DuckDBPyConnection:
    return _ensure_connection().cursor()

def warehouse_available() -> bool:
    return Path(get_db_path()).exists()
