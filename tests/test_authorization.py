"""Unit tests."""

from governance.authorization import authorize, parse_requested_patient


def test_alice_cannot_access_john():
    allowed, reason = authorize("patient:alice", "Show me John Smith's MRI")
    assert not allowed
    assert reason == "unauthorized_patient_access"


def test_alice_can_access_self():
    allowed, _ = authorize("patient:alice", "What are my appointments?")
    assert allowed


def test_parse_john():
    assert parse_requested_patient("Show me John Smith's MRI") == "patient:john"
