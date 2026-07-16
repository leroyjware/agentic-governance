"""Chat runtime — governance envelope around rules or multi-agent LangGraph.

Modes:
  auto   — LangGraph workflow if API key present, else rules
  graph  — require multi-agent LangGraph + API key
  rules  — deterministic planner (CI / eval gates)
"""

from __future__ import annotations

import os
from typing import Any, Literal

from agent.graph import graph_available, run_langgraph_agent
from agent.llm import llm_configured
from agent.planner import run_planner

Mode = Literal["auto", "graph", "rules"]


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
) -> dict[str, Any]:
    """
    Full request path.

    LangGraph workflow already includes authorize → route → plan → evaluate →
    guardrails. Rules path uses planner.run_planner (also authorizes).
    """
    resolved = resolve_mode(mode)

    if use_langgraph(resolved):
        return run_langgraph_agent(user_scope, message)

    # Fast deny for rules mode still goes through planner (includes auth)
    result = run_planner(user_scope, message)
    return {**result, "engine": result.get("engine") or "rules"}
