"""FastAPI — governed chat API + control-plane UI."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent.llm import llm_configured
from agent.runtime import handle_chat, resolve_mode, use_langgraph
from governance import audit
from governance.request_context import new_request_id
from observability import metrics

APP_VERSION = "0.6.0"
UI_DIR = Path(__file__).resolve().parents[1] / "ui"

app = FastAPI(
    title="Agentic Governance",
    description=(
        "Governed assistants on synthetic data. Healthcare (LangGraph flagship) + "
        "Claims (second vertical). Control plane at /ui. "
        "Correlation: request_id on responses, audit, and graph traces."
    ),
    version=APP_VERSION,
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_scope: str | None = Field(
        default=None,
        description="e.g. patient:alice or member:alice — ignored when X-User-Scope is set",
    )
    mode: Literal["auto", "graph", "rules"] | None = Field(
        default=None,
        description="auto | graph (healthcare+LLM) | rules",
    )
    assistant: Literal["healthcare", "claims"] = Field(
        default="healthcare",
        description="healthcare (flagship) | claims (second vertical, rules)",
    )
    request_id: str | None = Field(
        default=None,
        description="Optional client correlation id; otherwise server generates a UUID",
    )


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    status: str
    blocked: bool = False
    reason: str | None = None
    engine: str | None = None
    intent: str | None = None
    evaluator_approved: bool | None = None
    retry_count: int | None = None
    trace: list[dict] | None = None
    user_scope: str | None = None
    assistant: str | None = None
    request_id: str | None = None


def resolve_user_scope(
    body_scope: str | None,
    header_scope: str | None,
) -> str:
    strict = os.getenv("AUTH_STRICT", "0").strip() == "1"
    header = (header_scope or "").strip() or None
    body = (body_scope or "").strip() or None

    if strict:
        if not header:
            raise HTTPException(status_code=401, detail="X-User-Scope header required (AUTH_STRICT=1)")
        if body and body != header:
            raise HTTPException(status_code=403, detail="user_scope does not match X-User-Scope")
        return header

    if header:
        if body and body != header:
            raise HTTPException(status_code=403, detail="user_scope does not match X-User-Scope")
        return header
    if body:
        return body
    raise HTTPException(status_code=400, detail="user_scope or X-User-Scope required")


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/ui/")


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
        "auth_strict": os.getenv("AUTH_STRICT", "0") == "1",
        "assistants": ["healthcare", "claims"],
        "version": APP_VERSION,
    }


@app.get("/metrics")
def prometheus_metrics() -> Response:
    body, content_type = metrics.metrics_body()
    return Response(content=body, media_type=content_type)


@app.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    response: Response,
    x_user_scope: str | None = Header(default=None, alias="X-User-Scope"),
    x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
) -> ChatResponse:
    start = time.perf_counter()
    user_scope = resolve_user_scope(req.user_scope, x_user_scope)
    request_id = (req.request_id or x_request_id or "").strip() or new_request_id()

    mode = req.mode
    if mode is None and os.getenv("AGENT_MODE"):
        mode = resolve_mode()  # type: ignore[assignment]

    result = handle_chat(
        user_scope,
        req.message,
        mode=mode,
        assistant=req.assistant,
        request_id=request_id,
    )

    if result.get("blocked"):
        metrics.record_phi_block()
        metrics.record_request("blocked")
    elif result.get("status") == "refused":
        metrics.record_refusal()
        metrics.record_request("refused")
    else:
        metrics.record_request("ok")

    metrics.LATENCY.observe(time.perf_counter() - start)

    rid = result.get("request_id") or request_id
    response.headers["X-Request-Id"] = rid

    return ChatResponse(
        answer=result["answer"],
        citations=result.get("citations", []),
        status=result.get("status", "ok"),
        blocked=result.get("blocked", False),
        reason=result.get("reason"),
        engine=result.get("engine"),
        intent=result.get("intent"),
        evaluator_approved=result.get("evaluator_approved"),
        retry_count=result.get("retry_count"),
        trace=result.get("trace"),
        user_scope=user_scope,
        assistant=result.get("assistant") or req.assistant,
        request_id=rid,
    )


@app.get("/audit")
def audit_log(limit: int = Query(default=50, ge=1, le=500)) -> dict:
    events = audit.get_events(limit=limit)
    return {"events": events, "count": len(events)}


if UI_DIR.is_dir():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
