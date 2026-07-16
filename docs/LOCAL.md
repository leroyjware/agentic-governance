# Local testing — multi-agent LangGraph + governance

## What you’re testing

A **Semantic Harness–aligned** workflow executed as LangGraph:

```
authorize → route → plan (intent tool tiers) → evaluate ─┬→ finalize
                                            ↑            │
                                            └─ replan×1 ─┘
```

| Layer | Source of truth |
|-------|-----------------|
| Agents, skills, tools, policy, invariants | `harness/harness.jsonld` |
| Graph edges | `agent/workflow.py` (explicit; step IDs must match harness) |
| Trust proof | `make gate` + `make showcase` / `make live` |
| Visual | `make run` → http://localhost:8080/ui |

## Setup (once)

```bash
cd agentic-governance
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GROQ_API_KEY=gsk_...          # never commit
export GROQ_MODEL=llama-3.3-70b-versatile
```

## 1) Deterministic gates (no LLM)

```bash
make gate          # test + eval + hygiene + harness validate + lint
make showcase      # PHI → read → refuse → schedule write tier
```

## 2) Real multi-agent inference (Groq)

```bash
export GROQ_API_KEY=...
make showcase      # adds live graph step
make demo          # per-step trace
make live          # curated PHI / grounding / refusal / imaging
```

## 3) Control plane + API

```bash
make run
# open http://localhost:8080/ui
```

Presets in the UI: appointments, PHI block, refuse, schedule write, visit summary.

```bash
curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -H 'X-User-Scope: patient:alice' \
  -d '{"message":"What are my upcoming appointments?","mode":"graph"}' | jq .
```

## 4) Validate the harness

```bash
make validate-harness
```

## How Semantic Harness is used

| Declared | Runtime |
|----------|---------|
| `sh:Agent` prompts / models | Router, Planner, Evaluator nodes |
| `sh:Policy` ∩ `hasTool` | Tool allowlist |
| `sh:Workflow` step IDs | Must exist in `NODE_REGISTRY` |
| Graph edges | Hardcoded in `build_workflow()` (reviewable) |

**Harness declares. LangGraph executes. Gates prove.**

## Adding another agent

See [ADD-AN-AGENT.md](./ADD-AN-AGENT.md).

## Expected showcase outcomes

| Request | Expect |
|---------|--------|
| Alice → appointments | citations, evaluator approved (graph) |
| Alice → John’s MRI | **blocked at authorize** |
| Alice → surgery date | `status=refused` |
| John → my MRI | grounded imaging answer |
