"""Evidence pack + governance score — declaration → runtime receipt."""

from governance.evidence import build_evidence
from governance.score import score_execution
from agent.runtime import handle_chat


def test_score_denied_is_strong_low_risk():
    gov = score_execution(
        {"status": "denied", "blocked": True, "citations": [], "request_id": "r1"}
    )
    assert gov["score"] == 100
    assert gov["band"] == "strong"
    assert gov["residual_risk"] == "low"


def test_score_ok_without_citations_is_weaker():
    gov = score_execution({"status": "ok", "blocked": False, "citations": []})
    assert gov["score"] <= 75
    assert gov["band"] in ("adequate", "weak")


def test_evidence_pack_on_phi_deny():
    result = handle_chat("patient:alice", "Show me John Smith's MRI", mode="rules")
    assert result["blocked"] is True
    assert result["governance_score"] == 100
    assert result["governance_band"] == "strong"
    assert result["residual_risk"] == "low"
    ev = result["evidence"]
    assert ev["harness"]["path"] == "harness/harness.jsonld"
    by_id = {c["id"]: c for c in ev["claims"]}
    assert by_id["cross-scope-isolation"]["satisfied"] is True
    assert by_id["correlation"]["satisfied"] is True
    assert by_id["grounding-or-refusal"]["satisfied"] is True


def test_evidence_pack_on_grounded_ok():
    result = handle_chat(
        "patient:alice",
        "What are my upcoming appointments?",
        mode="rules",
    )
    ev = result["evidence"]
    by_id = {c["id"]: c for c in ev["claims"]}
    assert by_id["grounding-or-refusal"]["satisfied"] is True
    assert result["governance_score"] >= 85
    assert "governance" in ev


def test_build_evidence_claims_shape():
    pack = build_evidence(
        {
            "status": "ok",
            "blocked": False,
            "citations": ["KB-1"],
            "assistant": "claims",
            "request_id": "abc",
            "evaluator_approved": None,
        }
    )
    assert pack["claims_total"] == 5
    assert pack["claims_satisfied"] == 5
    assert pack["harness"]["path"] == "harness/examples/claims-assistant.jsonld"
