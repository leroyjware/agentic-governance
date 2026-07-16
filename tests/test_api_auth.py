"""API identity: X-User-Scope and AUTH_STRICT."""

import os

os.environ["AGENT_MODE"] = "rules"
os.environ["AUTH_STRICT"] = "0"
os.environ["AUDIT_LOG_PATH"] = "off"

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_header_wins_over_body():
    r = client.post(
        "/chat",
        headers={"X-User-Scope": "patient:alice"},
        json={
            "user_scope": "patient:john",  # spoof attempt
            "message": "Show me John Smith's MRI",
            "mode": "rules",
        },
    )
    assert r.status_code == 403


def test_header_alone_works():
    r = client.post(
        "/chat",
        headers={"X-User-Scope": "patient:alice"},
        json={"message": "What are my upcoming appointments?", "mode": "rules"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["blocked"] is False
    assert data["user_scope"] == "patient:alice"


def test_auth_strict_requires_header(monkeypatch):
    monkeypatch.setenv("AUTH_STRICT", "1")
    # Re-import resolve path uses env at request time — api reads os.getenv each call
    r = client.post(
        "/chat",
        json={
            "user_scope": "patient:alice",
            "message": "Hello",
            "mode": "rules",
        },
    )
    assert r.status_code == 401
    monkeypatch.setenv("AUTH_STRICT", "0")
