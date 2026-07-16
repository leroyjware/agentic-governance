# Observability

```
observability/
├── metrics.py                              # Prometheus → GET /metrics
└── grafana/agentic-governance.json         # Importable dashboard (optional)
```

**Shipped metrics:** `agent_requests_total`, `agent_phi_violations_total`, `agent_refusals_total`, `agent_request_latency_seconds`.

**Grafana:** Import `grafana/agentic-governance.json` into any Grafana that scrapes the API `/metrics` endpoint. Compose stack is deferred — [PLAN.md](../PLAN.md).
