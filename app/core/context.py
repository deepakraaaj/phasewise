import base64
import json
from typing import Optional
from fastapi import Header, HTTPException
from pydantic import ValidationError
from app.types import UserContext

def get_user_context(x_user_context: Optional[str] = Header(None)) -> Optional[UserContext]:
    """
    Decodes the x-user-context header (base64 encoded JSON)
    and returns a UserContext object.
    
    In development mode, this allows injecting user identity.
    WARNING: Unsecured. Phase 10 will replace this with signed tokens.
    """
    if not x_user_context:
        return None

    try:
        decoded_bytes = base64.b64decode(x_user_context)
        decoded_str = decoded_bytes.decode('utf-8')
        data = json.loads(decoded_str)
        return UserContext(**data)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid x-user-context header: {str(e)}")
