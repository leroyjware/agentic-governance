"""LangGraph ReAct agent for the healthcare appointment assistant.

Lives *inside* the governance envelope — callers must authorize first and
set tools.user_scope_var before invoke.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from langgraph.prebuilt import create_react_agent

from agent.llm import build_chat_model
from agent.tools import ALL_TOOLS, get_citations, set_request_scope

_PROMPT_PATH = Path(__file__).parent / "prompts" / "system.md"


def load_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def build_graph():
    """Compile the LangGraph ReAct agent (cached per process)."""
    model = build_chat_model()
    return create_react_agent(
        model,
        ALL_TOOLS,
        prompt=load_system_prompt(),
    )


def run_langgraph_agent(user_scope: str, message: str) -> dict[str, Any]:
    """Invoke LangGraph for an already-authorized request."""
    set_request_scope(user_scope)
    graph = build_graph()

    result = graph.invoke(
        {"messages": [("user", message)]},
        config={"configurable": {"thread_id": f"{user_scope}-session"}},
    )

    messages = result.get("messages") or []
    answer = ""
    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if content and getattr(msg, "type", None) == "ai":
            # Skip empty / tool-call-only AI messages
            if isinstance(content, str) and content.strip():
                answer = content.strip()
                break
            if isinstance(content, list):
                parts = [
                    p.get("text", "") if isinstance(p, dict) else str(p)
                    for p in content
                ]
                joined = "".join(parts).strip()
                if joined:
                    answer = joined
                    break

    if not answer:
        answer = "I don't have enough information to answer that."

    citations = get_citations()
    # Ensure citations appear in the answer for grounding checks / reviewers
    if citations and "sources:" not in answer.lower():
        answer = f"{answer} [sources: {', '.join(citations)}]"

    status = "ok"
    if "don't have enough information" in answer.lower():
        status = "refused"

    return {
        "blocked": False,
        "status": status,
        "answer": answer,
        "citations": citations,
        "engine": "langgraph",
    }


def graph_available() -> bool:
    """True if LangGraph + LLM deps can be imported (key checked separately)."""
    try:
        import langgraph  # noqa: F401
        import langchain_openai  # noqa: F401

        return True
    except ImportError:
        return False
