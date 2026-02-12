from fastapi import APIRouter, HTTPException, Depends
from app.types import ConnectRequest, ConnectResponse, ChatRequest, ChatResponse, SchemaResponse, UserContext
from app.db.manager import db_manager
from app.db.introspect import build_catalog, reflect_metadata
from app.core.chat_engine import handle_message
from app.core.context import get_user_context
from app.config import settings

router = APIRouter()
_catalog_by_session = {}
_metadata_by_session = {}

@router.post("/connect", response_model=ConnectResponse)
def connect(req: ConnectRequest):
    try:
        engine = db_manager.connect(req.session_id, req.db_url)
        catalog = build_catalog(engine)
        metadata = reflect_metadata(engine, catalog["exposed_tables"])

        _catalog_by_session[req.session_id] = catalog
        _metadata_by_session[req.session_id] = metadata

        return ConnectResponse(status="connected", exposed_tables=catalog["exposed_tables"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/schema", response_model=SchemaResponse)
def schema(session_id: str):
    if session_id not in _catalog_by_session:
        raise HTTPException(status_code=400, detail="Not connected. Call /connect first.")
    cat = _catalog_by_session[session_id]
    return SchemaResponse(session_id=session_id, exposed_tables=cat["exposed_tables"], tables=cat["tables"])

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user_context: UserContext = Depends(get_user_context)):
    try:
        engine = db_manager.get_engine(req.session_id)
        catalog = _catalog_by_session.get(req.session_id)
        metadata = _metadata_by_session.get(req.session_id)

        if not catalog or not metadata:
            raise HTTPException(status_code=400, detail="Not connected. Call /connect first.")

        out = handle_message(req.session_id, req.message, engine, catalog, metadata, user_context=user_context.model_dump() if user_context else None)
        return ChatResponse(session_id=req.session_id, reply=out["reply"], data=out["data"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
