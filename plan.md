## Phase 0 — Decisions (1–2 hours)

**Hard rules (bake into code):**

* ❌ DELETE never
* ✅ SELECT allowed (max rows = 100)
* ✅ INSERT/UPDATE allowed **only with preview + confirm**
* ✅ UPDATE must have a WHERE filter (no mass updates)
* ✅ Always parameterized queries (SQLAlchemy Core/ORM only)
* ✅ Audit log everything

---

## Phase 1 — Bootstrap Service (FastAPI) + DB Connector

**Goal:** accept DB URL, connect, introspect.

1. Create FastAPI app with endpoints:

   * `POST /connect` → takes DB URL + credentials, stores connection profile (encrypted or in-memory for dev)
   * `GET /schema` → returns discovered safe schema summary
   * `POST /chat` → main conversation endpoint

2. DB engine factory:

   * Create SQLAlchemy engine dynamically from URL
   * Connection test + graceful errors

**Deliverable:** You can paste DB URL and confirm “connected”.

---

## Phase 2 — Schema Introspection + “Safe Exposure” Filter

**Goal:** reflect schema and decide what’s safe to expose.

1. Reflect schema:

   * `MetaData().reflect(bind=engine)` (or `inspect(engine)` for incremental)
2. Auto-filter tables (very important):

   * Drop obvious system tables: `alembic_version`, `flyway_schema_history`, `django_migrations`, etc.
   * Drop tables with names containing: `auth`, `token`, `secret`, `password`, `credential`, `session` (configurable)
   * Drop tables without a primary key (or mark read-only)
3. Build an **Entity Catalog** from reflected schema:

   * table name, PK, columns, types, nullable, FK relationships, indexes (if detectable)

**Deliverable:** internal JSON “entity catalog” generated automatically.

---

## Phase 3 — Auto-Generate “Conversational Forms” from Schema

**Goal:** for each table, infer insert/update requirements automatically.

For each table:

1. Infer **create_fields**:

   * required = non-nullable columns excluding PK + server defaults
2. Infer **read_fields**:

   * pick representative columns (PK + 4–8 useful columns)
3. Infer **filterable fields**:

   * indexed columns + PK + common identifiers (name/code/no/date/status)
4. Infer **updateable fields**:

   * exclude PK, created_at, created_by, audit columns unless allowed

**Deliverable:** the agent can ask missing fields for any table automatically.

---

## Phase 4 — Conversation State Engine (Plug-and-play)

**Goal:** fully conversational multi-turn flow.

1. Store per-session state (Redis recommended):

   * `intent` (read/create/update)
   * `entity`
   * `stage` (idle → collecting → preview → confirm)
   * `draft_payload` (fields collected so far)
   * `filters` (for update/read)
2. Add universal commands:

   * “cancel”, “start over”, “show draft”, “change X to Y”

**Deliverable:** bot asks follow-up questions until required fields are present.

---

## Phase 5 — LLM Layer (2 prompts + strict JSON)

**Goal:** LLM talks naturally but outputs strict structures.

### A) Intent + Entity Detection

LLM returns:

```json
{ "intent": "create|read|update|unknown", "entity": "table_name|null" }
```

Entity must be chosen from the catalog list you provide.

### B) Field/Filter Extraction

LLM returns:

```json
{
  "fields": { "colA": "value", "colB": 123 },
  "filters": [{ "field": "id", "op": "=", "value": 10 }]
}
```

Use `response_format: json_object` + Pydantic validation + retry-on-invalid.

**Deliverable:** LLM never emits SQL—only structured deltas to merge into state.

---

## Phase 6 — SQLAlchemy Execution Layer (No raw SQL)

**Goal:** execute safely with hard guardrails.

### SELECT executor

* Always `LIMIT <= 100`
* Disallow heavy joins initially (single-table only in v1)
* Allow simple filters, date ranges, equals/like/IN

### INSERT executor

* Only allow columns inferred as create_fields
* Block writing to forbidden fields (`id`, `created_at`, etc.)
* Execute only after “confirm”

### UPDATE executor

* Require at least one filter
* Before confirm: run “preview count” + show sample rows
* After confirm: execute update + return affected rows

**Deliverable:** safe CRUD without hallucinated SQL.

---

## Phase 7 — Preview + Confirm UX (Mandatory)

**Goal:** zero surprise writes.

For create/update:

1. Show preview card/table:

   * what will be inserted/updated
   * how many rows will be affected (for update)
2. Require explicit confirmation:

   * “confirm” / “proceed”
3. Provide “modify” option:

   * “change amount to 35000”
   * “set due_date to 2026-03-30”

**Deliverable:** conversational form completion + final commit.

---

## Phase 8 — Audit Logging + Replay

**Goal:** enterprise-proof traceability.

Create table `ai_audit_log`:

* timestamp
* user/session id
* raw user messages
* generated intent/entity
* extracted fields
* final SQLAlchemy operation summary
* rows returned / affected
* errors + latency

**Deliverable:** you can debug anything that happened.

---

## Phase 9 — Hardening (Before real use)

**Goal:** stop bad cases automatically.

Add guards:

* Reject UPDATE without WHERE
* Reject queries that scan too much (optional: EXPLAIN cost check)
* Rate limiting per user/session
* Timeouts
* “blocked tables” list configurable
* “readonly mode” switch for emergency

**Deliverable:** safe enough for internal admin usage.

---

## Phase 10 — V2 Enhancements (After it works)

* Multi-table join support via detected FKs (careful)
* Soft delete support (still no hard delete)
* RBAC (roles/permissions) — add last as you said
* “skills” / “macros” (predefined actions like `mark_invoice_not_received`)

---

# What you’ll have at the end

A **plug-and-play conversational DB admin**:

✅ Paste DB URL → auto introspect
✅ User chats naturally
✅ System asks missing fields
✅ Preview → confirm → commit
✅ No SQL writing by user or LLM
✅ No deletes
✅ Audit log for everything

---

If you want, I can give you next (pick one, I’ll just deliver it):

1. A full **FastAPI starter repo skeleton** (files + code) for this exact plan
2. The **Pydantic schemas + prompts** (intent + extraction + confirmation)
3. The **SQLAlchemy reflection + entity catalog builder** code (core of plug-and-play)
