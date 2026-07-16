# Agentic Governance

**Enterprise Agentic AI SDLC Reference Architecture**

[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](pyproject.toml)
[![Semantic Harness](https://img.shields.io/badge/harness-compatible-sh:*-purple)](harness/harness.jsonld)

> *Most teams can build a LangGraph agent. Few can prove it's production-ready.*

**Whitepaper:** [docs/WHITEPAPER.md](docs/WHITEPAPER.md) · **Local demo:** [docs/LOCAL.md](docs/LOCAL.md) · **Plan:** [PLAN.md](PLAN.md) · **Audit:** [AUDIT.md](AUDIT.md)

This is **not** a chatbot demo. It is an open-source reference showing how to **operationalize** agentic AI with governance, evaluation, and CI discipline.

**LangGraph is an implementation detail.** Governance is the product.

---

## What this repo proves (honestly)

| Question | Answer in this repo |
|----------|---------------------|
| How do we gate AI deployments? | CI runs unit tests + PHI / hallucination / grounding / latency + harness validate |
| How do we prevent PHI leakage? | Auth **before** retrieval → scoped tools → output guardrails → audit |
| How do we know the rules path didn't regress? | Prompt regression + PHI / grounding / hallucination / latency on every push |
| How do we run real multi-agent inference? | LangGraph: authorize → route → plan → evaluate (replan×1) → finalize |
| How do we see governance live? | Control plane at `/ui` + `make showcase` |
| How do we describe the architecture? | [Semantic Harness](harness/harness.jsonld) — agents, tools, policy, invariants |
| How do we monitor? | Prometheus `/metrics` (Grafana is Planned — see [PLAN.md](PLAN.md)) |

**Known limitations** (by design for v0.4): in-memory synthetic store (not pgvector); demo identity via `X-User-Scope` / body scope (not JWT); eval gates exercise the **rules** planner — live LangGraph is optional CI + local `make live`. Details: [AUDIT.md](AUDIT.md).

---

## CI quality gates (what actually runs)

```
Commit
  → Lint (ruff or compileall)
  → Harness validate (structural)
  → Static synthetic-PHI hygiene
  → Unit + API tests
  → Prompt regression (golden.jsonl)
  → Grounding evaluation
  → Hallucination tests
  → PHI leakage tests
  → Latency benchmark (rules path)
  → (optional) Live LangGraph cases if GROQ_API_KEY secret set
```

**If a required gate fails, the PR fails.** Roadmap gates (prompt regression, token budget, Grafana) are listed in [docs/AI-SDLC.md](docs/AI-SDLC.md) and [PLAN.md](PLAN.md) — not advertised as shipped.

---

## Sample agent: Healthcare Appointment Assistant

100% **synthetic** data (Alice + John). Focus is governance, not domain complexity.

| Capability | Governed how |
|------------|--------------|
| Appointment / imaging / visit questions | Grounding evals + citations |
| Cross-patient access | Authorization before retrieval |
| Tool use | `sh:Policy` allowlist ∩ agent `hasTool` |
| Model output | Guardrails (names + synthetic MRN scope) |

---

## Runtime governance chain

```
Request (+ optional X-User-Scope)
  → Identity resolve (AUTH_STRICT optional)
  → Authorization (before any retrieval / LLM)
  → Route → Plan (intent tool tiers) → Evaluate (replan×1)  [graph]
  →   or rules planner                                      [CI]
  → Output guardrails
  → Audit (memory + optional JSONL)
  → Response (+ trace in graph mode)
```

---

## Repository map

```
agentic-governance/
├── harness/           # Semantic Harness declaration (sh:*)
├── agent/             # LangGraph workflow, rules planner, tools, harness loader
├── governance/        # Authorization, guardrails, audit
├── evaluation/        # PHI / hallucination / grounding / latency gates
├── knowledge/         # Synthetic patients (in-memory retrieval)
├── observability/     # Prometheus metrics
├── api/               # FastAPI
├── scripts/           # demo, live cases, harness validate, hygiene
├── tests/
├── .github/workflows/ # AI SDLC CI
├── PLAN.md            # Living roadmap (only planning source)
├── AUDIT.md           # Dated audit + remediation status
└── docs/
```

---

## Semantic Harness

| Repo | Role |
|------|------|
| [semantic-harness](https://github.com/leroyjware/semantic-harness) | Spec — declares agents, invariants, metrics |
| [semantic-runtimes](https://github.com/leroyjware/semantic-runtimes) | Reference CLI / HDD |
| **This repo** | Operationalizes the declaration — CI gates + runtime |

**Harness declares. LangGraph executes a compatible graph. Gates prove.**  
Workflow *edges* are explicit in Python; step IDs and agent prompts come from the harness. See [docs/SEMANTIC-HARNESS-BRIDGE.md](docs/SEMANTIC-HARNESS-BRIDGE.md).

---

## Quick start

```bash
git clone https://github.com/leroyjware/agentic-governance
cd agentic-governance
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

make gate          # full deterministic suite
make showcase      # hard-path narrative (PHI → read → refuse → schedule write)
make run           # http://localhost:8080/ui  (control plane)
```

```bash
# Prefer header identity (body cannot escalate when both are set)
curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -H 'X-User-Scope: patient:alice' \
  -d '{"message":"What are my upcoming appointments?"}'

curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -H 'X-User-Scope: patient:alice' \
  -d '{"message":"Show me John Smith'\''s MRI"}'
```

### Live multi-agent (Groq)

```bash
export GROQ_API_KEY=...
make showcase      # includes live graph step when key set
make demo          # per-step trace
make live          # curated cases
```

Add agents: [docs/ADD-AN-AGENT.md](docs/ADD-AN-AGENT.md).

---

## Status

| Component | Status |
|-----------|--------|
| Auth-before-retrieval + scoped tools + guardrails + audit | **Shipped** |
| Multi-agent LangGraph + tool tiers + evaluator replan | **Shipped** |
| Harness loader + `sh:Policy` | **Shipped** |
| Rules planner + eval gates (PHI 14 / hall / ground / latency) | **Shipped** |
| Control plane UI (`/ui`) + `make showcase` | **Shipped** |
| CI matching the diagram above | **Shipped** |
| Grafana / pgvector / JWT / prompt-regression gate | **Deferred** — [PLAN.md](PLAN.md) |

---

## License

Apache 2.0 — same as Semantic Harness.

**Contact:** [Closure Network](https://closurenetwork.com)
