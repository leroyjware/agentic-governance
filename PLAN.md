# Plan — living roadmap

**Single source of planning truth for this repo.**  
Past audits: [AUDIT.md](AUDIT.md) (2026-07-15).

**Principle:** Prefer honest docs over unfinished features. Novelty must strengthen the governance thesis — not decorate it.

---

## Status: Evidence & interview sharpness complete (v0.7)

Clone → `make gate` → `/ui` shows **score + evidence claims** on every chat.  
Next novelty only if it strengthens declaration → proof — not HITL stubs or a third vertical.

---

## Feedback triage (kept for scope discipline)

| Idea | Verdict | Why |
|------|---------|-----|
| Verifiable harness → evidence receipt | **Shipped** | `governance/evidence.py` + `/chat` |
| Governance score | **Shipped** | `governance/score.py` + `/ui` |
| NIST / OWASP controls map | **Shipped** | `docs/CONTROLS-MAP.md` |
| Interview hard-question guide | **Shipped** | `docs/INTERVIEW-GUIDE.md` |
| Prom alert example YAML | **Shipped** | `observability/prometheus/alerts.yml` (not auto-loaded) |
| Human-in-the-loop approval UI | **Defer** | Easy to look half-baked |
| More verticals (prior auth, etc.) | **Reject for now** | Two verticals already prove reuse |
| “What-if” prompt simulator | **Reject** | CI golden set is the regression story |
| Anomaly ML on metrics | **Reject** | Alert YAML only; no ML |
| ELK / LangSmith required | **Reject** | Already decided |

---

## Now

_Empty — pick from Deferred only when an interview or workshop needs it._

---

## Deferred

| Item | When |
|------|------|
| Human-in-the-loop approval gate | When we can ship a real escalation path, not a stub |
| Optional LangSmith/OTel exporter | Workshops |
| Token/cost gate | After LLM metering |
| Claims LangGraph | Parity demo only |
| JWT/OIDC sample | Enterprise workshops |
| Third vertical | Only if reuse story needs another domain |

---

## Explicitly reject

ELK as required · LangSmith as required · vertical gallery · swarm theater · weekly re-audits · novelty for novelty’s sake

---

## Shipped

| Capability | Where |
|------------|--------|
| Healthcare LangGraph + tiers + replan | `agent/workflow.py` |
| Claims second vertical | `agent/claims_planner.py` |
| CI gates + prompt/claims regression | `evaluation/` |
| `request_id` + audit schema + KPI/adopter docs | `governance/`, `docs/` |
| Prom+Grafana compose | `make obs-up` |
| Evidence pack + governance score (v0.7) | `governance/evidence.py`, `score.py`, `/ui` |
| Controls map + interview guide | `docs/CONTROLS-MAP.md`, `INTERVIEW-GUIDE.md` |

---

## Naming (locked)

**agentic-governance** — Enterprise Agentic AI SDLC Reference Architecture.
