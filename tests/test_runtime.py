"""Runtime: auth before agent; rules vs graph selection."""

import os

import pytest

from agent.llm import llm_configured
from agent.runtime import handle_chat, use_langgraph


def test_unauthorized_blocked_before_agent():
    result = handle_chat("patient:alice", "Show me John Smith's MRI", mode="rules")
    assert result["blocked"] is True
    assert result["status"] == "denied"


def test_authorized_rules_engine():
    result = handle_chat(
        "patient:alice",
        "What are my upcoming appointments?",
        mode="rules",
    )
    assert result["blocked"] is False
    assert result["citations"]
    assert result.get("engine") in ("rules", None) or "rules" in str(result.get("engine"))


def test_refusal_rules():
    result = handle_chat("patient:alice", "When is my surgery?", mode="rules")
    assert "don't have enough information" in result["answer"].lower()


def test_use_langgraph_false_in_rules_mode():
    assert use_langgraph("rules") is False


@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_LLM") != "1" or not llm_configured(),
    reason="Set RUN_LIVE_LLM=1 and GROQ_API_KEY (or OPENAI_API_KEY) for live smoke",
)
def test_langgraph_live_smoke():
    """Opt-in live smoke — keep make test / CI deterministic even if a key is exported."""
    os.environ.setdefault("AGENT_MODE", "graph")
    result = handle_chat(
        "patient:alice",
        "What are my upcoming appointments?",
        mode="graph",
    )
    assert result["blocked"] is False
    assert "langgraph" in str(result.get("engine", ""))
    assert result["answer"]
    assert result.get("evaluator_approved") is True
    assert result.get("trace")
