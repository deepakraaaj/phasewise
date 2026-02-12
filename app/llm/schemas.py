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

class CreatePlanOut(BaseModel):
    entity: str = Field(..., description="Table name")
    fields: Dict[str, Any] = Field(..., description="Key-value pairs to insert")

class UpdatePlanOut(BaseModel):
    entity: str = Field(..., description="Table name")
    fields: Dict[str, Any] = Field(..., description="Key-value pairs to update")
    filters: List[FilterOut] = Field(..., description="Filters to identify rows to update (WHERE clause)")
