"""LangGraph module smoke tests (no API key required)."""

from agent.graph import graph_available, load_system_prompt
from agent.tools import ALL_TOOLS


def test_system_prompt_loads():
    prompt = load_system_prompt()
    assert "synthetic" in prompt.lower()
    assert "tools" in prompt.lower()


def test_tools_registered():
    names = {t.name for t in ALL_TOOLS}
    assert names == {"retrieve_records", "schedule_appointment", "summarize_visit"}


def test_graph_deps_importable():
    assert graph_available() is True
