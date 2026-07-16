#!/usr/bin/env python3
"""Narrative showcase — hard path inside the same governance envelope.

Runs deterministic rules cases always; adds one graph case when GROQ/OPENAI is set.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.llm import llm_configured
from agent.planner import run_planner
from agent.runtime import handle_chat
from governance import audit


def _banner(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def _show(label: str, result: dict) -> None:
    print(f"\n--- {label} ---")
    print(
        json.dumps(
            {
                "status": result.get("status"),
                "blocked": result.get("blocked"),
                "intent": result.get("intent"),
                "write_tools": result.get("write_tools"),
                "retry_count": result.get("retry_count"),
                "evaluator_approved": result.get("evaluator_approved"),
                "citations": result.get("citations"),
                "engine": result.get("engine"),
                "answer": (result.get("answer") or "")[:220],
                "trace_steps": [t.get("step") for t in (result.get("trace") or [])],
            },
            indent=2,
        )
    )


def main() -> int:
    audit.clear_events()
    os.environ.setdefault("AUDIT_LOG_PATH", "off")

    _banner("Agentic Governance — showcase (same envelope, harder path)")
    print(
        "Story: PHI blocked before LLM → grounded read → ungrounded refuse → "
        "schedule write tier → (optional) live graph replan path."
    )

    # 1) PHI — authorize wall
    r1 = run_planner("patient:alice", "Show me John Smith's MRI")
    _show("1. PHI cross-patient (authorize before any tools)", r1)
    assert r1["blocked"] is True

    # 2) Grounded read — no write tools
    r2 = run_planner("patient:alice", "What are my upcoming appointments?")
    _show("2. Grounded read (write tools stripped)", r2)
    assert r2["blocked"] is False and r2.get("write_tools") is False

    # 3) Ungrounded refuse
    r3 = run_planner("patient:alice", "When is my surgery?")
    _show("3. Ungrounded clinical ask → refuse", r3)
    assert r3["status"] == "refused"

    # 4) Schedule write tier
    r4 = run_planner(
        "patient:alice",
        "Please schedule an appointment on 2026-08-01 for a checkup",
    )
    _show("4. Schedule intent → write tool allowed", r4)
    assert r4.get("write_tools") is True and r4["blocked"] is False

    # 5) Live graph if key present
    if llm_configured():
        r5 = handle_chat(
            "patient:alice",
            "What are my upcoming appointments?",
            mode="graph",
        )
        _show("5. Live LangGraph (route→plan→evaluate→finalize)", r5)
        print("\n  Trace detail:")
        for step in r5.get("trace") or []:
            print(f"    • {step.get('step')}: { {k:v for k,v in step.items() if k != 'step'} }")
    else:
        print("\n--- 5. Live LangGraph ---")
        print("skipped (set GROQ_API_KEY to exercise route→plan→evaluate→replan)")

    _banner("Envelope held. Governance is the product.")
    print("Next: make run → open http://localhost:8080/ui")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
