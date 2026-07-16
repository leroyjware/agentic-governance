# Architecture

Enterprise Agentic AI SDLC Reference Architecture — system view.

---

## System context

```mermaid
flowchart TB
  subgraph external [External]
    DEV[Developer]
    USER[End User]
    GH[GitHub Actions]
  end

  subgraph repo [agentic-governance]
    HARNESS[harness/harness.jsonld]
    EVAL[evaluation/]
    GOV[governance/]
    AGENT[agent/ LangGraph]
    API[api/ FastAPI]
    OBS[observability/]
  end

  subgraph infra [Infrastructure]
    STORE[(In-memory synthetic store)]
    PROM[Prometheus]
    GRAF[Grafana optional]
    LLM[LLM API]
  end

  DEV --> GH
  GH --> EVAL
  GH --> HARNESS
  EVAL --> GOV
  USER --> API
  API --> GOV
  GOV --> AGENT
  AGENT --> LLM
  AGENT --> STORE
  API --> OBS
  OBS --> PROM
  PROM --> GRAF
```

---

## Layered architecture

| Layer | Responsibility | Technology |
|-------|----------------|------------|
| **Declaration** | What the agent is allowed to do | Semantic Harness JSON-LD |
| **Governance** | Enforce policies at runtime + CI + evidence | Python envelope |
| **Orchestration** | Plan, retrieve, act | LangGraph or rules (swappable) |
| **Knowledge** | Synthetic records | In-memory store (not pgvector) |
| **Evaluation** | Prove trust before deploy | Pytest + eval runners |
| **Delivery** | AI SDLC pipeline | GitHub Actions |
| **Observability** | Ops posture in production | Prometheus + optional Grafana |

---

## Data flow — authorized question

1. User authenticates → role `patient`, scope `patient:alice`
2. Authorization middleware attaches scope to request context
3. Planner decides retrieval needed
4. `retrieve_records` called with scope filter → only Alice's synthetic records returned
5. Planner drafts answer with citations
6. Grounding Evaluator approves (graph path)
7. Output guardrails scan → clean
8. Audit log + evidence pack + governance score → response returned

## Data flow — unauthorized PHI attempt

1. User `patient:alice` asks "Show me John Smith's MRI"
2. Authorization denies cross-patient access **before** retrieval
3. No records returned to LLM
4. If planner hallucinates anyway, output guardrail blocks
5. Audit event with reason + `request_id`
6. Safe denial returned; evidence claim `cross-scope-isolation` satisfied
7. `agent_phi_violations_total` incremented; governance score reflects controls worked

---

## CI/CD integration

See [AI-SDLC.md](./AI-SDLC.md) for gate specifications.

Harness validation runs in CI **before** deploy — architecture and behavior stay linked.

---

## Extension points (adopter seams)

See [ADOPTERS.md](./ADOPTERS.md) and [PLAN.md](../PLAN.md).

| Extension | Status in this reference |
|-----------|--------------------------|
| JWT / OIDC identity | Deferred — demo uses `X-User-Scope` |
| pgvector / enterprise retrieval | Deferred — authorize-first seam is ready |
| Human-in-the-loop approval UI | Deferred — until a real escalation path |
| Custom verticals | Pattern shown via claims assistant |
