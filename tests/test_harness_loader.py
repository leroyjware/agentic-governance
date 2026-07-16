"""Semantic Harness loader — declaration must stay coherent with the workflow."""

from agent.harness_loader import load_harness
from agent.workflow import NODE_REGISTRY


def test_harness_loads_three_agents():
    h = load_harness()
    names = {a.get("name") for a in h.agents()}
    assert names == {"Router", "Healthcare Planner", "Grounding Evaluator"}


def test_workflow_steps_match_registry():
    h = load_harness()
    wf = h.workflow()
    assert wf is not None
    steps = wf.get("steps") or []
    step_ids = [s.get("sh:stepId") for s in steps]
    assert step_ids == ["authorize", "route", "plan", "evaluate"]
    for sid in step_ids:
        assert sid in NODE_REGISTRY


def test_planner_tools_from_harness():
    h = load_harness()
    agent = h.agent_by_name("Healthcare Planner")
    tools = h.tools_for(agent)
    assert "retrieve_records" in tools
    assert "schedule_appointment" in tools


def test_system_prompt_includes_skills():
    h = load_harness()
    prompt = h.system_prompt("Grounding Evaluator")
    assert "Maker never validates" in prompt or "maker" in prompt.lower()
