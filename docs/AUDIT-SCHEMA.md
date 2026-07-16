# Audit schema

Every governance decision emits a structured event. Events are held in process memory **and** appended to JSONL when `AUDIT_LOG_PATH` is set (default `data/audit.jsonl`).

CI/tests use `AUDIT_LOG_PATH=off`.

---

## Record shape

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `event` | string | yes | e.g. `governance.block`, `agent.response`, `agent.refuse` |
| `timestamp` | number | yes | Unix epoch seconds |
| `request_id` | string (UUID) | yes* | Injected from request context when present |
| `user_scope` | string | usually | e.g. `patient:alice`, `member:john` |
| `reason` | string | optional | Denial / guardrail reason |
| `assistant` | string | optional | `healthcare` \| `claims` |
| `citations` | string[] | optional | Grounding doc ids |
| `message` | string | optional | User message (sensitive — redact in prod) |
| `engine` | string | optional | `rules`, `langgraph-workflow`, … |
| `step` | string | optional | Workflow step when relevant |

\*Present whenever the call went through `handle_chat` / `/chat`.

### JSONL example

```json
{"event":"governance.block","timestamp":1721136000.12,"request_id":"a1b2c3d4-...","user_scope":"patient:alice","reason":"unauthorized_patient_access","message":"Show me John Smith's MRI"}
```

---

## How to attach your SIEM

1. Tail or ship `data/audit.jsonl` (or your `AUDIT_LOG_PATH`) with Filebeat / Fluent Bit / Vector.  
2. Or poll `GET /audit?limit=500` and forward (demo only — prefer the file).  
3. Index on `request_id`, `event`, `user_scope`, `reason`.

We do **not** ship ELK. Your platform already has a log pipeline.

---

## Correlation

| Surface | Field |
|---------|--------|
| `POST /chat` body | `request_id` |
| Response header | `X-Request-Id` |
| Audit events | `request_id` |
| Graph `trace[]` entries | `request_id` |

Clients may send `X-Request-Id` or `request_id` in the body; otherwise the server generates a UUID.
