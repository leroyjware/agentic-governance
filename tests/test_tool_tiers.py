"""Tool tiers + evaluator replan routing (no LLM)."""

from agent.workflow import _after_evaluate, reset_workflow_cache
from governance.tool_tiers import WRITE_TOOLS, filter_tools_for_intent


def test_write_tools_only_for_schedule_intent():
    base = {"retrieve_records", "schedule_appointment", "summarize_visit"}
    assert "schedule_appointment" not in filter_tools_for_intent(base, "appointments")
    assert "schedule_appointment" not in filter_tools_for_intent(base, "imaging")
    assert "schedule_appointment" in filter_tools_for_intent(base, "schedule")
    assert WRITE_TOOLS == {"schedule_appointment"}


def test_after_evaluate_replans_once():
    assert _after_evaluate({"evaluator_approved": True, "retry_count": 0}) == "finalize"
    assert _after_evaluate({"evaluator_approved": False, "retry_count": 0}) == "plan"
    assert _after_evaluate({"evaluator_approved": False, "retry_count": 1}) == "finalize"


def test_rules_planner_schedule_uses_write_tier():
    from agent.planner import run_planner

    result = run_planner(
        "patient:alice",
        "Please schedule an appointment on 2026-08-01 for a checkup",
    )
    assert result["blocked"] is False
    assert result.get("intent") == "schedule"
    assert result.get("write_tools") is True
    assert result["citations"]


def test_rules_planner_read_path_no_write_flag():
    from agent.planner import run_planner

    result = run_planner("patient:alice", "What are my upcoming appointments?")
    assert result["blocked"] is False
    assert result.get("write_tools") is False


def test_workflow_compiles_with_replan_edge():
    reset_workflow_cache()
    from agent.workflow import build_workflow

    g = build_workflow()
    assert g is not None
