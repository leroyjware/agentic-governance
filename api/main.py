"""FastAPI — governance middleware chain + LangGraph / rules agent."""

from __future__ import annotations

import os
import time
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field

from agent.llm import llm_configured
from agent.runtime import handle_chat, resolve_mode, use_langgraph
from governance import audit
from observability import metrics

app = FastAPI(
    title="Agentic Governance",
    description=(
        "Healthcare appointment assistant — synthetic data, real governance. "
        "LangGraph when OPENAI_API_KEY/GROQ_API_KEY set; rule-based planner for CI."
    ),
    version="0.2.0",
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_scope: str = Field(..., description="e.g. patient:alice")
    mode: Literal["auto", "graph", "rules"] | None = Field(
        default=None,
        description="auto (default) | graph (require LLM) | rules (CI deterministic)",
    )


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    status: str
    blocked: bool = False
    reason: str | None = None
    engine: str | None = None


@app.get("/health")
def health() -> dict:
    mode = resolve_mode()
    try:
        active = use_langgraph(mode)
    except RuntimeError:
        active = False
    return {
        "status": "ok",
        "agent_mode": mode,
        "llm_configured": llm_configured(),
        "langgraph_active": active,
        "version": "0.2.0",
    }


@app.get("/metrics")
def prometheus_metrics() -> Response:
    body, content_type = metrics.metrics_body()
    return Response(content=body, media_type=content_type)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    start = time.perf_counter()
    # Allow env AGENT_MODE override when request omits mode
    mode = req.mode
    if mode is None and os.getenv("AGENT_MODE"):
        mode = resolve_mode()  # type: ignore[assignment]

    result = handle_chat(req.user_scope, req.message, mode=mode)

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
        engine=result.get("engine"),
    )


@app.get("/audit")
def audit_log(limit: int = Query(default=50, ge=1, le=500)) -> dict:
    events = audit.get_events()
    return {"events": events[-limit:], "count": len(events)}
