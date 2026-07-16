# Second vertical — Claims Status Assistant

Proves the governance envelope is **reusable**, not a one-off healthcare demo.

| Layer | Healthcare (flagship) | Claims (second vertical) |
|-------|----------------------|---------------------------|
| Harness | `harness/harness.jsonld` | `harness/examples/claims-assistant.jsonld` |
| Runtime | LangGraph multi-agent **or** rules | Rules planner (`agent/claims_planner.py`) |
| Identity scopes | `patient:alice` / `patient:john` | `member:alice` / `member:john` |
| Auth before retrieval | Yes | Yes (`governance/claims_authorization.py`) |
| CI gate | prompt / PHI / … | `evaluation/claims_regression.py` |

**Honest scope:** Claims is harness-declared + deterministic today. Full LangGraph for claims is post-flagship (see [PLAN.md](../PLAN.md)).

## Try it

```bash
curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -H 'X-User-Scope: member:alice' \
  -d '{"assistant":"claims","message":"What is the status of my claims?","mode":"rules"}'

curl -s -X POST http://localhost:8080/chat \
  -H 'Content-Type: application/json' \
  -H 'X-User-Scope: member:alice' \
  -d '{"assistant":"claims","message":"Show me John Smith'\''s claim status","mode":"rules"}'
```

Or open `/ui` → Assistant: **claims**.
