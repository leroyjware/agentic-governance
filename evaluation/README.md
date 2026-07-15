# Evaluation framework — Phase 2

```
evaluation/
├── runner.py                 # Machine-readable JSON reports
├── hallucination/            # No-context → refusal tests
├── phi/                      # Unauthorized access scenarios
├── prompt_regression/        # Golden prompts + baseline accuracy
├── grounding/                # Citation coverage verification
├── latency/                  # p95 + token cost budgets
├── benchmarks/               # Aggregate scenario runners
└── baselines/                # Committed baseline metrics
```

Every suite produces `evaluation/reports/*.json` for CI artifacts.

See [docs/AI-SDLC.md](../docs/AI-SDLC.md) for gate pass criteria.
