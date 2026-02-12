import re
from typing import Any, Dict, List, Optional

# Phase-1 guardrails (read-only)
MAX_SELECT_ROWS = 100
DEFAULT_LIMIT = 25

DEFAULT_BLOCK_PATTERNS = [
    r"^alembic_version$",
    r"^flyway_schema_history$",
    r"^django_migrations$",
    r".*password.*",
    r".*secret.*",
    r".*token.*",
    r".*credential.*",
    r".*session.*",
    r"^auth_.*",
    r"^users?$",  # Often sensitive, usually has pii/auth data
]

def is_blocked_table(table_name: str, patterns: List[str] = DEFAULT_BLOCK_PATTERNS) -> bool:
    for pat in patterns:
        if re.match(pat, table_name, flags=re.IGNORECASE):
            return True
    return False

def clamp_limit(limit: Optional[int]) -> int:
    if not limit:
        return DEFAULT_LIMIT
    return max(1, min(int(limit), MAX_SELECT_ROWS))

def forbid_write_ops(user_message: str) -> None:
    # Lightweight safety net (real enforcement is in planner/executor)
    banned = ["delete ", "drop ", "truncate "]
    msg = user_message.strip().lower()
    if any(b in msg for b in banned):
        raise ValueError("DELETE/DROP/TRUNCATE operations are not allowed.")

# Phase 7: Write operation guardrails
MAX_UPDATE_ROWS = 100
SYSTEM_COLUMNS = {"id", "created_at", "updated_at", "created_by", "updated_by"}

def validate_update_filters(filters: List[dict]) -> None:
    """Ensure UPDATE has filters to prevent mass updates"""
    if not filters or len(filters) == 0:
        raise ValueError("UPDATE requires WHERE filters. Mass updates are not allowed.")

def is_system_column(col_name: str) -> bool:
    """Check if column is a system/protected column"""
    return col_name.lower() in SYSTEM_COLUMNS
