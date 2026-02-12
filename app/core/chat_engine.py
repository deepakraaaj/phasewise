from typing import Any, Dict
from sqlalchemy.engine import Engine
from sqlalchemy import MetaData

from app.core.state_manager import state_manager
from app.core.planner import detect_intent, make_read_plan
from app.core.executor import run_read
from app.core.formatter import format_table, short_preview

def handle_message(session_id: str, message: str, engine: Engine, catalog: Dict[str, Any], metadata: MetaData, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    # Basic protection: phase-1 is read-only
    # forbid_write_ops(message) # Relaxing this check as we now have state manager to handle intents safely

    # Update state with user context if present
    if user_context:
         state_manager.update_state(session_id, user_context=user_context)

    state = state_manager.get_state(session_id)
    exposed_tables = catalog["exposed_tables"]
    tables_info = catalog["tables"]

    # 1. Universal Commands (Rule-based)
    msg_lower = message.strip().lower()
    if msg_lower in ["cancel", "stop", "start over", "reset"]:
        state_manager.clear_state(session_id)
        return {"reply": "♻️ Conversation reset. What would you like to do?", "data": None}
    
    if msg_lower == "show draft":
        if not state.draft_payload:
            return {"reply": "No draft in progress.", "data": None}
        return {"reply": f"📝 Current Draft for {state.entity}:\n{state.draft_payload}", "data": state.draft_payload}

    # 2. Intent Detection (if idle or unknown)
    # For now, we still rely on strict phase 1 read flow, but we update state.
    # In future phases, we will use state.stage to determine if we are in a flow.
    
    if state.stage == "idle":
        intent_out = detect_intent(message, exposed_tables)
        
        # Update state with detected intent
        state = state_manager.update_state(
            session_id, 
            intent=intent_out.intent, 
            entity=intent_out.entity
        )

        if intent_out.intent == "cancel": # LLM detected cancel
             state_manager.clear_state(session_id)
             return {"reply": "Okay — cleared context.", "data": None}

    # 3. Handle Intents
    if state.intent == "read":
        # Check if entity is present
        if not state.entity:
             # Try to see if message contains entity selection if we are in a loop (not implemented yet fully)
             # For now, just ask user.
             top = exposed_tables[:12]
             return {"reply": f"Which table should I read from? Examples: {', '.join(top)}", "data": None}
        
        if state.entity not in tables_info:
             # Reset entity if invalid
             state_manager.update_state(session_id, entity=None)
             return {"reply": "That table isn’t exposed. Please pick another.", "data": None}

        # Build read plan
        # Note: In a real stateful flow, we'd check if we have filters in state.
        # For Phase 4, we just execute fresh every time for 'read' but store context.
        plan = make_read_plan(message, state.entity, tables_info[state.entity])
        
        # Execute
        try:
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
        except Exception as e:
            return {"reply": f"⚠️ Error executing query: {str(e)}", "data": None}

        columns = list(rows[0].keys()) if rows else (plan.columns or [])
        data = format_table(rows, columns) if rows else {"type": "table", "columns": columns, "rows": [], "count": 0}
        preview = short_preview(rows, columns)
        
        # Reset state after successful read (read is usually one-shot)
        # Or keep it for context? Let's keep entity for now but reset stage.
        state_manager.update_state(session_id, stage="idle")
        
        return {"reply": f"Done. {preview}", "data": data}

    # If intent is create/update (Phase 5+), we would handle it here.
    # For Phase 4, we just acknowledge receipt of state for now.
    if state.intent in ["create", "update"]:
        return {"reply": f"Detected intent '{state.intent}' for table '{state.entity}'. (Write flows coming in Phase 5)", "data": None}

    return {"reply": "I didn't understand that. Try 'show users' or 'list invoices'.", "data": None}
