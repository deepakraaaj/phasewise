# AI DB Agent (TAG) – Phase 1 (Production-safe Read Only)

## What this phase supports
- Connect to a SQL DB by URL (Postgres/MySQL)
- Safe schema introspection + filtering
- Conversational READ (SELECT) using LLM planning
- Strict guardrails:
  - No DELETE
  - No direct SQL from LLM
  - Max rows enforced (LIMIT <= 100)
  - Only introspected & exposed tables can be queried

## Setup
1) Create venv + install:
   pip install -r requirements.txt

2) Copy env:
   cp .env.example .env
   set OPENAI_API_KEY

3) Run:
   uvicorn app.main:app --reload

## Endpoints
- POST /connect    { session_id, db_url }
- GET  /schema     ?session_id=...
- POST /chat       { session_id, message }

## Example
1) Connect
curl -X POST http://127.0.0.1:8000/connect \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo","db_url":"postgresql://user:pass@localhost:5432/db"}'

2) Ask
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo","message":"show last 20 invoices"}'
