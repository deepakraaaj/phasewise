import json
from typing import Any, Dict, Optional
from app.config import settings

class InMemoryStateStore:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self._store.get(key)

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

class RedisStateStore:
    def __init__(self, redis_url: str):
        import redis
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        val = self.r.get(key)
        return json.loads(val) if val else None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self.r.set(key, json.dumps(value))

    def delete(self, key: str) -> None:
        self.r.delete(key)

def make_state_store():
    if settings.state_store == "redis":
        return RedisStateStore(settings.redis_url)
    return InMemoryStateStore()

state_store = make_state_store()
