from typing import Any, Dict, List, Optional

def format_table(rows: List[Dict[str, Any]], columns: List[str]) -> Dict[str, Any]:
    return {
        "type": "table",
        "columns": columns,
        "rows": [[r.get(c) for c in columns] for r in rows],
        "count": len(rows),
    }

def short_preview(rows: List[Dict[str, Any]], columns: List[str], max_rows: int = 5) -> str:
    if not rows:
        return "No rows found."
    head = rows[:max_rows]
    lines = []
    lines.append("Preview:")
    lines.append(" | ".join(columns))
    for r in head:
        lines.append(" | ".join([str(r.get(c, "")) for c in columns]))
    if len(rows) > max_rows:
        lines.append(f"...and {len(rows) - max_rows} more rows.")
    return "\n".join(lines)
