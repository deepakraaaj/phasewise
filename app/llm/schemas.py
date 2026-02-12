from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

Intent = Literal["read", "create", "update", "delete", "cancel", "unknown"]

class DetectIntentOut(BaseModel):
    intent: Intent
    entity: Optional[str] = Field(default=None, description="Must be one of exposed_tables when intent=read")

class FilterOut(BaseModel):
    field: str
    op: Literal["=", "!=", ">", ">=", "<", "<=", "like", "ilike", "in"]
    value: Any

class ReadPlanOut(BaseModel):
    entity: str = Field(..., description="Table name")
    columns: Optional[List[str]] = Field(default=None, description="Optional list of columns to return")
    filters: List[FilterOut] = Field(default_factory=list)
    order_by: Optional[str] = Field(default=None, description="Column to sort by")
    order_dir: Literal["asc", "desc"] = "desc"
    limit: Optional[int] = 25
