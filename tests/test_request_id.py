"""Correlation: request_id on responses and audit events."""

import os

os.environ["AGENT_MODE"] = "rules"
os.environ["AUDIT_LOG_PATH"] = "off"
os.environ["AUTH_STRICT"] = "0"

from fastapi.testclient import TestClient

from agent.runtime import handle_chat
from governance import audit
from governance.request_context import get_request_id


def test_handle_chat_returns_request_id_and_audits():
    audit.clear_events()
    rid = "11111111-2222-3333-4444-555555555555"
    result = handle_chat(
        "patient:alice",
        "Show me John Smith's MRI",
        mode="rules",
        request_id=rid,
    )
    assert result["request_id"] == rid
    assert result["blocked"] is True
    assert get_request_id() is None  # cleared after call
    events = audit.get_events()
    assert any(e.get("request_id") == rid for e in events)


def test_api_sets_request_id_header():
    from api.main import app

    client = TestClient(app)
    r = client.post(
        "/chat",
        headers={"X-User-Scope": "patient:alice", "X-Request-Id": "req-from-header"},
        json={"message": "Hello", "mode": "rules"},
    )
    assert r.status_code == 200
    assert r.headers.get("X-Request-Id") == "req-from-header"
    assert r.json()["request_id"] == "req-from-header"
