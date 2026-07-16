# Agent — multi-agent LangGraph + Semantic Harness

**Status: shipped**

```
agent/
├── harness_loader.py   # Load harness/harness.jsonld (declare → query)
├── workflow.py         # StateGraph: authorize→route→plan→evaluate→finalize
├── graph.py            # Entrypoint → workflow
├── runtime.py          # auto|graph|rules mode switch
├── planner.py          # Deterministic rules engine (CI)
├── tools.py            # Scoped LangChain tools
├── llm.py              # Groq / OpenAI factory
└── prompts/            # Legacy single-prompt file (workflow uses harness)
```

## How Semantic Harness drives this

| Harness object | Runtime |
|----------------|---------|
| `sh:Agent` (Router, Planner, Evaluator) | Prompts + models via `harness_loader` |
| `sh:Skill` | Appended into agent system prompts |
| `sh:Tool` + policy allowlist | Planner tool filter |
| `sh:Workflow` steps | Graph topology in `workflow.py` |
| `sh:Invariant` | `evaluation/*` + CI |

**Declare in JSON-LD. Execute in LangGraph. Prove with gates.**

## Add an agent

1. Add `sh:Agent` (+ skill) to `harness/harness.jsonld`
2. Implement `node_youragent(state)` in `workflow.py`
3. Register in `NODE_REGISTRY` and add edges
4. `PYTHONPATH=. python scripts/demo_workflow.py`

## Local

See [docs/LOCAL.md](../docs/LOCAL.md).
