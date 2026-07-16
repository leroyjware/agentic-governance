# Interview Guide

Quick reference for principal/staff AI architect interviews — especially healthcare, insurance, and platform governance roles.

---

## "What does AI governance mean to you?"

> I view governance as spanning the entire lifecycle. At design time, we declare agent capabilities, policies, and metrics in a Semantic Harness graph. During development, CI/CD enforces quality gates — prompt regression, grounding, hallucination refusal, PHI leakage tests, latency and cost budgets. In production, runtime middleware enforces authorization before retrieval, tool permissions, output scanning, and audit logging. In healthcare, governance isn't just compliance — it's operational discipline that makes agentic systems trustworthy at scale.

---

## "Where does governance live?"

Not one component. **Cross-cutting controls:**

| Phase | Controls |
|-------|----------|
| Design | Architecture standards, harness declaration |
| Development | Static scans, unit tests |
| Pre-deploy | Evaluation suites, invariant probes |
| Deploy | Approval gates, environment promotion |
| Runtime | Auth, tool policy, output guardrails, audit |
| Operations | Metrics, alerting, feedback to eval datasets |

Point to: `docs/GOVERNANCE-LAYERS.md` and README CI diagram.

---

## "How do you prevent PHI leakage?"

**Defense in depth** — not one test:

1. **Static scan** — no real PHI in repo (CI)
2. **Authorization before retrieval** — LLM never receives unauthorized records (architecture)
3. **Evaluation suite** — cross-patient scenarios must block (CI)
4. **Runtime guardrails** — outbound PHI pattern scan (production)
5. **Audit + metrics** — `agent_phi_violations_total`, blocked response logs

Key phrase: *"The model can't leak what it never received."*

---

## "How is this different from LangSmith / LangGraph alone?"

| Capability | LangSmith traces | This repo |
|------------|------------------|-----------|
| Trace debugging | Yes | Workflow `trace` + audit log |
| CI gate on PHI | No | Yes — pipeline fails |
| Harness declaration | No | Yes — portable graph |
| Auth before RAG | DIY | Reference pattern |
| Prometheus metrics | DIY | `/metrics` + Grafana JSON |
| Prompt regression in CI | DIY | `golden.jsonl` gate |
| Second vertical reuse | DIY | Claims assistant (same envelope) |

LangGraph is the orchestrator. **Governance is the product.**

---

## "What's Semantic Harness vs this repo?"

- **Semantic Harness** — declares the agent (portable JSON-LD)
- **Agentic Governance** — operationalizes the declaration (CI + runtime + observability)

Analog: OpenAPI spec vs API gateway with WAF, rate limits, and audit.

---

## Demo flow (5 minutes)

1. README CI diagram — gates that actually run
2. `make showcase` or `/ui` — PHI block + grounded answer + schedule write tier
3. Switch assistant to **claims** — cross-member block (envelope reuse)
4. Open `harness/harness.jsonld` + `harness/examples/claims-assistant.jsonld`
5. Point at Grafana JSON under `observability/grafana/` (import when scraping `/metrics`)

---

## Red flags to avoid saying

- "We fine-tuned a model for HIPAA" (wrong focus)
- "Governance is a compliance checklist" (too narrow)
- "The LLM prompt tells it not to leak PHI" (not defense in depth)
- "We use LangGraph so we're enterprise-ready" (orchestration ≠ governance)
