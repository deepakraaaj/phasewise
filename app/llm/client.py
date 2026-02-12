from openai import OpenAI
from app.config import settings

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        if settings.groq_api_key:
            # Use Groq
            _client = OpenAI(
                api_key=settings.groq_api_key,
                base_url=settings.groq_base_url
            )
        elif settings.openai_api_key:
            # Use OpenAI
            _client = OpenAI(api_key=settings.openai_api_key)
        else:
            raise RuntimeError("LLM API Key missing (OPENAI_API_KEY or GROQ_API_KEY). Put it in .env")
    return _client
