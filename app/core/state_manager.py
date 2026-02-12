from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from app.state_store import state_store

# Enums / Literals
IntentType = Literal["read", "create", "update", "delete", "unknown"]
StageType = Literal["idle", "collecting", "preview", "confirm"]

class ConversationState(BaseModel):
    intent: IntentType = "unknown"
    entity: Optional[str] = None
    stage: StageType = "idle"
    draft_payload: Dict[str, Any] = Field(default_factory=dict)
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    user_context: Optional[Dict[str, Any]] = None
    # Could add more context like:
    # missing_fields: List[str] = []

class StateManager:
    """
    Manages the conversation state on top of the raw state_store.
    Ensures type safety and structured updates using ConversationState Pydantic model.
    """
    
    def get_state(self, session_id: str) -> ConversationState:
        raw = state_store.get(f"state:{session_id}")
        if raw:
            return ConversationState(**raw)
        return ConversationState()

    def update_state(self, session_id: str, **kwargs) -> ConversationState:
        """
        Updates the current state with provided kwargs.
        Persists the updated state to storage.
        """
        current = self.get_state(session_id)
        updated_data = current.model_dump()
        updated_data.update(kwargs)
        
        # Validate effectively by re-creating model
        new_state = ConversationState(**updated_data)
        
        # Persist
        state_store.set(f"state:{session_id}", new_state.model_dump())
        return new_state

    def clear_state(self, session_id: str) -> None:
        state_store.delete(f"state:{session_id}")

state_manager = StateManager()
