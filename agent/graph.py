"""LangGraph entrypoint — multi-agent workflow."""

from __future__ import annotations

from typing import Any

from agent.workflow import run_workflow


def run_langgraph_agent(
    user_scope: str,
    message: str,
    request_id: str | None = None,
) -> dict[str, Any]:
    """Run the harness-aligned multi-agent LangGraph workflow."""
    return run_workflow(user_scope, message, request_id=request_id)


def graph_available() -> bool:
    try:
        import langgraph  # noqa: F401
        import langchain_openai  # noqa: F401

        return True
    except ImportError:
        return False
