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
        
        # Phase 2: Filter out tables without a primary key
        if not pk_cols:
            continue

        indexes = insp.get_indexes(t) or []
        fks = insp.get_foreign_keys(t) or []

        
        # Phase 3: Infer conversational form metadata
        # 1. create_fields: required for INSERT (non-nullable, no default, not PK)
        create_fields = []
        for c in cols:
            name = c["name"]
            if name in pk_cols:
                continue
            # Logic: if nullable=False and default is None, user MUST provide it.
            # (In SQLAlchemy, default=None means no server default, verify autoincrement context though)
            # We treat 'autoincrement' usually for PKs. 
            if not c.get("nullable", True) and c.get("default") is None:
                # Also exclude system columns if any passed through guards (e.g. created_at handled by DB?)
                # For now, strict rule: if DB says not null & no default -> user must give it.
                create_fields.append(name)

        # 2. updateable_fields: everything except PK and audit columns
        update_fields = []
        audit_cols = ["created_at", "created_by", "updated_at", "updated_by"]
        for c in cols:
            name = c["name"]
            if name in pk_cols or name in audit_cols:
                continue
            update_fields.append(name)

        # 3. filterable_fields: PKs + indexed columns + common descriptors
        # Start with PKs
        filter_candidates = set(pk_cols)
        # Add indexed columns
        for idx in indexes:
            for cname in idx.get("column_names", []):
                # sometimes column_names might be None or expressions, skip if not string
                if isinstance(cname, str):
                    filter_candidates.add(cname)
        
        # Add common business keys
        common_keys = ["status", "type", "category", "email", "name", "date", "created_at"]
        for c in cols:
             name = c["name"]
             if any(k in name.lower() for k in common_keys):
                 filter_candidates.add(name)
        
        # 4. read_fields: PKs + first 5-6 interesting columns
        # Start with PK
        read_fields = list(pk_cols)
        # Fill up to 8 columns total
        for c in cols:
            if len(read_fields) >= 8:
                break
            name = c["name"]
            if name not in read_fields:
                read_fields.append(name)


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
            "foreign_keys": [
                {
                    "constrained_columns": fk.get("constrained_columns", []),
                    "referred_schema": fk.get("referred_schema"),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns", []),
                }
                for fk in fks
            ],
            # Phase 3 Fields
            "create_fields": create_fields,
            "update_fields": update_fields,
            "filter_fields": list(filter_candidates),
            "read_fields": read_fields,
        }
        exposed.append(t)

    return {"tables": tables, "exposed_tables": exposed}

def reflect_metadata(engine: Engine, exposed_tables: List[str]) -> MetaData:
    md = MetaData()
    md.reflect(bind=engine, only=exposed_tables)
    return md
