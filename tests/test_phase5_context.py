import base64
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.context import get_user_context
from app.types import UserContext
from app.core.state_manager import state_manager
from app.api.routes import _catalog_by_session, _metadata_by_session

client = TestClient(app)

def test_decode_user_context():
    # Valid context
    ctx = {"user_id": "u123", "user_role": "admin", "company_id": 99}
    json_str = json.dumps(ctx)
    b64_str = base64.b64encode(json_str.encode()).decode()
    
    result = get_user_context(b64_str)
    assert result is not None
    assert result.user_id == "u123"
    assert result.user_role == "admin"
    assert result.company_id == 99

def test_decode_invalid_context():
    # Invalid base64
    with pytest.raises(Exception): # dependency raises HTTPException
        get_user_context("invalid-base64")

def test_chat_with_context(monkeypatch):
    # Setup state
    session_id = "test_phase5_session"
    
    # Mock catalog/metadata to bypass connection check
    _catalog_by_session[session_id] = {
        "exposed_tables": ["users"],
        "tables": {"users": {"columns": ["id", "name"]}}
    }
    _metadata_by_session[session_id] = "mock_metadata" 
    
    # Mock engine and chat engine to avoid actual DB calls
    monkeypatch.setattr("app.db.manager.db_manager.get_engine", lambda s: "mock_engine")
    
    # We want to verify state update, so we can check state_manager after the call
    # But chat_engine.handle_message is called by route.
    # Let's mock handle_message to just return something and check state separately?
    # Or just let it run (it might fail on run_read if we don't mock it completely).
    
    # Let's mock handle_message to avoid logic execution but verify context injection
    # Actually, we can just check if state_manager has the context after the call.
    # But handle_message does logic.
    
    # Let's mock `app.core.chat_engine.handle_message`
    # We need to ensure the route calls handle_message which calls state_manager (wait, handle_message calls state_manager update).
    # Correct.
    
    # So if we mock handle_message, we won't test the wiring inside handle_message.
    # We should stick to mocking `run_read` and `detect_intent`.
    
    monkeypatch.setattr("app.core.chat_engine.detect_intent", lambda msg, tbls: type('obj', (object,), {'intent': 'read', 'entity': 'users'})())
    monkeypatch.setattr("app.core.chat_engine.make_read_plan", lambda msg, ent, prof: type('obj', (object,), {'entity': 'users', 'columns': [], 'filters': [], 'order_by': None, 'order_dir': 'asc', 'limit': 10})())
    monkeypatch.setattr("app.core.chat_engine.run_read", lambda **kwargs: [{"id": 1, "name": "Alice"}])
    
    # Prepare header
    ctx = {"user_id": "u555", "user_role": "editor"}
    b64 = base64.b64encode(json.dumps(ctx).encode()).decode()
    
    # CALL
    response = client.post(
        "/chat",
        json={"session_id": session_id, "message": "hello"},
        headers={"x-user-context": b64}
    )
    
    assert response.status_code == 200
    
    # VERIFY STATE
    state = state_manager.get_state(session_id)
    assert state.user_context is not None
    assert state.user_context["user_id"] == "u555"
    assert state.user_context["user_role"] == "editor"
    
    print("✅ Phase 5 User Context Verification Passed!")

if __name__ == "__main__":
    # Manually run if executed as script
    try:
        test_decode_user_context()
        # test_decode_invalid_context() # verify manually or via pytest
        # test_chat_with_context() # needs monkeypatch if running raw
        pass
    except Exception as e:
        print(f"Test failed: {e}")
