from sqlalchemy import inspect, MetaData
from sqlalchemy.engine import Engine
from typing import Any, Dict, List, Tuple
from app.db.guards import is_blocked_table

def build_catalog(engine: Engine) -> Dict[str, Any]:
    """
    Build an "exposed schema catalog" used to ground the LLM and whitelist execution.
    """
    insp = inspect(engine)
    table_names = insp.get_table_names()

    tables: Dict[str, Any] = {}
    exposed: List[str] = []

    for t in table_names:
        if is_blocked_table(t):
            continue

        cols = insp.get_columns(t)
        pk = insp.get_pk_constraint(t) or {}
        pk_cols = pk.get("constrained_columns", []) if pk else []
        indexes = insp.get_indexes(t) or []

        tables[t] = {
            "table": t,
            "primary_key": pk_cols,
            "columns": [
                {
                    "name": c["name"],
                    "type": str(c["type"]),
                    "nullable": bool(c.get("nullable", True)),
                    "default": c.get("default"),
                }
                for c in cols
            ],
            "indexes": [
                {"name": i.get("name"), "column_names": i.get("column_names", [])}
                for i in indexes
            ],
        }
        exposed.append(t)

    return {"tables": tables, "exposed_tables": exposed}

def reflect_metadata(engine: Engine, exposed_tables: List[str]) -> MetaData:
    md = MetaData()
    md.reflect(bind=engine, only=exposed_tables)
    return md
