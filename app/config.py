import os
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel

class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    default_model: str = os.getenv("DEFAULT_MODEL", "gpt-4o")
    state_store: str = os.getenv("STATE_STORE", "inmemory").lower()
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app_env: str = os.getenv("APP_ENV", "dev")

settings = Settings()
