# Plan — living roadmap

**Single source of planning truth for this repo.**  
Past audits: [AUDIT.md](AUDIT.md). When work ships: move it to **Shipped**, clear **Now**, update README if claims change.

**Principle:** Prefer honest docs over unfinished features. Governance is the product; LangGraph is an implementation detail.

---

## Documentation rules

| Keep | Do not keep |
|------|-------------|
| `PLAN.md` — shipped + now + deferred | Dead phase checkboxes |
| `AUDIT.md` — dated findings + remediation | Duplicate roadmaps in subsystem READMEs |
| Spec docs that match code | “Phase N will add…” stubs |

---

## Shipped

| Capability | Where |
|------------|--------|
| Dual-mode runtime (`rules` / `graph` / `auto`) | `agent/runtime.py` |
| Multi-agent LangGraph + intent tool tiers + evaluator replan×1 | `agent/workflow.py`, `governance/tool_tiers.py` |
| Rules planner (schedule write tier parity) | `agent/planner.py` |
| Semantic Harness + loader (`sh:Policy`, prompts, tools) | `harness/`, `agent/harness_loader.py` |
| Auth-before-retrieval + scoped tools + guardrails + audit JSONL | `governance/` |
| Eval gates + hygiene + harness validate in CI | `evaluation/`, `.github/workflows/` |
| FastAPI + Prometheus + `X-User-Scope` / `AUTH_STRICT` | `api/` |
| Control plane UI | `/ui` (`ui/index.html`) |
| Narrative showcase | `make showcase` → `scripts/showcase.py` |
| Prompt regression gate (`golden.jsonl`) | `evaluation/prompt_regression.py` |
| Synthetic patients (Alice, John) — in-memory retrieval | `knowledge/` |
| Credibility waves 1–3 | 2026-07-15 |
| Next-1 hard path + Next-2 control plane | 2026-07-15 |

Local: [docs/LOCAL.md](docs/LOCAL.md).

---

## Now

_No active wave._ Next increments only if they strengthen the governance thesis.

Suggested later (not started):

- Optional Grafana JSON dashboard (visual polish on existing `/metrics`)
- One second vertical as a second harness file (“same CI, different agent”)
- Token-cost gate once live metering exists

---

## Deferred (do not advertise as shipped)

| Item | Why deferred |
|------|----------------|
| Example gallery / many verticals | Dilutes the flagship hard path |
| Large multi-swarm mesh | Branching + tiers already prove complexity |
| Grafana + compose | Metrics exist; dashboards are polish |
| pgvector / Postgres RAG | Keyword store enough for governance story |
| Full JWT / OIDC | `X-User-Scope` demonstrates the seam |
| Token cost budget gate | Needs live token metering |
| Dynamic compile from `sh:Workflow` | Edges stay explicit in Python |
| `harness verify` in CI image | Needs sibling runtime packaging |
| Human-in-the-loop approval product UI | Later |
| 50-patient corpus | Expand when eval diversity demands it |

---

## Stack (actual)

| Layer | Choice |
|-------|--------|
| Language | Python 3.12+ |
| Install | `pip install -r requirements.txt` |
| Agent | LangGraph (swappable) |
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
