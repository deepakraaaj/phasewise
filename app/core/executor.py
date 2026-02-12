from typing import Any, Dict, List, Optional
from sqlalchemy import MetaData, Table, select, asc, desc
from sqlalchemy.engine import Engine
from app.db.guards import clamp_limit

ALLOWED_OPS = {"read"}

def _apply_filters(stmt, table: Table, filters: list[dict]):

    for f in filters:
        col_name = f["field"]
        op = f["op"]
        val = f["value"]

        if col_name not in table.c:
            continue

        col = table.c[col_name]

        if op == "=":
            stmt = stmt.where(col == val)
        elif op == "!=":
            stmt = stmt.where(col != val)
        elif op == ">":
            stmt = stmt.where(col > val)
        elif op == ">=":
            stmt = stmt.where(col >= val)
        elif op == "<":
            stmt = stmt.where(col < val)
        elif op == "<=":
            stmt = stmt.where(col <= val)
        elif op in ("like", "ilike"):
            # simple pattern support
            pattern = str(val)
            stmt = stmt.where(col.ilike(pattern) if op == "ilike" else col.like(pattern))
        elif op == "in":
            if isinstance(val, list) and len(val) > 0:
                stmt = stmt.where(col.in_(val))
    return stmt

def run_read(engine: Engine, metadata: MetaData, entity: str, columns: Optional[list[str]], filters: list[dict], order_by: Optional[str], order_dir: str, limit: Optional[int]) -> List[Dict[str, Any]]:
    if entity not in metadata.tables:
        raise ValueError("Unknown entity/table (not exposed).")

    table = metadata.tables[entity]

    # column selection
    if columns:
        safe_cols = [c for c in columns if c in table.c]
        if not safe_cols:
            safe_cols = [c.name for c in list(table.c)[:8]]
    else:
        # default: PK + first columns (reasonable)
        pk_cols = [c for c in table.primary_key.columns]
        picked = [c.name for c in pk_cols] + [c.name for c in list(table.c) if c.name not in [p.name for p in pk_cols]]
        safe_cols = picked[:8]

    stmt = select(*[table.c[c] for c in safe_cols])

    # filters
    stmt = _apply_filters(stmt, table, filters)

    # order
    if order_by and order_by in table.c:
        stmt = stmt.order_by(asc(table.c[order_by]) if order_dir == "asc" else desc(table.c[order_by]))

    # limit
    stmt = stmt.limit(clamp_limit(limit))

    with engine.connect() as conn:
        res = conn.execute(stmt)
        return [dict(r._mapping) for r in res]
