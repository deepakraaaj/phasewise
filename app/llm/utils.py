import json
from pydantic import BaseModel, ValidationError
from app.config import settings
from app.llm.client import get_client

def call_llm_json(model: str, system: str, user: str) -> dict:
    """
    Calls LLM and asks for JSON object output.
    Uses Chat Completions API with response_format json_object.
    """
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    txt = resp.choices[0].message.content
    return json.loads(txt)

def parse_with_retry(model: str, system: str, user: str, schema: type[BaseModel], retries: int = 2) -> BaseModel:
    last_err = None
    for i in range(retries + 1):
        data = call_llm_json(model=model, system=system, user=user)
        try:
            return schema(**data)
        except ValidationError as e:
            last_err = str(e)
            # On retry, nudge model with validation error
            user = user + f"\n\nValidation error to fix: {last_err}\nReturn JSON that matches schema exactly."
    raise ValueError(f"LLM output failed validation: {last_err}")
