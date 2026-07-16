# Plan — living roadmap

**Single source of planning truth for this repo.**  
Past audits: [AUDIT.md](AUDIT.md).

**Principle:** Prefer honest docs over unfinished features. Governance is the product; LangGraph is an implementation detail.

---

## Status: Flagship complete (v0.5)

Definition of done met:

1. Healthcare multi-agent path (LangGraph + harness + tiers + replan)
2. Deterministic CI matches the README diagram (incl. prompt regression)
3. Control plane UI + `make showcase`
4. Second vertical (claims) — harness + rules + CI gate
5. Grafana dashboard JSON for `/metrics`
6. Docs aligned; dead `docs/LANGGRAPH-PLAN.md` removed

**Now is empty.** Further work is post-flagship (Deferred only).

---

## Documentation rules

| Keep | Do not keep |
|------|-------------|
| `PLAN.md` — shipped + deferred | Dead phase checklists |
| `AUDIT.md` — dated findings | Duplicate roadmaps |
| Spec docs that match code | Superseded plan docs |

---

## Shipped

| Capability | Where |
|------------|--------|
| Dual-mode runtime | `agent/runtime.py` |
| Healthcare LangGraph + tool tiers + replan×1 | `agent/workflow.py` |
| Healthcare rules planner | `agent/planner.py` |
| Claims second vertical (rules + harness) | `agent/claims_planner.py`, `harness/examples/` |
| Semantic Harness + `sh:Policy` | `harness/` |
| Auth / guardrails / audit JSONL | `governance/` |
| Eval gates + prompt + claims regression + CI | `evaluation/`, `.github/workflows/` |
| FastAPI + Prometheus + identity header | `api/` |
| Control plane UI + showcase | `/ui`, `make showcase` |
| Grafana dashboard JSON | `observability/grafana/` |

Local: [docs/LOCAL.md](docs/LOCAL.md). Second vertical: [docs/SECOND-VERTICAL.md](docs/SECOND-VERTICAL.md).

---

## Now

_Empty — flagship complete._

---

## Deferred (post-flagship)

| Item | Why deferred |
|------|----------------|
| Claims LangGraph (full multi-agent) | Rules + harness already prove reuse |
| Example gallery / many verticals | One second vertical is enough |
| Large multi-swarm mesh | Complexity shown via tiers + replan |
| Grafana compose stack | JSON dashboard enough to import |
| pgvector / Postgres RAG | Keyword store enough |
| Full JWT / OIDC | `X-User-Scope` demonstrates the seam |
| Token cost budget gate | Needs live token metering |
| Dynamic compile from `sh:Workflow` | Edges stay explicit in Python |
| `harness verify` in CI image | Needs sibling runtime packaging |
| Human-in-the-loop approval UI | Later |
| 50-patient corpus | Expand when eval diversity demands it |

---

## Stack (actual)

| Layer | Choice |
|-------|--------|
| Language | Python 3.12+ |
| Install | `pip install -r requirements.txt` |
| Agent | LangGraph (healthcare); rules for CI + claims |
| LLM | Groq preferred, else OpenAI-compatible |
| API | FastAPI |
| UI | Static control plane at `/ui` |
| Retrieval | In-memory synthetic JSON |
| CI | GitHub Actions |
| Declaration | Semantic Harness JSON-LD |

---

## Explicit non-goals

- Real PHI / HIPAA production system  
- Full EHR integration  
- Another agent framework  
- Closure Apps coupling  
- Consumer chatbot UI as the flagship surface  

---

## Naming (locked)

**agentic-governance** — Enterprise Agentic AI SDLC Reference Architecture.
