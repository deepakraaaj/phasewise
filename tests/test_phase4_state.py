import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.state_manager import state_manager
from app.state_store import state_store

def test_phase4_state():
    session_id = "test_session_123"
    
    # 1. Clear start
    state_manager.clear_state(session_id)
    state = state_manager.get_state(session_id)
    assert state.intent == "unknown", "Initial state intent should be unknown"
    assert state.stage == "idle", "Initial state stage should be idle"

    # 2. Update State
    print("Updating state...")
    new_state = state_manager.update_state(session_id, intent="create", entity="users", stage="collecting")
    assert new_state.intent == "create"
    assert new_state.entity == "users"
    assert new_state.stage == "collecting"

    # 3. Verify Persistence
    print("Verifying persistence...")
    # Re-fetch from manager
    fetched_state = state_manager.get_state(session_id)
    assert fetched_state.entity == "users"
    
    # Verify raw store
    raw = state_store.get(f"state:{session_id}")
    assert raw is not None
    assert raw["entity"] == "users"

    # 4. Update Draft Payload
    print("Updating draft payload...")
    draft = {"username": "alice", "email": "alice@example.com"}
    state_manager.update_state(session_id, draft_payload=draft)
    
    s = state_manager.get_state(session_id)
    assert s.draft_payload == draft
    assert s.entity == "users", "Entity should persist"

    # 5. Clear State
    print("Clearing state...")
    state_manager.clear_state(session_id)
    final_state = state_manager.get_state(session_id)
    assert final_state.intent == "unknown"
    assert final_state.draft_payload == {}

    print("✅ Phase 4 State Management Verification Passed!")

if __name__ == "__main__":
    test_phase4_state()
