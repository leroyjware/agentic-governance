# Contributing

Thank you for helping establish thought leadership in agentic AI governance.

## What to contribute

| Area | Examples |
|------|----------|
| Evaluation suites | New PHI / grounding / hallucination scenarios |
| Governance patterns | Authorization rules, guardrail checks |
| Harness declarations | Agents, tools, policies, invariants |
| Docs | Keep claims aligned with CI — update [PLAN.md](PLAN.md) |
| CI gates | New gates with an entry in [docs/AI-SDLC.md](docs/AI-SDLC.md) |

## Development setup

```bash
git clone https://github.com/leroyjware/agentic-governance
cd agentic-governance
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make gate
```

## Pull request requirements

1. `make gate` passes
2. No real PHI — synthetic data only (`SYN-MRN-*`)
3. If you add a CI gate, document it under **Shipped** in `docs/AI-SDLC.md` and update the README diagram
4. If you defer work, add it under **Next** in `PLAN.md` — do not leave stale “Phase N” READMEs

## Philosophy

- **Governance over demo** — every PR should strengthen trust
- **Harness-first** — declare policy/invariants before enforcing them
- **LangGraph is swappable** — do not couple governance to one orchestrator
- **One living plan** — `PLAN.md` only; archives belong in git history

See [PLAN.md](PLAN.md) and [AUDIT.md](AUDIT.md).
