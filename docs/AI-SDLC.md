# AI SDLC — Quality Gates

The CI pipeline is a core artifact of this repository. This doc distinguishes **shipped gates** (fail the PR today) from **planned gates** (roadmap only).

Living tracker: [PLAN.md](../PLAN.md).

---

## Shipped pipeline (`.github/workflows/ci.yml`)

```mermaid
flowchart TD
  A[Commit] --> B[Lint]
  B --> C[Harness validate]
  C --> D[Static PHI hygiene]
  D --> E[Unit + API tests]
  E --> F[Grounding]
  F --> G[Hallucination]
  G --> H[PHI leakage]
  H --> I[Latency]
  I --> J{Secrets?}
  J -->|GROQ_API_KEY| K[Live LangGraph cases]
  J -->|none| L[Skip live]
  K --> M[Merge allowed if green]
  L --> M
```

| Gate | Command | Pass criteria |
|------|---------|---------------|
| Lint | `make lint` | ruff clean, or `compileall` |
| Harness validate | `python scripts/validate_harness.py` | Required types + refs resolve |
| PHI hygiene | `python scripts/static_phi_hygiene.py` | No SSN-like / non-SYN MRN in fixtures |
| Unit + API | `pytest tests/ -q` | 100% pass |
| Grounding | `python evaluation/grounding.py` | Citations present when expected |
| Hallucination | `python evaluation/hallucination.py` | Refusal when no context |
| PHI leakage | `python evaluation/phi.py` | All scenarios match expect_blocked |
| Latency | `python evaluation/latency.py` | Rules-path p95 under budget |
| Live LangGraph | `python scripts/live_graph_cases.py` | Optional — needs repo secret |

Eval gates use **`AGENT_MODE=rules`** (deterministic, no LLM spend). Live job exercises the real LangGraph workflow.

---

## Planned gates (not in CI yet)

Do not claim these in the README star diagram until implemented.

| Gate | Intent |
|------|--------|
| Prompt regression | Golden prompts with accuracy floor |
| Token cost budget | Avg tokens under threshold |
| Security scan | bandit + pip-audit |
| Full `harness verify` | Sibling semantic-runtimes HDD probes |
| Coverage floor | pytest-cov on `governance/` |

---

## Rule

Any **shipped** gate failure blocks merge. Waivers require an explicit PR note — do not silently skip.
