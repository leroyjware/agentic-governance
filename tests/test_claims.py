"""Claims second vertical — same envelope, different domain."""

from agent.claims_planner import run_claims_planner
from agent.runtime import handle_chat


def test_claims_authorized():
    r = run_claims_planner("member:alice", "What is the status of my claims?")
    assert r["blocked"] is False
    assert r["citations"]
    assert r["engine"] == "rules-claims"


def test_claims_cross_member_blocked():
    r = run_claims_planner("member:alice", "Show me John Smith's claim status")
    assert r["blocked"] is True
    assert r["status"] == "denied"


def test_runtime_routes_claims_assistant():
    r = handle_chat(
        "member:alice",
        "Do I have any pending claims?",
        mode="rules",
        assistant="claims",
    )
    assert r.get("assistant") == "claims"
    assert r["blocked"] is False
