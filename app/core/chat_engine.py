from typing import Any, Dict
from sqlalchemy.engine import Engine
from sqlalchemy import MetaData

from app.state_store import state_store
from app.db.guards import forbid_write_ops
from app.core.planner import detect_intent, make_read_plan
from app.core.executor import run_read
from app.core.formatter import format_table, short_preview

def _session_key(session_id: str) -> str:
    return f"sess:{session_id}"

def handle_message(session_id: str, message: str, engine: Engine, catalog: Dict[str, Any], metadata: MetaData) -> Dict[str, Any]:
    # Basic protection: phase-1 is read-only
    forbid_write_ops(message)

    state = state_store.get(_session_key(session_id)) or {}

    exposed_tables = catalog["exposed_tables"]
    tables_info = catalog["tables"]

    # Detect intent/entity
    intent_out = detect_intent(message, exposed_tables)

    if intent_out.intent == "cancel":
        state_store.delete(_session_key(session_id))
        return {"reply": "Okay — cleared the current context. What do you want to view?", "data": None}

    if intent_out.intent != "read":
        return {"reply": "Phase 1 supports READ only (SELECT). I can fetch data, but writes are disabled for now.", "data": None}

    entity = intent_out.entity
    if not entity:
        # If entity not chosen, ask the user to pick
        top = exposed_tables[:12]
        return {"reply": f"Which table should I read from? Examples: {', '.join(top)}", "data": None}

    if entity not in tables_info:
        return {"reply": "That table isn’t exposed (or doesn’t exist). Try another one.", "data": None}

    # Build read plan based on entity profile + message
    plan = make_read_plan(message, entity, tables_info[entity])

    # Ensure plan.entity matches detected entity or exposed list
    if plan.entity not in exposed_tables:
        plan.entity = entity

    # Execute
    rows = run_read(
        engine=engine,
        metadata=metadata,
        entity=plan.entity,
        columns=plan.columns,
        filters=[f.model_dump() for f in plan.filters],
        order_by=plan.order_by,
        order_dir=plan.order_dir,
        limit=plan.limit,
    )

    # Choose displayed columns
    columns = list(rows[0].keys()) if rows else (plan.columns or [])
    data = format_table(rows, columns) if rows else {"type": "table", "columns": columns, "rows": [], "count": 0}

    preview = short_preview(rows, columns)
    reply = f"Done. {preview}"

    # Update state (lightweight)
    state_store.set(_session_key(session_id), {"last_entity": plan.entity})
    return {"reply": reply, "data": data}
