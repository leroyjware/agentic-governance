"""Tool scope tests — model cannot escape authorized patient."""

import json

from agent.tools import get_citations, retrieve_records, set_request_scope, summarize_visit


def test_retrieve_scoped_to_alice():
    set_request_scope("patient:alice")
    raw = retrieve_records.invoke({"query": "upcoming appointments"})
    data = json.loads(raw)
    assert data["patient_scope"] == "patient:alice"
    assert data["count"] >= 1
    assert all("alice" in d["doc_id"] for d in data["documents"])
    assert get_citations()


def test_retrieve_john_mri_for_john_scope():
    set_request_scope("patient:john")
    raw = retrieve_records.invoke({"query": "MRI imaging"})
    data = json.loads(raw)
    assert data["count"] >= 1
    assert any(d["kind"] == "imaging" for d in data["documents"])


def test_summarize_alice():
    set_request_scope("patient:alice")
    raw = summarize_visit.invoke({"focus": "latest"})
    data = json.loads(raw)
    assert data["status"] == "ok"
