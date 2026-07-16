# CI — AI SDLC

Workflow: [`ci.yml`](./ci.yml)

| Job | Requires secret? | Purpose |
|-----|------------------|---------|
| `governance-gates` | No | Lint, harness validate, hygiene, tests, eval gates |
| `live-langgraph` | Optional `GROQ_API_KEY` | Real multi-agent cases |

Gate definitions: [docs/AI-SDLC.md](../../docs/AI-SDLC.md). Roadmap: [PLAN.md](../../PLAN.md).
