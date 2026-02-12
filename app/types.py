from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class ConnectRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    db_url: str = Field(..., min_length=8)

class ConnectResponse(BaseModel):
    status: str
    exposed_tables: List[str]

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    data: Optional[Dict[str, Any]] = None

class SchemaResponse(BaseModel):
    session_id: str
    exposed_tables: List[str]
    tables: Dict[str, Any]
