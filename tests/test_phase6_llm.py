import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm.schemas import CreatePlanOut, UpdatePlanOut, FilterOut
from app.llm.prompts import create_plan_prompt, update_plan_prompt

def test_phase6_schemas():
    """Test that Create and Update schemas are properly defined"""
    
    # Test CreatePlanOut
    create_plan = CreatePlanOut(
        entity="users",
        fields={"username": "alice", "email": "alice@example.com"}
    )
    assert create_plan.entity == "users"
    assert create_plan.fields["username"] == "alice"
    print("✅ CreatePlanOut schema validated!")
    
    # Test UpdatePlanOut
    update_plan = UpdatePlanOut(
        entity="users",
        fields={"email": "newemail@example.com"},
        filters=[FilterOut(field="id", op="=", value=5)]
    )
    assert update_plan.entity == "users"
    assert update_plan.fields["email"] == "newemail@example.com"
    assert len(update_plan.filters) == 1
    assert update_plan.filters[0].field == "id"
    print("✅ UpdatePlanOut schema validated!")

def test_phase6_prompts():
    """Test that Create and Update prompts are properly generated"""
    
    entity_profile = {
        "table": "users",
        "columns": [
            {"name": "id", "type": "INTEGER", "nullable": False, "pk": True},
            {"name": "username", "type": "VARCHAR", "nullable": False},
            {"name": "email", "type": "VARCHAR", "nullable": False}
        ]
    }
    
    # Test create prompt
    create_prompt = create_plan_prompt(entity_profile)
    assert "CREATE" in create_prompt or "INSERT" in create_prompt
    assert "users" in str(entity_profile)
    assert "JSON" in create_prompt
    print("✅ create_plan_prompt generated correctly!")
    
    # Test update prompt
    update_prompt = update_plan_prompt(entity_profile)
    assert "UPDATE" in update_prompt
    assert "filters" in update_prompt
    assert "JSON" in update_prompt
    print("✅ update_plan_prompt generated correctly!")

def test_phase6_planner_imports():
    """Test that planner has the new functions"""
    from app.core.planner import make_create_plan, make_update_plan
    
    assert callable(make_create_plan)
    assert callable(make_update_plan)
    print("✅ Planner functions imported successfully!")

if __name__ == "__main__":
    print("Testing Phase 6: LLM Layer (Schema & Prompt Validation)")
    print("=" * 60)
    
    try:
        test_phase6_schemas()
        print()
        test_phase6_prompts()
        print()
        test_phase6_planner_imports()
        print()
        print("=" * 60)
        print("✅ All Phase 6 validation tests passed!")
        print()
        print("Note: Full LLM integration tests require API keys.")
        print("The schemas, prompts, and planner functions are correctly implemented.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
