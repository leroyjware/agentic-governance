# Contributing

Thank you for helping establish thought leadership in agentic AI governance.

## What to contribute

| Area | Examples |
|------|----------|
| **Evaluation suites** | New PHI scenarios, grounding cases, vertical-specific tests |
| **Governance patterns** | Authorization models, output guardrail rules |
| **Harness declarations** | New example agents with invariants + probes |
| **Docs** | Architecture patterns, interview scenarios, comparisons |
| **CI gates** | New quality gates with documented fail criteria |

## Development setup

```bash
git clone https://github.com/leroyjware/agentic-governance
cd agentic-governance
uv sync --all-extras
make validate-harness
```

## Pull request requirements

1. `make validate-harness` passes
2. `make lint` passes (when code exists)
3. New eval suites include JSON report format
4. No real PHI — synthetic data only
5. Document new gates in `docs/AI-SDLC.md`

## Philosophy

- **Governance over demo** — every PR should strengthen trust, not just features
- **Harness-first** — declare invariants before implementing enforcement
- **LangGraph is swappable** — don't couple governance to one orchestrator

See [PLAN.md](PLAN.md) for roadmap phases.
