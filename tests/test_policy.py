"""Harness policy allowlist is enforced at runtime."""

from agent.harness_loader import load_harness
from governance import output_guardrails


def test_policy_allowlist_resolves_tools():
    h = load_harness()
    names = h.policy_tool_names()
    assert "retrieve_records" in names
    assert "schedule_appointment" in names
    assert "summarize_visit" in names


def test_planner_tools_intersect_policy():
    h = load_harness()
    allowed = h.allowed_tools_for_agent("Healthcare Planner")
    assert allowed == {"retrieve_records", "schedule_appointment", "summarize_visit"}
    assert "check_authorization" not in allowed


def test_mrn_guardrail_blocks_other_patient():
    safe, reason = output_guardrails.scan_response(
        "Your MRN is SYN-MRN-00002",
        allowed_patient_names={"alice", "alice chen"},
        user_scope="patient:alice",
    )
    assert safe is False
    assert reason == "phi_mrn_scope_violation"


def test_mrn_guardrail_allows_own():
    safe, reason = output_guardrails.scan_response(
        "Your MRN is SYN-MRN-00001",
        allowed_patient_names={"alice", "alice chen"},
        user_scope="patient:alice",
    )
    assert safe is True
    assert reason is None
