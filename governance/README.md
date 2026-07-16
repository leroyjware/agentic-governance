# Governance

Runtime trust controls — the center of this repository.

```
governance/
├── authorization.py      # Auth BEFORE retrieval (cross-patient block)
├── output_guardrails.py  # Name + SYN-MRN scope checks
└── audit.py              # In-memory events + optional JSONL (AUDIT_LOG_PATH)
```

Tool allowlists come from Semantic Harness `sh:Policy` via `agent/harness_loader.py`.

See [PLAN.md](../PLAN.md) for deferred items (JWT, human approval UI).
