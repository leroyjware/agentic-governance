# LangGraph Implementation Plan

**Goal:** Ship a real LangGraph agent inside the governance envelope. Stop looking unfinished.

## Architecture (non-negotiable)

```
Request
  → authorize (governance)          # BEFORE any tool/LLM
  → LangGraph agent (if LLM key)    # OR rule-based planner (CI/no key)
  → tools call scoped retrieval     # never unscoped
  → output guardrails
  → audit + metrics
```

LangGraph is **inside** the envelope. It does not replace authorization.

## Phases

### Phase A — Core agent (this sprint)
1. `agent/tools.py` — retrieve / schedule / summarize with scope
2. `agent/prompts/system.md` — healthcare assistant doctrine
3. `agent/graph.py` — LangGraph ReAct-style tool agent
4. `agent/runtime.py` — choose graph vs rule-based
5. Keep `planner.run_planner()` as CI-safe path
6. API uses `runtime.handle_chat()`

### Phase B — Tests & CI
1. Unit tests: tools, graph compiles, auth still blocks
2. Eval gates stay on rule-based path (no key required)
3. Optional live test skipped without `OPENAI_API_KEY` / `GROQ_API_KEY`
4. CI green on every PR

### Phase C — Docs & honesty
1. agent/README matches reality
2. Root README: LangGraph shipped; rule-based = CI/demo fallback
3. Whitepaper: update “planned” → shipped with dual-mode note
