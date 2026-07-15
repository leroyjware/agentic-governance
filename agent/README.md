# LangGraph agent implementation — Phase 1

```
agent/
├── graph.py          # LangGraph state machine
├── planner.py        # Intent routing
├── tools.py          # retrieve_records, schedule_appointment, summarize_visit
├── prompts/          # Versioned prompt templates
└── policies/         # Runtime policy overrides (YAML)
```

**Status:** Planned — Phase 1

The orchestrator is an implementation detail. Governance lives in `governance/` and `evaluation/`.
