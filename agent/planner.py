"""Healthcare planner — rule-based for CI / no-LLM demos."""

from __future__ import annotations

import re

from governance import audit, authorization, output_guardrails
from governance.tool_tiers import WRITE_TOOLS, filter_tools_for_intent
from knowledge.synthetic import get_patient, retrieve_for_scope

REFUSAL = "I don't have enough information to answer that."

_SCOPE_NAMES = {
    "patient:alice": {"alice", "alice chen"},
    "patient:john": {"john", "john smith"},
}


def infer_intent(message: str) -> str:
    q = message.lower()
    if any(
        k in q
        for k in (
            "book ",
            "schedule an",
            "schedule me",
            "make an appointment",
            "set up an appointment",
            "schedule a ",
        )
    ):
        return "schedule"
    if any(k in q for k in ("mri", "imaging", "scan", "x-ray")):
        return "imaging"
    if any(k in q for k in ("summary", "visit note", "chart")):
        return "summary"
    if any(k in q for k in ("appointment", "upcoming", "when is my")):
        return "appointments"
    return "unknown"


def needs_factual_context(message: str) -> bool:
    q = message.lower()
    return any(
        k in q
        for k in ("surgery", "when is", "mri", "appointment", "schedule", "show me", "summary")
    )


def docs_answer_query(docs: list, message: str) -> bool:
    """True only if retrieved docs are relevant to the question (anti-hallucination)."""
    if not docs:
        return False
    q = message.lower()
    if "surgery" in q or "transplant" in q:
        return any("surgery" in d["text"].lower() or "transplant" in d["text"].lower() for d in docs)
    if any(k in q for k in ("mri", "imaging", "scan")):
        return any(d["kind"] == "imaging" for d in docs)
    if any(k in q for k in ("appointment", "upcoming")) and "schedule an" not in q:
        return any(d["kind"] == "appointment" for d in docs)
    return True


def _schedule_reply(user_scope: str, message: str) -> dict:
    """Synthetic write path — only when intent is schedule (tool tier parity)."""
    tools = filter_tools_for_intent({"retrieve_records", "schedule_appointment", "summarize_visit"}, "schedule")
    assert "schedule_appointment" in tools
    assert WRITE_TOOLS & tools

    m = re.search(r"20\d{2}-\d{2}-\d{2}", message)
    date = m.group(0) if m else "2026-08-15"
    patient = get_patient(user_scope)
    if not patient:
        return {
            "blocked": False,
            "status": "refused",
            "answer": REFUSAL,
            "citations": [],
            "intent": "schedule",
            "write_tools": True,
        }

    doc_id = f"{user_scope}:appt:{date}"
    answer = (
        f"Scheduled a synthetic appointment on {date} with Dr. Martinez "
        f"for {patient['display_name']}. [sources: {doc_id}]"
    )
    names = _SCOPE_NAMES.get(user_scope, set())
    safe, guard_reason = output_guardrails.scan_response(answer, names, user_scope=user_scope)
    if not safe:
        audit.log_event("governance.block", user_scope=user_scope, reason=guard_reason)
        return {
            "blocked": True,
            "status": "denied",
            "reason": guard_reason,
            "answer": "Response blocked by output guardrails.",
            "citations": [],
            "intent": "schedule",
        }

    audit.log_event("agent.schedule", user_scope=user_scope, doc_id=doc_id, engine="rules")
    return {
        "blocked": False,
        "status": "ok",
        "answer": answer,
        "citations": [doc_id],
        "intent": "schedule",
        "write_tools": True,
        "engine": "rules",
    }


def run_planner(user_scope: str, message: str) -> dict:
    """Full governance chain: authorize → intent tier → retrieve/schedule → guardrails."""
    allowed, reason = authorization.authorize(user_scope, message)
    if not allowed:
        audit.log_event(
            "governance.block",
            user_scope=user_scope,
            reason=reason,
            message=message,
        )
        return {
            "blocked": True,
            "status": "denied",
            "reason": reason,
            "answer": "Access denied. You are not authorized to view those records.",
            "citations": [],
            "engine": "rules",
        }

    intent = infer_intent(message)
    # Prove write tier: schedule tools only for schedule intent
    read_only = filter_tools_for_intent(
        {"retrieve_records", "schedule_appointment", "summarize_visit"},
        intent,
    )
    write_allowed = "schedule_appointment" in read_only

    if intent == "schedule":
        return _schedule_reply(user_scope, message)

    docs = retrieve_for_scope(user_scope, message)

    if needs_factual_context(message) and not docs_answer_query(docs, message):
        audit.log_event("agent.refusal", user_scope=user_scope, message=message)
        return {
            "blocked": False,
            "status": "refused",
            "answer": REFUSAL,
            "citations": [],
            "intent": intent,
            "write_tools": write_allowed,
            "engine": "rules",
        }

    if not docs:
        return {
            "blocked": False,
            "status": "ok",
            "answer": "How can I help you with your appointments or visit information?",
            "citations": [],
            "intent": intent,
            "write_tools": write_allowed,
            "engine": "rules",
        }

    citations = [d["doc_id"] for d in docs]
    answer = " ".join(d["text"] for d in docs)
    if citations:
        answer += f" [sources: {', '.join(citations)}]"

    names = _SCOPE_NAMES.get(user_scope, set())
    safe, guard_reason = output_guardrails.scan_response(
        answer, names, user_scope=user_scope
    )
    if not safe:
        audit.log_event("governance.block", user_scope=user_scope, reason=guard_reason, message=message)
        return {
            "blocked": True,
            "status": "denied",
            "reason": guard_reason,
            "answer": "Response blocked by output guardrails.",
            "citations": [],
            "intent": intent,
            "engine": "rules",
        }

    audit.log_event("agent.response", user_scope=user_scope, citations=citations)
    return {
        "blocked": False,
        "status": "ok",
        "answer": answer,
        "citations": citations,
        "intent": intent,
        "write_tools": write_allowed,
        "engine": "rules",
    }
