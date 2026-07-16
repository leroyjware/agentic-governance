# Execution evidence pack

Every `/chat` response includes an **evidence** object: a per-request receipt linking outcomes to governance claims. This is **not** a legal attestation or certification.

See also: [CONTROLS-MAP.md](./CONTROLS-MAP.md), [AUDIT-SCHEMA.md](./AUDIT-SCHEMA.md).

---

## Shape

| Field | Meaning |
|-------|---------|
| `request_id` | Correlation id |
| `harness.name` / `harness.path` | Which Semantic Harness declaration applied |
| `outcomes` | status, blocked, citations, evaluator, engine, … |
| `claims[]` | Machine-checkable statements (`id`, `satisfied`, `evidence`) |
| `governance` | Score 0–100, band, residual_risk, factors |

### Claim ids (current)

| Claim | Satisfied when |
|-------|----------------|
| `authz-before-retrieval` | Request went through authorize |
| `cross-scope-isolation` | Cross-patient/member denied, or in-scope path |
| `grounding-or-refusal` | Denied/refused, or `ok` **with** citations |
| `maker-checker` | Evaluator not `false` (n/a on rules path) |
| `correlation` | `request_id` present |

---

## Governance score

| Field | Meaning |
|-------|---------|
| `score` | Control effectiveness (higher = envelope behaved correctly) |
| `band` | `strong` \| `adequate` \| `weak` |
| `residual_risk` | `low` \| `medium` \| `high` — exposure if the answer were acted on |
| `factors` | Deltas that explain the score |

A **denied** PHI attempt scores **strong / low residual risk** — controls worked.  
An `ok` answer **without citations** scores weaker.

---

## Demo

```bash
curl -s -X POST http://localhost:8080/chat \
  -H 'X-User-Scope: patient:alice' -H 'Content-Type: application/json' \
  -d '{"mode":"rules","message":"Show me John Smith'\''s MRI"}' | jq '.governance_score, .evidence.claims'
```
