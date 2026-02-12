from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

class DBManager:
    """
    Holds Engines per session_id.
    For real multi-tenant SaaS: store encrypted db_url per tenant and recreate engines.
    """
    def __init__(self):
        self._engines: dict[str, Engine] = {}

    def connect(self, session_id: str, db_url: str) -> Engine:
        engine = create_engine(db_url, pool_pre_ping=True, future=True)
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        self._engines[session_id] = engine
        return engine

    def get_engine(self, session_id: str) -> Engine:
        if session_id not in self._engines:
            raise RuntimeError("Not connected. Call /connect first.")
        return self._engines[session_id]

db_manager = DBManager()
