# Agent (LangGraph + rules fallback)

**Status: shipped**

```
agent/
├── graph.py           # LangGraph ReAct agent (create_react_agent)
├── runtime.py         # authorize → graph|rules → guardrails → audit
├── planner.py         # Deterministic rules engine (CI / no API key)
├── tools.py           # Scoped LangChain tools
├── llm.py             # OpenAI-compatible factory (OpenAI / Groq)
├── prompts/system.md  # System doctrine
└── policies/          # Runtime policy YAML
```

## Dual mode

| Mode | When | Engine |
|------|------|--------|
| `auto` (default) | `OPENAI_API_KEY` or `GROQ_API_KEY` set | **LangGraph** |
| `auto` | no key | Rules planner |
| `graph` | key required | **LangGraph** |
| `rules` | CI / eval gates | Rules planner |

Governance always runs **before** the agent: unauthorized cross-patient requests never reach LangGraph.

## Tools (scoped via contextvars)

- `retrieve_records` — only authorized patient
- `schedule_appointment` — synthetic booking
- `summarize_visit` — visit notes

The model **cannot** pass a patient id into tools. Scope comes from the authenticated request.

## Local

```bash
pip install -r requirements.txt

# CI-safe gates (rules)
AGENT_MODE=rules make eval

# Live LangGraph (needs key)
export GROQ_API_KEY=...   # or OPENAI_API_KEY
PYTHONPATH=. python scripts/smoke_langgraph.py
make run
```
