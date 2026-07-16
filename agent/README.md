# Agent (orchestrator)

**Status: shipped (rule-based planner)** — LangGraph swap-in planned.

```
agent/
└── planner.py   # authorize → scoped retrieve → answer → guardrails → audit
```

## What runs today

`planner.py` is a **deterministic, rule-based** healthcare assistant so governance and CI gates work **without API keys**.

It is intentionally not LangGraph. The point of this repo is the envelope around the agent:

```
authorization → scoped retrieval → planner → output guardrails → audit
```

Swap `run_planner()` for a LangGraph graph later; leave `governance/` and `evaluation/` unchanged.

## What is not here yet

| File | Status |
|------|--------|
| `graph.py` (LangGraph) | Planned |
| `tools.py` (LLM tool calling) | Planned |
| `prompts/` | Planned |

## Test locally

```bash
PYTHONPATH=. python3 evaluation/phi.py
PYTHONPATH=. python3 evaluation/hallucination.py
PYTHONPATH=. python3 evaluation/grounding.py
PYTHONPATH=. python3 evaluation/latency.py
```
