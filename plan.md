# ✅ UPDATED ARCHITECTURE PLAN (WITH USER CONTEXT HANDLING)

---

## Phase 0 — Decisions (1–2 hours)

**Hard rules (bake into code):**

* ❌ DELETE never
* ✅ SELECT allowed (max rows = 100)
* ✅ INSERT/UPDATE allowed **only with preview + confirm**
* ✅ UPDATE must have a WHERE filter (no mass updates)
* ✅ Always parameterized queries (SQLAlchemy Core/ORM only)
* ✅ Audit log everything
* ✅ Executor layer enforces all rules (LLM cannot override)

---

## Phase 1 — Bootstrap Service (FastAPI) + DB Connector

**Goal:** accept DB URL, connect, introspect.

### 1. Create FastAPI app with endpoints:

* `POST /connect` → takes DB URL + credentials
* `GET /schema` → returns discovered safe schema summary
* `POST /chat` → main conversation endpoint

### 2. DB engine factory:

* Create SQLAlchemy engine dynamically from URL
* Connection test + graceful errors
* Metadata reflection caching

**Deliverable:** You can paste DB URL and confirm “connected”.

---

## Phase 2 — Schema Introspection + “Safe Exposure” Filter

**Goal:** reflect schema and decide what’s safe to expose.

### 1. Reflect schema:

* `MetaData().reflect(bind=engine)`
* Or `inspect(engine)` for incremental

### 2. Auto-filter tables (very important):

* Drop system tables (`alembic_version`, etc.)
* Drop auth/security tables
* Drop secret/token/password-related tables
* Drop tables without PK (or mark read-only)

### 3. Build an Entity Catalog:

For each table:

* Table name
* PK
* Columns
* Types
* Nullable
* Defaults
* Indexes
* FK relationships (optional)

**Deliverable:** internal JSON entity catalog.

---

## Phase 3 — Auto-Generate “Conversational Forms” from Schema

**Goal:** dynamic CRUD capability per table.

For each table:

### 1. Infer `create_fields`

* Required = non-nullable - PK - server defaults

### 2. Infer `read_fields`

* PK + representative columns

### 3. Infer `filterable_fields`

* Indexed columns
* PK
* Status/name/date/code fields

### 4. Infer `updateable_fields`

* Exclude PK
* Exclude audit/system columns

**Deliverable:** dynamic form inference per table.

---

## Phase 4 — Conversation State Engine (Plug-and-play)

**Goal:** fully conversational multi-turn flow.

Store per session:

```json
{
  "intent": "read|create|update",
  "entity": "table",
  "stage": "idle|collecting|preview|confirm",
  "draft_payload": {},
  "filters": []
}
```

### Universal commands:

* cancel
* start over
* show draft
* change X to Y
* confirm

**Deliverable:** conversational loop stability.

---

## Phase 5 — User Context Injection (Development Mode)

**Goal:** inject user identity for auditing and multi-tenant scoping (temporary implementation).**

### Current Implementation:

`POST /chat` accepts:

```
x-user-context: <base64_encoded_json>
```

Example raw JSON before encoding:

```json
{
  "user_id": 42,
  "user_role": "admin",
  "company_id": 10
}
```

Server flow:

1. Decode Base64
2. Parse JSON
3. Extract `user_id`
4. Inject into request object
5. Attach to conversation state

```python
request.user_id = context_data["user_id"]
```

### ⚠ Current Mode: Trusted Internal Admin Environment Only

This header is:

* Not signed
* Not cryptographically verified
* Not production-secure

**It is temporary for development.**

---

## Phase 6 — LLM Layer (Strict JSON, No SQL)

### A) Intent + Entity Detection

```json
{ "intent": "create|read|update|unknown", "entity": "table_name|null" }
```

### B) Field/Filter Extraction

```json
{
  "fields": { "colA": "value" },
  "filters": [{ "field": "id", "op": "=", "value": 10 }]
}
```

Requirements:

* `response_format=json_object`
* Pydantic validation
* Retry on schema mismatch
* LLM never generates SQL

**Deliverable:** LLM outputs structured plan only.

---

## Phase 7 — SQLAlchemy Execution Layer (Hard Guardrails)

### SELECT

* Enforce `LIMIT <= 100`
* No joins (v1)
* Validate columns exist
* Validate table exposed

### INSERT

* Only allowed fields
* No system columns
* Preview required
* Confirm required

### UPDATE

* Require WHERE filter
* Preview affected rows
* Confirm required
* Hard cap on max affected rows

Executor enforces rules, not LLM.

---

## Phase 8 — Preview + Confirm UX

**Mandatory for writes**

Flow:

1. Collect fields
2. Show preview
3. Show affected rows (update)
4. Wait for explicit confirm
5. Execute

No implicit execution.

---

## Phase 9 — Audit Logging + Replay

Create table:

`ai_audit_log`

Store:

* timestamp
* user_id
* session_id
* raw user message
* decoded context
* detected intent/entity
* extracted fields
* validated execution plan
* rows returned/affected
* latency
* error stack

Every action traceable.

---

## Phase 10 — Hardening (Pre-Production Security Upgrade)

Before release:

### 1. Replace Base64 header with:

* JWT (recommended)
  OR
* HMAC-signed header

### 2. Add:

* Secrets manager for DB URLs
* Encrypted at rest storage
* TLS DB connections
* Least-privilege DB user
* Statement timeout
* Rate limiting
* Sensitive column masking
* Prompt injection test suite
* EXPLAIN cost checks (optional)
* Read-only emergency mode flag

---

## Phase 11 — V2 Enhancements

* Multi-table joins
* Soft delete support
* RBAC
* Macros / skills
* Tenant policy engine
* LLM fallback model logic

---

# Final Outcome

A fully enterprise-grade:

Plug DB URL → Conversational DB Admin Agent

With:

✅ Controlled execution
✅ LLM planning only
✅ No SQL hallucination
✅ Preview-confirm writes
✅ Audit trail
✅ Upgradeable security model
✅ Zero blind trust in LLM

---
