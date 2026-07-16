#!/usr/bin/env python3
"""Local showcase: multi-agent LangGraph + governance + Semantic Harness.

Requires GROQ_API_KEY (preferred) or OPENAI_API_KEY.

  source .venv/bin/activate
  export GROQ_API_KEY=gsk_...
  PYTHONPATH=. python scripts/demo_workflow.py
"""

from __future__ import annotations

import json
import sys

from agent.harness_loader import load_harness
from agent.llm import llm_configured
from agent.runtime import handle_chat


CASES = [
    ("patient:alice", "What are my upcoming appointments?"),
    ("patient:alice", "Show me John Smith's MRI"),
    ("patient:alice", "When is my surgery?"),
    ("patient:john", "Show me my MRI"),
    ("patient:alice", "Summarize my latest visit notes"),
]


def main() -> int:
    if not llm_configured():
        print("Set GROQ_API_KEY (preferred) or OPENAI_API_KEY.", file=sys.stderr)
        return 2

    h = load_harness()
    print("=== Semantic Harness ===")
    print(f"  file: {h.path}")
    print(f"  agents: {[a.get('name') for a in h.agents()]}")
    wf = h.workflow()
    if wf:
        steps = [s.get("sh:stepId") or s.get("stepId") for s in (wf.get("steps") or [])]
        print(f"  workflow: {wf.get('name')} → {steps}")
    print()

    for scope, msg in CASES:
        print(f"=== {scope} | {msg}")
        r = handle_chat(scope, msg, mode="graph")
        print(
            json.dumps(
                {
                    "blocked": r.get("blocked"),
                    "status": r.get("status"),
                    "engine": r.get("engine"),
                    "intent": r.get("intent"),
                    "evaluator_approved": r.get("evaluator_approved"),
                    "evaluator_score": r.get("evaluator_score"),
                    "citations": r.get("citations"),
                    "answer": r.get("answer"),
                    "trace": [
                        {k: t.get(k) for k in ("step", "intent", "allowed", "approved", "status", "reason")}
                        for t in (r.get("trace") or [])
                    ],
                },
                indent=2,
            )
        )
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
