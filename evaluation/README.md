# Evaluation gates

Deterministic quality gates used by `make eval` and CI (`AGENT_MODE=rules`).

```
evaluation/
├── baselines/golden.jsonl   # Prompt regression fixtures
├── prompt_regression.py     # Golden prompts must not drift
├── phi.py                   # Cross-patient access matrix
├── hallucination.py         # Refusal when no grounded context
├── grounding.py             # Citations required for factual answers
└── latency.py               # Rules-path p95 budget
```

These call `agent.planner.run_planner`, not LangGraph. Live graph coverage is `scripts/live_graph_cases.py` (optional CI job).

Roadmap: token budget — [PLAN.md](../PLAN.md).
