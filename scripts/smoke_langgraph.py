#!/usr/bin/env python3
"""Live multi-agent LangGraph smoke. Requires GROQ_API_KEY or OPENAI_API_KEY."""

from __future__ import annotations

import json
import sys

from agent.llm import llm_configured
from agent.runtime import handle_chat


def main() -> int:
    if not llm_configured():
        print("Set GROQ_API_KEY or OPENAI_API_KEY first.", file=sys.stderr)
        return 2

    failures: list[str] = []

    r1 = handle_chat("patient:alice", "What are my upcoming appointments?", mode="graph")
    print(json.dumps({"case": "authorized", **_public(r1)}, indent=2))
    if r1.get("blocked"):
        failures.append("authorized request was blocked")
    if "langgraph" not in str(r1.get("engine", "")):
        failures.append(f"expected langgraph engine, got {r1.get('engine')}")
    if not r1.get("answer"):
        failures.append("empty answer")

    r2 = handle_chat("patient:alice", "Show me John Smith's MRI", mode="graph")
    print(json.dumps({"case": "phi_block", **_public(r2)}, indent=2))
    if not r2.get("blocked"):
        failures.append("cross-patient MRI was NOT blocked")
    # Must short-circuit at authorize — no planner hop
    steps = [t.get("step") for t in (r2.get("trace") or [])]
    if "plan" in steps:
        failures.append("PHI request reached planner — authorize failed to short-circuit")

    r3 = handle_chat("patient:alice", "When is my surgery?", mode="graph")
    print(json.dumps({"case": "refusal", **_public(r3)}, indent=2))
    answer = (r3.get("answer") or "").lower()
    if r3.get("blocked") and r3.get("reason") == "unauthorized_patient_access":
        failures.append("surgery question auth-blocked unexpectedly")
    elif not any(
        p in answer
        for p in (
            "don't have enough information",
            "not enough information",
            "no information",
            "cannot find",
            "don't have",
            "do not have",
            "grounding evaluator",
        )
    ):
        failures.append(f"surgery question did not refuse; answer={r3.get('answer')!r}")

    print("---")
    if failures:
        print("SMOKE FAILED:", *failures, sep="\n  - ", file=sys.stderr)
        return 1
    print("SMOKE PASSED")
    return 0


def _public(r: dict) -> dict:
    keys = (
        "blocked",
        "status",
        "engine",
        "intent",
        "evaluator_approved",
        "answer",
        "citations",
        "reason",
        "trace",
    )
    return {k: r.get(k) for k in keys}


if __name__ == "__main__":
    raise SystemExit(main())
