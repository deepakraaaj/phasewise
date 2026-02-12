from typing import Any, Dict, Optional
from app.config import settings
from app.llm.prompts import detect_intent_prompt, read_plan_prompt
from app.llm.schemas import DetectIntentOut, ReadPlanOut
from app.llm.utils import parse_with_retry
from app.db.guards import forbid_write_ops

def detect_intent(message: str, exposed_tables: list[str]) -> DetectIntentOut:
    sys = detect_intent_prompt(exposed_tables)
    return parse_with_retry(settings.default_model, sys, message, DetectIntentOut)

def make_read_plan(message: str, entity: str, entity_profile: dict) -> ReadPlanOut:
    sys = read_plan_prompt(entity_profile)
    return parse_with_retry(settings.default_model, sys, message, ReadPlanOut)
