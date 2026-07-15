"""Prometheus metrics for governance observability."""

from __future__ import annotations

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUESTS = Counter("agent_requests_total", "Total agent requests", ["status"])
PHI_BLOCKS = Counter("agent_phi_violations_total", "Unauthorized PHI access attempts blocked")
REFUSALS = Counter("agent_refusals_total", "Responses refused due to missing context")
LATENCY = Histogram("agent_request_latency_seconds", "Request latency seconds")


def record_request(status: str) -> None:
    REQUESTS.labels(status=status).inc()


def record_phi_block() -> None:
    PHI_BLOCKS.inc()


def record_refusal() -> None:
    REFUSALS.inc()


def metrics_body() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
