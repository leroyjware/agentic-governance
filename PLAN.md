# Plan — living roadmap

**Single source of planning truth for this repo.**  
Historical phase checklists were removed so they cannot drift. Past audits live in [AUDIT.md](AUDIT.md); this file tracks what is shipped and what we do next.

**Principle:** Prefer honest docs over unfinished features. Every claim in the README must match CI or be labeled Planned.

---

## Documentation rules

| Keep | Do not keep |
|------|-------------|
| `PLAN.md` — current + next | Dead phase checklists with unchecked boxes |
| `AUDIT.md` — dated findings + remediation status | Duplicate roadmaps in subsystem READMEs |
| Spec docs that match code (`docs/AI-SDLC.md`, etc.) | “Phase N will add…” READMEs that never update |

When a planned item ships: move it to **Shipped**, update README/AI-SDLC, mark the AUDIT finding remediated.

---

## Shipped (current)

| Capability | Where |
|------------|--------|
| Dual-mode runtime (`rules` / `graph` / `auto`) | `agent/runtime.py` |
| Multi-agent LangGraph: authorize → route → plan → evaluate → finalize | `agent/workflow.py` |
| Rules planner for deterministic CI | `agent/planner.py` |
| Semantic Harness declaration + loader (prompts, models, tools, policy) | `harness/`, `agent/harness_loader.py` |
| Auth-before-retrieval + scoped tools | `governance/authorization.py`, `agent/tools.py` |
| Output guardrails + audit (memory + JSONL) | `governance/` |
| Eval gates: PHI, hallucination, grounding, latency (rules path) | `evaluation/` |
| FastAPI + Prometheus counters | `api/`, `observability/` |
| CI: tests + evals + harness validate (+ optional live Groq) | `.github/workflows/ci.yml` |
| Synthetic patients (Alice, John) — in-memory retrieval | `knowledge/data/patients.json` |

Local demo: [docs/LOCAL.md](docs/LOCAL.md).

---

## Now — credibility waves

Track with checkboxes. Uncheck only while work is in flight; delete the wave section when done and fold into **Shipped** / **Next**.

### Wave 1 — Truth (docs match code)

- [x] Rewrite README star diagram / status to match CI
- [x] Fix map claims (no pgvector; synthetic in-memory store)
- [x] Rewrite `docs/AI-SDLC.md` as shipped vs planned
- [x] Fix `docs/SYNTHETIC-DATA.md` paths and patient count
- [x] Fix `docs/ADD-AN-AGENT.md` to real APIs
- [x] Replace stale subsystem READMEs
- [x] Align CONTRIBUTING with `pip` + real make targets
- [x] Replace this PLAN with living roadmap (this file)

### Wave 2 — Declare → prove

- [x] Load `sh:Policy` allowlist at runtime
- [x] Structural `scripts/validate_harness.py` + CI step
- [x] Prefer sibling `harness validate` when available (`make validate-harness`)
- [x] Document harness topology honesty (compatible steps, hardcoded edges)

### Wave 3 — Governance depth

- [x] Expand PHI suite (≥12 scenarios)
- [x] Enforce synthetic MRN pattern in output guardrails
- [x] Persist audit events to JSONL (`AUDIT_LOG_PATH`)
- [x] Light identity: `X-User-Scope` + optional `AUTH_STRICT=1`
- [x] Minimal static synthetic-PHI hygiene scan in CI
- [x] `make lint` (ruff if installed, else compileall)

---

## Next (deferred — do not advertise as shipped)

| Item | Why deferred |
|------|----------------|
| Grafana dashboards + compose | Visual polish; metrics already exist |
| pgvector / Postgres RAG | Not needed for governance story; keyword store is enough |
| Full JWT / OIDC | Demo uses `X-User-Scope`; enterprise IdP is adopter work |
| Prompt regression + token budget gates | Valuable; add when suites exist |
| Dynamic LangGraph compile from `sh:Workflow` | Edges stay explicit in Python until needed |
| `harness verify` (metric probes via HDD) | Needs sibling runtime in CI image |
| Human-in-the-loop approval UI | Later product surface |
| 50-patient corpus | Expand when eval diversity demands it |

---

## Stack (actual)

| Layer | Choice |
|-------|--------|
| Language | Python 3.12+ |
| Install | `pip install -r requirements.txt` (uv optional) |
| Agent | LangGraph (swappable) |
| LLM | Groq preferred (`GROQ_API_KEY`), else OpenAI-compatible |
| API | FastAPI |
| Retrieval | In-memory synthetic JSON (not pgvector) |
| CI | GitHub Actions |
| Metrics | Prometheus `/metrics` |
| Declaration | Semantic Harness JSON-LD |

---

## Explicit non-goals

- Real PHI / HIPAA-covered production system  
- Full EHR integration  
- Another agent framework  
- Closure Apps / Semantic UI coupling  
- Giant application UI  

---

## Naming (locked)

**agentic-governance** — Enterprise Agentic AI SDLC Reference Architecture.  
LangGraph is an implementation detail; governance is the product.
