# Governance layer — Phase 1

```
governance/
├── policy_engine.py      # Load harness + YAML policies
├── authorization.py      # RBAC/ABAC — auth BEFORE retrieval
├── output_guardrails.py  # PHI scan, block, redact
├── audit.py              # Structured audit events
├── quality_gates.py      # Local gate runner (CI uses evaluation/)
├── approval.py           # Human-in-loop stub — Phase 4
└── static_scan.py        # Pre-commit PHI pattern scan — Phase 2
```

**Center of the repository.** Not LangGraph.
