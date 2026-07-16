"""LangChain tools — always scoped to the authorized patient.

user_scope is injected via contextvars so tools never receive a free-form
patient id from the model (prevents prompt-injection privilege escalation).
"""

from __future__ import annotations

import json
from contextvars import ContextVar
from typing import Any

from langchain_core.tools import tool

from knowledge.synthetic import get_patient, retrieve_for_scope

# Set by the graph runner before invoking the agent.
user_scope_var: ContextVar[str] = ContextVar("user_scope", default="")
_citations_var: ContextVar[list[str]] = ContextVar("citations", default=[])


def set_request_scope(scope: str) -> None:
    user_scope_var.set(scope)
    _citations_var.set([])


def get_citations() -> list[str]:
    return list(_citations_var.get())


def _record_citations(docs: list[dict[str, Any]]) -> None:
    cites = _citations_var.get()
    for d in docs:
        doc_id = d.get("doc_id")
        if doc_id and doc_id not in cites:
            cites.append(doc_id)
    _citations_var.set(cites)


@tool
def retrieve_records(query: str) -> str:
    """Retrieve authorized synthetic patient records (appointments, notes, imaging).

    Only returns records for the authenticated user's patient scope.
    Use for questions about appointments, visit notes, or imaging.
    """
    scope = user_scope_var.get()
    if not scope:
        return json.dumps({"error": "no_authorized_scope", "documents": []})

    docs = retrieve_for_scope(scope, query)
    _record_citations(docs)
    return json.dumps(
        {
            "patient_scope": scope,
            "count": len(docs),
            "documents": [
                {"doc_id": d["doc_id"], "kind": d["kind"], "text": d["text"]} for d in docs
            ],
        }
    )


@tool
def schedule_appointment(date: str, appointment_type: str, provider: str = "Dr. Martinez") -> str:
    """Schedule a synthetic appointment for the authorized patient.

    Demo only — appends to in-memory view of the patient record for this process.
    """
    scope = user_scope_var.get()
    if not scope:
        return json.dumps({"error": "no_authorized_scope"})

    patient = get_patient(scope)
    if not patient:
        return json.dumps({"error": "patient_not_found", "scope": scope})

    appt = {"date": date, "type": appointment_type, "provider": provider}
    # Mutate loaded copy only for demo response (not persisted to disk)
    appointments = list(patient.get("appointments", []))
    appointments.append(appt)
    doc_id = f"{scope}:appt:{date}"
    cites = _citations_var.get()
    if doc_id not in cites:
        cites.append(doc_id)
        _citations_var.set(cites)

    return json.dumps(
        {
            "status": "scheduled",
            "patient_scope": scope,
            "appointment": appt,
            "doc_id": doc_id,
            "note": "Synthetic demo — not persisted to EHR",
        }
    )


@tool
def summarize_visit(focus: str = "latest") -> str:
    """Summarize authorized visit notes for the authenticated patient."""
    scope = user_scope_var.get()
    if not scope:
        return json.dumps({"error": "no_authorized_scope"})

    patient = get_patient(scope)
    if not patient:
        return json.dumps({"error": "patient_not_found", "scope": scope})

    notes = [
        {
            "doc_id": f"{scope}:note:{n['date']}",
            "kind": "visit_note",
            "text": f"Visit note {n['date']}: {n['summary']}",
        }
        for n in patient.get("visit_notes", [])
    ]
    _record_citations(notes)

    if not notes:
        return json.dumps(
            {
                "status": "no_notes",
                "message": "No visit notes available for this patient.",
                "documents": [],
            }
        )

    if focus != "latest":
        notes = [n for n in notes if focus.lower() in n["text"].lower()] or notes

    return json.dumps(
        {
            "status": "ok",
            "patient_scope": scope,
            "summaries": [{"doc_id": n["doc_id"], "text": n["text"]} for n in notes],
        }
    )


ALL_TOOLS = [retrieve_records, schedule_appointment, summarize_visit]
