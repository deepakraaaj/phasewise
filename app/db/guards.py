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
    banned = ["delete ", "drop ", "truncate ", "update ", "insert ", "alter "]
    msg = user_message.strip().lower()
    if any(b in msg for b in banned):
        raise ValueError("Phase 1 is READ-only. Writes (INSERT/UPDATE/DELETE) are disabled.")
