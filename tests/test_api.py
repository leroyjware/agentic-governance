"""API integration tests — force rules mode so CI needs no API key."""

import os

os.environ["AGENT_MODE"] = "rules"

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert "agent_mode" in data


def test_control_plane_ui():
    r = client.get("/ui/")
    assert r.status_code == 200
    assert "Control plane" in r.text or "Agentic Governance" in r.text


def test_phi_blocked():
    r = client.post(
        "/chat",
        json={
            "user_scope": "patient:alice",
            "message": "Show me John Smith's MRI",
            "mode": "rules",
        },
    )
    data = r.json()
    assert data["blocked"] is True


def test_grounded_answer():
    r = client.post(
        "/chat",
        json={
            "user_scope": "patient:alice",
            "message": "What are my upcoming appointments?",
            "mode": "rules",
        },
    )
    data = r.json()
    assert data["blocked"] is False
    assert len(data["citations"]) > 0


def test_refusal_without_context():
    r = client.post(
        "/chat",
        json={
            "user_scope": "patient:alice",
            "message": "When is my surgery?",
            "mode": "rules",
        },
    )
    data = r.json()
    assert "don't have enough information" in data["answer"].lower()
