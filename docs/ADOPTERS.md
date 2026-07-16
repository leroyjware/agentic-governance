# Adopter guide — use this as a pattern, not a product

This repo is a **reference architecture**. Copy the envelope; replace the seams with your platform.

---

## Seams to swap

| Seam | Reference default | Your swap |
|------|-------------------|-----------|
| **Identity** | `X-User-Scope` (+ optional `AUTH_STRICT`) | JWT/OIDC middleware → map claims to `user_scope` |
| **LLM** | Groq / OpenAI-compatible via env | Azure OpenAI, Bedrock, private endpoint (`OPENAI_BASE_URL`) |
| **Orchestrator** | LangGraph (`agent/workflow.py`) | Keep the envelope; swap graph implementation |
| **Retrieval** | In-memory synthetic JSON | pgvector / OpenSearch / your EHR proxy — **after** authorize |
| **Declaration** | `harness/*.jsonld` | Your agents/tools/policies/invariants |
| **Eval gates** | `evaluation/*` + CI | Point probes at your suites; keep fail-closed |
| **Metrics** | Prometheus `/metrics` | Scrape into your Grafana/Datadog |
| **Audit / SIEM** | JSONL + `GET /audit` | Ship file to your pipeline ([AUDIT-SCHEMA.md](./AUDIT-SCHEMA.md)) |
| **Tracing** | `request_id` + workflow `trace[]` | Optional: export spans to your APM (LangSmith/OTel/etc.) |

---

## Minimum viable adoption

1. Keep **authorize before retrieval** and **CI gates that fail the build**.  
2. Preserve **`request_id`** correlation across API → audit → traces.  
3. Replace synthetic knowledge; do not weaken auth to “make demos easier.”  
4. Attach IdP and SIEM at the seams above — do not wait for this repo to ship them.

---

## Local observability (optional)

```bash
# Terminal 1 — API
make run

# Terminal 2 — Prometheus + Grafana only (not ELK)
make obs-up
# Grafana http://localhost:3000  (anonymous or admin/admin)
# Prometheus http://localhost:9090
```

See `docker-compose.obs.yml`. Tear down: `make obs-down`.

---

## What not to copy blindly

- Client-trusted scope without IdP (demo only)  
- In-memory patient store (demo only)  
- Treating LangGraph as the governance layer  

---

## Related

- [KPI.md](./KPI.md) — how we measure “working”  
- [AUDIT-SCHEMA.md](./AUDIT-SCHEMA.md) — log contract  
- [SECOND-VERTICAL.md](./SECOND-VERTICAL.md) — envelope reuse  
- [PLAN.md](../PLAN.md) — shipped vs deferred  
