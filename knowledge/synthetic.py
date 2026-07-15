"""Synthetic patient store — in-memory, no real PHI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DATA = Path(__file__).parent / "data" / "patients.json"


def load_patients() -> list[dict[str, Any]]:
    return json.loads(_DATA.read_text())


def get_patient(patient_id: str) -> dict[str, Any] | None:
    for p in load_patients():
        if p["patient_id"] == patient_id:
            return p
    return None


def retrieve_for_scope(patient_id: str, query: str) -> list[dict[str, Any]]:
    """Return documents only for the authorized patient scope."""
    patient = get_patient(patient_id)
    if not patient:
        return []

    docs: list[dict[str, Any]] = []
    q = query.lower()

    for appt in patient.get("appointments", []):
        docs.append({
            "doc_id": f"{patient_id}:appt:{appt['date']}",
            "patient_id": patient_id,
            "kind": "appointment",
            "text": f"{patient['display_name']} has {appt['type']} on {appt['date']} with {appt['provider']}.",
        })

    for note in patient.get("visit_notes", []):
        docs.append({
            "doc_id": f"{patient_id}:note:{note['date']}",
            "patient_id": patient_id,
            "kind": "visit_note",
            "text": f"Visit note {note['date']}: {note['summary']}",
        })

    for img in patient.get("imaging", []):
        docs.append({
            "doc_id": f"{patient_id}:img:{img['date']}",
            "patient_id": patient_id,
            "kind": "imaging",
            "text": f"{img['type']} ({img['region']}, {img['date']}): {img['summary']}",
        })

    if any(k in q for k in ("appointment", "schedule", "upcoming", "visit")):
        return [d for d in docs if d["kind"] == "appointment"]
    if any(k in q for k in ("mri", "imaging", "scan", "x-ray")):
        return [d for d in docs if d["kind"] == "imaging"]
    if any(k in q for k in ("note", "summary", "chart")):
        return [d for d in docs if d["kind"] in ("visit_note", "imaging")]

    return docs
