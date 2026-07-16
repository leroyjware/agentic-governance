"""Healthcare planner — rule-based for demo (LLM-swappable later)."""

from __future__ import annotations

from governance import audit, authorization, output_guardrails
from knowledge.synthetic import get_patient, retrieve_for_scope

REFUSAL = "I don't have enough information to answer that."

_SCOPE_NAMES = {
    "patient:alice": {"alice", "alice chen"},
    "patient:john": {"john", "john smith"},
}


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
    if any(k in q for k in ("appointment", "schedule", "upcoming")):
        return any(d["kind"] == "appointment" for d in docs)
    return True


def run_planner(user_scope: str, message: str) -> dict:
    """Full governance chain: authorize → retrieve → answer → guardrails."""
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
        }

    docs = retrieve_for_scope(user_scope, message)

    if needs_factual_context(message) and not docs_answer_query(docs, message):
        audit.log_event("agent.refusal", user_scope=user_scope, message=message)
        return {
            "blocked": False,
            "status": "refused",
            "answer": REFUSAL,
            "citations": [],
        }

    if not docs:
        return {
            "blocked": False,
            "status": "ok",
            "answer": "How can I help you with your appointments or visit information?",
            "citations": [],
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
        }

    audit.log_event("agent.response", user_scope=user_scope, citations=citations)
    return {
        "blocked": False,
        "status": "ok",
        "answer": answer,
        "citations": citations,
    }
