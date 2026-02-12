def detect_intent_prompt(exposed_tables: list[str]) -> str:
    return f"""
You are an admin database assistant for a transactional application.

PHASE-1 RULES:
- You must support READ only (SELECT).
- If user asks to create/update/delete, set intent accordingly, but the system will refuse.
- Choose entity ONLY from this list: {exposed_tables}

Return JSON ONLY:
{{
  "intent": "read|create|update|delete|cancel|unknown",
  "entity": "one_of_exposed_tables_or_null"
}}
"""

def read_plan_prompt(entity_profile: dict) -> str:
    return f"""
You are a database planning assistant.

RULES:
- Output a READ plan ONLY (no SQL).
- Use only columns that exist in the table profile.
- If user asks for "all", prefer a few key columns unless they insist.
- Keep LIMIT <= 100.
- Filters must use existing columns.
- If you cannot confidently decide entity or required filters, return an empty filters list.

TABLE PROFILE:
{entity_profile}

Return JSON ONLY:
{{
  "entity": "<table>",
  "columns": ["col1","col2"] | null,
  "filters": [{{"field":"...","op":"=","value":"..."}}],
  "order_by": "column_or_null",
  "order_dir": "asc|desc",
  "limit": 25
}}
"""
