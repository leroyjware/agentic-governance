"""FastAPI — governance middleware chain."""

from __future__ import annotations

import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from agent.planner import run_planner
from governance import audit
from observability import metrics

app = FastAPI(
    title="Agentic Governance",
    description="Healthcare appointment assistant — synthetic data, real governance",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_scope: str = Field(..., description="e.g. patient:alice")


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    status: str
    blocked: bool = False
    reason: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def prometheus_metrics() -> Response:
    body, content_type = metrics.metrics_body()
    return Response(content=body, media_type=content_type)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    start = time.perf_counter()
    result = run_planner(req.user_scope, req.message)

    if result.get("blocked"):
        metrics.record_phi_block()
        metrics.record_request("blocked")
    elif result.get("status") == "refused":
        metrics.record_refusal()
        metrics.record_request("refused")
    else:
        metrics.record_request("ok")

    metrics.LATENCY.observe(time.perf_counter() - start)

    return ChatResponse(
        answer=result["answer"],
        citations=result.get("citations", []),
        status=result.get("status", "ok"),
        blocked=result.get("blocked", False),
        reason=result.get("reason"),
    )


@app.get("/audit")
def audit_log() -> dict:
    return {"events": audit.get_events()}
