"""Chat runtime — governance first, then LangGraph or rule-based planner.

Modes:
  auto   — LangGraph if API key present, else rules (default)
  graph  — require LangGraph + API key
  rules  — force deterministic planner (CI / eval gates)
"""

from __future__ import annotations

import os
from typing import Any, Literal

from agent.graph import graph_available, run_langgraph_agent
from agent.llm import llm_configured
from agent.planner import run_planner
from governance import audit, authorization, output_guardrails

Mode = Literal["auto", "graph", "rules"]

_SCOPE_NAMES = {
    "patient:alice": {"alice", "alice chen"},
    "patient:john": {"john", "john smith"},
}


def resolve_mode(explicit: Mode | None = None) -> Mode:
    if explicit:
        return explicit
    env = os.getenv("AGENT_MODE", "auto").lower()
    if env in ("auto", "graph", "rules"):
        return env  # type: ignore[return-value]
    return "auto"


def use_langgraph(mode: Mode) -> bool:
    if mode == "rules":
        return False
    if mode == "graph":
        if not graph_available():
            raise RuntimeError("LangGraph dependencies not installed. pip install -r requirements.txt")
        if not llm_configured():
            raise RuntimeError("AGENT_MODE=graph requires OPENAI_API_KEY or GROQ_API_KEY")
        return True
    # auto
    return graph_available() and llm_configured()


def handle_chat(
    user_scope: str,
    message: str,
    mode: Mode | None = None,
) -> dict[str, Any]:
    """Full request path: authorize → agent → guardrails → audit."""
    resolved = resolve_mode(mode)

    allowed, reason = authorization.authorize(user_scope, message)
    if not allowed:
        audit.log_event(
            "governance.block",
            user_scope=user_scope,
            reason=reason,
            message=message,
            engine="runtime",
        )
        return {
            "blocked": True,
            "status": "denied",
            "reason": reason,
            "answer": "Access denied. You are not authorized to view those records.",
            "citations": [],
            "engine": "runtime",
        }

    if use_langgraph(resolved):
        result = run_langgraph_agent(user_scope, message)
    else:
        # Rule-based path also authorizes — pass through by calling inner logic.
        # Avoid double-deny: run_planner re-checks auth (idempotent for allowed).
        result = run_planner(user_scope, message)
        result = {**result, "engine": result.get("engine", "rules")}

    if result.get("blocked"):
        return result

    names = _SCOPE_NAMES.get(user_scope, set())
    safe, guard_reason = output_guardrails.scan_response(result.get("answer", ""), names)
    if not safe:
        audit.log_event(
            "governance.block",
            user_scope=user_scope,
            reason=guard_reason,
            message=message,
            engine=result.get("engine"),
        )
        return {
            "blocked": True,
            "status": "denied",
            "reason": guard_reason,
            "answer": "Response blocked by output guardrails.",
            "citations": [],
            "engine": result.get("engine"),
        }

    if result.get("status") != "refused":
        audit.log_event(
            "agent.response",
            user_scope=user_scope,
            citations=result.get("citations", []),
            engine=result.get("engine"),
        )

    return result
