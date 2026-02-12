from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="AI DB Agent - Phase 1 (Read Only)")
app.include_router(router)
