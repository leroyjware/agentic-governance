"""Lightweight governance score — control effectiveness, not a credit rating.

Higher score = envelope behaved correctly for this request.
residual_risk = leftover exposure *if* the answer were acted on.
"""

from __future__ import annotations

from typing import Any


def score_execution(result: dict[str, Any]) -> dict[str, Any]:
    """Derive score/band/residual_risk + human-readable factors."""
    score = 100
    factors: list[dict[str, Any]] = []
    status = result.get("status") or "ok"
    blocked = bool(result.get("blocked"))
    citations = result.get("citations") or []
    approved = result.get("evaluator_approved")
    write_tools = bool(result.get("write_tools"))
    retries = int(result.get("retry_count") or 0)

    def bump(delta: int, code: str, detail: str) -> None:
        nonlocal score
        score += delta
        factors.append({"code": code, "delta": delta, "detail": detail})

    if blocked and status == "denied":
        bump(0, "authz_enforced", "Unauthorized or policy-denied path blocked before leak")
        residual = "low"
        band = "strong"
    elif status == "refused":
        bump(-5, "honest_refusal", "Refused when context insufficient (preferred over invention)")
        residual = "low"
        band = "strong"
    elif status == "ok":
        if citations:
            bump(0, "grounded", "Factual path returned citations")
        else:
            bump(-25, "ungrounded_ok", "ok status without citations — weak grounding signal")
        if approved is False:
            bump(-30, "evaluator_rejected", "Maker-checker rejected draft")
        elif approved is True:
            bump(0, "evaluator_approved", "Maker-checker approved draft")
        if write_tools:
            bump(-10, "write_tier", "Write/schedule tool path — higher autonomy")
        if retries:
            bump(-8, "replan", f"Evaluator replan count={retries}")
        residual = "medium" if write_tools or not citations else "low"
        band = "strong" if score >= 85 else "adequate" if score >= 60 else "weak"
    else:
        bump(-20, "unknown_status", f"Unexpected status={status}")
        residual = "medium"
        band = "adequate"

    score = max(0, min(100, score))
    if score < 60:
        band = "weak"
    elif score < 85 and band == "strong":
        band = "adequate"

    return {
        "score": score,
        "band": band,
        "residual_risk": residual,
        "factors": factors,
    }
