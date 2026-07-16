"""Claims vertical — rules planner inside the same governance envelope.

Proves reuse: authorize → retrieve scoped claims → guardrails → audit.
LangGraph multi-agent remains the healthcare flagship; this vertical is
harness-declared + deterministic (CI-safe).
"""

from __future__ import annotations

from governance import audit, output_guardrails
from governance.claims_authorization import authorize
from knowledge.claims_store import claims_for, get_member

REFUSAL = "I don't have enough information to answer that."

_SCOPE_NAMES = {
    "member:alice": {"alice", "alice chen"},
    "member:john": {"john", "john smith"},
}


def run_claims_planner(user_scope: str, message: str) -> dict:
    allowed, reason = authorize(user_scope, message)
    if not allowed:
        audit.log_event(
            "governance.block",
            user_scope=user_scope,
            reason=reason,
            message=message,
            assistant="claims",
        )
        return {
            "blocked": True,
            "status": "denied",
            "reason": reason,
            "answer": "Access denied. You are not authorized to view those claims.",
            "citations": [],
            "engine": "rules-claims",
            "assistant": "claims",
        }

    q = message.lower()
    # Questions that require claim facts
    needs_facts = any(
        k in q for k in ("claim", "status", "pending", "approved", "denied", "amount", "reimburse")
    )
    docs = claims_for(user_scope, message)

    if needs_facts and not docs:
        audit.log_event("agent.refusal", user_scope=user_scope, assistant="claims")
        return {
            "blocked": False,
            "status": "refused",
            "answer": REFUSAL,
            "citations": [],
            "engine": "rules-claims",
            "assistant": "claims",
        }

    if not docs:
        member = get_member(user_scope)
        name = member["display_name"] if member else "member"
        return {
            "blocked": False,
            "status": "ok",
            "answer": f"How can I help with {name}'s synthetic claim status questions?",
            "citations": [],
            "engine": "rules-claims",
            "assistant": "claims",
        }

    # Ungrounded ask (e.g. appeal outcome not in store)
    if "appeal" in q or "lawsuit" in q:
        audit.log_event("agent.refusal", user_scope=user_scope, assistant="claims")
        return {
            "blocked": False,
            "status": "refused",
            "answer": REFUSAL,
            "citations": [],
            "engine": "rules-claims",
            "assistant": "claims",
        }

    citations = [d["doc_id"] for d in docs]
    answer = " ".join(d["text"] for d in docs)
    if citations:
        answer += f" [sources: {', '.join(citations)}]"

    names = _SCOPE_NAMES.get(user_scope, set())
    safe, guard_reason = output_guardrails.scan_response(answer, names, user_scope=None)
    if not safe:
        audit.log_event("governance.block", user_scope=user_scope, reason=guard_reason, assistant="claims")
        return {
            "blocked": True,
            "status": "denied",
            "reason": guard_reason,
            "answer": "Response blocked by output guardrails.",
            "citations": [],
            "engine": "rules-claims",
            "assistant": "claims",
        }

    audit.log_event("agent.response", user_scope=user_scope, citations=citations, assistant="claims")
    return {
        "blocked": False,
        "status": "ok",
        "answer": answer,
        "citations": citations,
        "engine": "rules-claims",
        "assistant": "claims",
    }
