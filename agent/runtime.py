"""Chat runtime — governance envelope around rules or multi-agent LangGraph.

Modes:
  auto   — LangGraph workflow if API key present, else rules
  graph  — require multi-agent LangGraph + API key (healthcare only)
  rules  — deterministic planner (CI / eval gates)

Assistants:
  healthcare — flagship (rules or LangGraph)
  claims     — second vertical (rules + harness; proves envelope reuse)
"""

from __future__ import annotations

import os
from typing import Any, Literal

from agent.claims_planner import run_claims_planner
from agent.graph import graph_available, run_langgraph_agent
from agent.llm import llm_configured
from agent.planner import run_planner
from governance.request_context import new_request_id, reset_request_id, set_request_id

Mode = Literal["auto", "graph", "rules"]
Assistant = Literal["healthcare", "claims"]


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
            raise RuntimeError("AGENT_MODE=graph requires GROQ_API_KEY or OPENAI_API_KEY")
        return True
    return graph_available() and llm_configured()


def handle_chat(
    user_scope: str,
    message: str,
    mode: Mode | None = None,
    assistant: Assistant = "healthcare",
    request_id: str | None = None,
) -> dict[str, Any]:
    """Full request path for the selected assistant. Sets request_id context."""
    rid = (request_id or "").strip() or new_request_id()
    token = set_request_id(rid)
    try:
        if assistant == "claims":
            result = run_claims_planner(user_scope, message)
            return {**result, "assistant": "claims", "request_id": rid}

        resolved = resolve_mode(mode)

        if use_langgraph(resolved):
            result = run_langgraph_agent(user_scope, message, request_id=rid)
            return {**result, "assistant": "healthcare", "request_id": rid}

        result = run_planner(user_scope, message)
        return {
            **result,
            "engine": result.get("engine") or "rules",
            "assistant": "healthcare",
            "request_id": rid,
        }
    finally:
        reset_request_id(token)
