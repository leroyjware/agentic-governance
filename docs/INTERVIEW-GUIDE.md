# Interview Guide

Quick reference for principal/staff AI architect interviews — especially healthcare, insurance, and platform governance roles.

---

## Opening frame

> Most candidates show agents. I built a **governance envelope** you can clone and run: declare in Semantic Harness, execute in LangGraph (or rules), prove with CI gates, and return an **evidence pack** per request. LangGraph is swappable. Governance is the product.

---

## Hard questions → how this repo answers

### “Show me you can stop PHI leakage — not just prompt for it.”

Demo: `/ui` or curl as `patient:alice` → “Show me John Smith's MRI”.  
Expect: `blocked=true`, audit event, evidence claim `cross-scope-isolation` satisfied, **high** governance score (controls worked).  
Talk track: auth **before** retrieval; CI PHI suite; guardrails; metrics counter.

### “How do you know the agent didn’t regress last week?”

Point at `make gate` / GitHub Actions: prompt regression (`golden.jsonl`), PHI, hallucination, grounding, latency, claims vertical.  
Talk track: gates fail the build — not a dashboard hope.

### “What’s novel vs LangSmith / a LangGraph tutorial?”

| Concern | Traces alone | This reference |
|---------|--------------|----------------|
| Fail CI on PHI | No | Yes |
| Portable declaration | No | Semantic Harness |
| Auth before tools | DIY | Pattern + tests |
| Per-request evidence | DIY | `evidence` on `/chat` |
| Second vertical reuse | DIY | Claims assistant |

### “How does declaration connect to a single production request?”

Show response JSON: `request_id`, `evidence.harness`, `evidence.claims[]`, `governance_score`.  
Docs: [EVIDENCE.md](./EVIDENCE.md).  
Talk track: declare → execute → prove **for that trajectory**.

### “Where’s human oversight?”

Honest: full HITL approval UI is **deferred** ([PLAN.md](../PLAN.md)).  
What we ship today: maker-checker evaluator on the graph path, refuse/deny paths, audit + evidence for accountability, escalation as an adopter seam ([ADOPTERS.md](./ADOPTERS.md)).

### “Map this to NIST / OWASP.”

[CONTROLS-MAP.md](./CONTROLS-MAP.md) — alignment vocabulary, not certification.

---

## Classic short answers

### “What does AI governance mean to you?”

Lifecycle: harness declaration → CI quality gates → runtime authorize/tools/guardrails/audit → metrics + evidence. In regulated domains it’s operational discipline, not a checklist.

### “Where does governance live?”

Cross-cutting — see [GOVERNANCE-LAYERS.md](./GOVERNANCE-LAYERS.md). Not a single middleware class.

### “How do you prevent PHI leakage?”

Defense in depth: hygiene scan → auth before retrieval → eval suites → output guardrails → audit/metrics.  
*The model can’t leak what it never received.*

---

## 5-minute demo

1. README CI diagram  
2. `/ui` — PHI block → show **score + evidence claims**  
3. Appointments path — citations + evidence `grounding-or-refusal`  
4. Claims assistant — cross-member block (envelope reuse)  
5. Optional: `make obs-up` for Prometheus/Grafana  

---

## Red flags to avoid

- “We’re HIPAA certified / NIST certified”  
- “The prompt tells it not to leak PHI”  
- “We use LangGraph so we’re enterprise-ready”  
- Overclaiming HITL or ELK/LangSmith when we don’t ship them  
