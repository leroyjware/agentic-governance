# Evaluation gates

Deterministic quality gates used by `make eval` and CI (`AGENT_MODE=rules`).

```
evaluation/
├── baselines/golden.jsonl   # Prompt regression fixtures
├── prompt_regression.py     # Golden prompts must not drift
├── claims_regression.py     # Second vertical envelope
├── phi.py                   # Cross-patient access matrix
├── hallucination.py         # Refusal when no grounded context
├── grounding.py             # Citations required for factual answers
└── latency.py               # Rules-path p95 budget
```

Healthcare gates call `agent.planner.run_planner`. Claims calls `agent.claims_planner`. Live graph: `scripts/live_graph_cases.py` (optional CI).

Flagship complete — [PLAN.md](../PLAN.md).
