"""API integration tests."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_phi_blocked():
    r = client.post("/chat", json={"user_scope": "patient:alice", "message": "Show me John Smith's MRI"})
    data = r.json()
    assert data["blocked"] is True
    assert "denied" in data["status"] or data["blocked"]


def test_grounded_answer():
    r = client.post("/chat", json={"user_scope": "patient:alice", "message": "What are my upcoming appointments?"})
    data = r.json()
    assert data["blocked"] is False
    assert len(data["citations"]) > 0


def test_refusal_without_context():
    r = client.post("/chat", json={"user_scope": "patient:alice", "message": "When is my surgery?"})
    data = r.json()
    assert "don't have enough information" in data["answer"].lower()
