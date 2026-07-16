# Plan — living roadmap

**Single source of planning truth for this repo.**  
Past audits: [AUDIT.md](AUDIT.md) (2026-07-15).

**Principle:** Prefer honest docs over unfinished features. A reference people can use beats a lab of optional stacks.

---

## Status: Reference hardening complete (v0.6)

Flagship (v0.5) + correlation/contracts (v0.6):

- `request_id` on `/chat`, audit events, graph traces  
- [AUDIT-SCHEMA.md](docs/AUDIT-SCHEMA.md), [KPI.md](docs/KPI.md), [ADOPTERS.md](docs/ADOPTERS.md)  
- Unused OpenTelemetry deps removed  
- Optional `make obs-up` — Prometheus + Grafana only  

**Now is empty.** Further work is deferred / adopter-side.

---

## Where we are (observability)

| Concern | Have |
|---------|------|
| Traceability | `request_id` + workflow `trace[]` + audit JSONL |
| KPIs | CI gates + Prometheus + KPI map doc |
| LangSmith / ELK | Not shipped (documented reject) |
| Thin scrape stack | `docker-compose.obs.yml` |

---

## Now

_Empty._

---

## Deferred

| Item | When |
|------|------|
| Optional LangSmith/OTel exporter behind env flag | If workshops demand it |
| Token/cost gate | After LLM metering |
| Claims LangGraph | Parity demo only |
| JWT/OIDC sample | Enterprise workshops |
| `harness verify` in CI image | Easy to vendor sibling runtime |
| Human-in-the-loop approval UI | Product surface |

---

## Explicitly reject

ELK as required stack · LangSmith as required · more verticals/swarm theater · weekly full re-audits

---

## Shipped

| Capability | Where |
|------------|--------|
| Healthcare LangGraph + tiers + replan | `agent/workflow.py` |
| Claims second vertical | `agent/claims_planner.py`, `harness/examples/` |
| CI eval + prompt/claims regression | `evaluation/`, `.github/workflows/` |
| Control plane `/ui` + showcase | `ui/`, `scripts/showcase.py` |
| `request_id` correlation | `governance/request_context.py`, `api/` |
| Audit schema + JSONL durability | `governance/audit.py`, `docs/AUDIT-SCHEMA.md` |
| KPI + adopter guides | `docs/KPI.md`, `docs/ADOPTERS.md` |
| Prom+Grafana compose | `docker-compose.obs.yml`, `make obs-up` |

---

## Documentation rules

| Keep | Do not keep |
|------|-------------|
| `PLAN.md` | Dead phase checklists |
| `AUDIT.md` dated snapshot | Claiming OTel/ELK/LangSmith without wiring |

---

## Explicit non-goals

Real PHI/HIPAA prod · Full EHR · Another agent framework · Required vendor SaaS tracing · Shipping a full observability platform

---

## Naming (locked)

**agentic-governance** — Enterprise Agentic AI SDLC Reference Architecture.
