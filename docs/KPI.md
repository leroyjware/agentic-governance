# KPI map — how we know governance is working

Two layers. Do not confuse them.

| Layer | Question | Mechanism |
|-------|----------|-----------|
| **Correctness** | Did the envelope behave as specified? | CI gates (`make gate`) |
| **Operations** | Is the running system healthy? | Prometheus `/metrics` (+ optional Grafana) |

---

## Correctness KPIs (CI — source of truth)

| Gate | Command | Pass means |
|------|---------|------------|
| Prompt regression | `evaluation/prompt_regression.py` | Golden prompts keep status / block / citations |
| PHI leakage | `evaluation/phi.py` | Cross-patient access denied |
| Hallucination | `evaluation/hallucination.py` | No-context → refusal |
| Grounding | `evaluation/grounding.py` | Factual answers cite docs |
| Latency (rules) | `evaluation/latency.py` | p95 under budget |
| Claims vertical | `evaluation/claims_regression.py` | Second vertical envelope holds |
| Harness validate | `scripts/validate_harness.py` | Declarations structurally sound |

**If CI is green, the reference behavior has not regressed.** That is the primary “working as expected” signal for a governance architecture.

---

## Runtime KPIs (Prometheus)

| Metric | Type | Governance meaning |
|--------|------|--------------------|
| `agent_requests_total{status=}` | Counter | Throughput by outcome (`ok` / `blocked` / `refused`) |
| `agent_phi_violations_total` | Counter | Unauthorized access attempts stopped |
| `agent_refusals_total` | Counter | Honest “not enough information” exits |
| `agent_request_latency_seconds` | Histogram | Envelope latency (incl. LLM when graph mode) |

### Suggested ops checks (adopter-defined SLOs)

| Signal | Healthy direction |
|--------|-------------------|
| Spike in `phi_violations` | Expected under attack/tests; investigate if correlated with `status=ok` leaks (should not happen) |
| `refused` rate | Domain-dependent; sudden drop may mean over-answering |
| Latency p95 | Graph mode will be higher than rules; alert on regressions vs your baseline |

Import `observability/grafana/agentic-governance.json` or run `make obs-up` (Prometheus + Grafana only).

---

## Not KPIs in this reference (yet)

| Gap | Status |
|-----|--------|
| Token / $ cost | Deferred — needs LLM metering |
| Online eval sampling | Deferred — use CI golden set |
| Goal-success from harness metrics | Probes exist in JSON-LD; CI runs scripts directly |

---

## Traceability (per request)

Use `request_id` to join:

1. API response / `X-Request-Id`  
2. Audit JSONL  
3. Graph `trace[]` (healthcare graph mode)

See [AUDIT-SCHEMA.md](./AUDIT-SCHEMA.md).
