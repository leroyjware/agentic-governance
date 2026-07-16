# Agentic Governance

**Enterprise Agentic AI SDLC Reference Architecture**

[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](pyproject.toml)
[![Semantic Harness](https://img.shields.io/badge/harness-compatible-sh:*-purple)](harness/harness.jsonld)

> *Most teams can build a LangGraph agent. Few can prove it's production-ready.*

**Whitepaper (for reviewers):** [docs/WHITEPAPER.md](docs/WHITEPAPER.md)

This is **not** a chatbot demo. It is an open-source reference implementation showing how to **operationalize** agentic AI with governance, evaluation, observability, and deployment discipline — the way enterprise architects at healthcare, insurance, and regulated industries actually ship.

**LangGraph is an implementation detail.** Governance is the product.

---

## What this repo proves

| Question | Answer in this repo |
|----------|---------------------|
| How do we gate AI deployments? | CI/CD quality gates that **fail the pipeline** |
| How do we prevent PHI leakage? | Defense in depth: static scan → auth at retrieval → runtime guardrails → audit |
| How do we know the agent didn't regress? | Prompt regression + grounding + hallucination suites on every PR |
| How do we govern runtime behavior? | Middleware: auth → tool permissions → output scanner → audit |
| How do we monitor production agents? | Prometheus `/metrics` (Grafana planned) |
| How do we describe the agent architecture? | [Semantic Harness](harness/harness.jsonld) — portable graph declaration |

---

## The star diagram: AI SDLC with quality gates

```
Developer
    ↓
Commit
    ↓
Build
    ↓
Unit Tests
    ↓
Prompt Regression Tests          ← known prompts, accuracy must not drop
    ↓
RAG / Grounding Evaluation       ← every answer cites retrieved docs
    ↓
Hallucination Tests              ← "no context" → "I don't have enough information"
    ↓
PHI Leakage Tests                ← unauthorized access → denied + audit event
    ↓
Latency Benchmark                ← p95 < 2s or pipeline fails
    ↓
Token Cost Budget                ← avg < 5000 tokens or pipeline fails
    ↓
Security Scan
    ↓
Architecture Validation          ← harness.jsonld validates, invariants hold
    ↓
Human Approval (optional gate)
    ↓
Deploy
    ↓
Runtime Monitoring               ← Prometheus + Grafana
    ↓
Feedback Loop → Evaluation dataset growth
```

**If any gate fails, deployment stops.** This is DevSecOps for agentic AI.

---

## Sample agent: Healthcare Appointment Assistant

A deliberately simple agent on **100% synthetic data** — so we can focus on governance, not domain complexity.

| Capability | Governed how |
|------------|--------------|
| Answer appointment questions | Grounding tests — must cite retrieved docs |
| Retrieve fake patient records | Authorization **before** retrieval — LLM never sees unauthorized PHI |
| Schedule appointments | Tool permissions — planner cannot invoke write tools without policy |
| Summarize visit notes | Output scanner — PHI patterns blocked if user lacks role |

**The pitch is not "look, an agent."** The pitch is **"here's how we prove this agent is production-ready."**

---

## Runtime governance chain

Every request passes through governance — not around it:

```
User Request
    ↓
Authentication
    ↓
Authorization (RBAC / ABAC)
    ↓
Planner (LangGraph)
    ↓
Tool Permission Check
    ↓
Retrieval (scoped to authorized records only)
    ↓
Output Scanner (PHI patterns, policy violations)
    ↓
Audit Logger (who, what, why, blocked?)
    ↓
Response
```

---

## Repository map

```
agentic-governance/
├── harness/                 # Semantic Harness declaration (sh:*) — architecture metadata
├── agent/                   # LangGraph implementation (planner, tools, graph)
├── governance/              # Policy engine, approval, guardrails, audit
├── evaluation/              # Reusable eval runners + healthcare test suites
├── knowledge/               # Synthetic RAG (pgvector), fake patient records
├── observability/           # Prometheus metrics, Grafana dashboards, tracing
├── api/                     # FastAPI entrypoint with governance middleware
├── tests/                   # Unit + integration tests
├── .github/workflows/       # AI SDLC pipeline — the star of the repo
└── docs/                    # Architecture, governance layers, interview guide
```

---

## Three meanings of "governance" (and how this repo covers all three)

| Layer | Focus | Where in repo |
|-------|-------|---------------|
| **AI Governance** | Policies, compliance, audit, responsible AI | `governance/`, PHI tests, audit logs |
| **Agentic Governance** | Tool permissions, autonomy tiers, agent mesh | `governance/authorization.py`, harness policies |
| **AI SDLC Governance** | Build → evaluate → approve → deploy → monitor | `.github/workflows/`, `evaluation/` |

See [docs/GOVERNANCE-LAYERS.md](docs/GOVERNANCE-LAYERS.md).

---

## Relationship to Semantic Harness

| Repo | Role |
|------|------|
| [semantic-harness](https://github.com/leroyjware/semantic-harness) | **Declares** the agent — capabilities, invariants, metrics, policies |
| [semantic-runtimes](https://github.com/leroyjware/semantic-runtimes) | Reference runtime + HDD (`harness verify`, export, hooks) |
| **agentic-governance** (this repo) | **Operationalizes** the declaration — CI gates, runtime middleware, observability |

```
harness.jsonld  →  CI/CD reads invariants & metrics  →  gates enforce them
                →  Runtime loads policies            →  middleware enforces them
                →  Observability exports metrics     →  Grafana proves them
```

This is the missing middle layer between "we declared an agent" and "we trust it in production."

---

## Quick start

```bash
git clone https://github.com/leroyjware/agentic-governance
cd agentic-governance
pip install -r requirements.txt

# Run governance quality gates (PHI, hallucination, grounding, latency)
make eval

# Unit + API tests
make test

# Start the governed API
make run
# → http://localhost:8080/docs
```

**Try it:**

```bash
# Authorized — grounded answer with citations
curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_scope":"patient:alice","message":"What are my upcoming appointments?"}'

# Blocked — cross-patient PHI attempt (never reaches LangGraph)
curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_scope":"patient:alice","message":"Show me John Smith'\''s MRI"}'

# Refusal — no context for surgery
curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_scope":"patient:alice","message":"When is my surgery?"}'
```

### LangGraph (live LLM)

```bash
export GROQ_API_KEY=...          # or OPENAI_API_KEY
# optional: export GROQ_MODEL=llama-3.3-70b-versatile
make smoke                       # live ReAct agent through governance
make run                         # AGENT_MODE=auto → LangGraph when key present
```

CI and `make eval` use `AGENT_MODE=rules` (deterministic planner, no API key). Production-shaped demos use LangGraph with the **same** auth → tools → guardrails → audit envelope.

## Status

| Component | Status |
|-----------|--------|
| Governance middleware (auth → retrieve → guardrails → audit) | **Shipped** |
| LangGraph ReAct agent + scoped LangChain tools | **Shipped** |
| Rules planner fallback (CI / no API key) | **Shipped** |
| PHI / hallucination / grounding / latency eval gates | **Shipped** |
| FastAPI + Prometheus metrics | **Shipped** |
| GitHub Actions CI | **Shipped** |
| Semantic Harness declaration | **Shipped** |
| Grafana dashboards | Planned |

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Planning + docs + harness | Done |
| 1 | Governance + eval gates + API | Done |
| 2 | LangGraph + live LLM | **Done** |
| 3 | Grafana dashboards | Planned |
| 4 | Thought leadership polish | Planned |

See [PLAN.md](PLAN.md) for the full phased roadmap.

---

## Who this is for

- **Principal / Staff AI architects** building enterprise agent platforms
- **Platform engineers** industrializing AI SDLC at healthcare, insurance, finance
- **Interview candidates** who need to demonstrate governance beyond "I built a RAG chatbot"
- **Semantic Harness adopters** who want a reference for operationalizing `sh:Invariant` and `sh:Metric` probes

---

## License

Apache 2.0 — same as Semantic Harness.

**Contact:** [Closure Network](https://closurenetwork.com)
