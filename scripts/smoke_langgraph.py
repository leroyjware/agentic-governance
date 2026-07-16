#!/usr/bin/env python3
"""Live LangGraph smoke test. Requires OPENAI_API_KEY or GROQ_API_KEY."""

from __future__ import annotations

import json
import sys

from agent.llm import llm_configured
from agent.runtime import handle_chat


def main() -> int:
    if not llm_configured():
        print("Set OPENAI_API_KEY or GROQ_API_KEY first.", file=sys.stderr)
        return 2

    cases = [
        ("patient:alice", "What are my upcoming appointments?"),
        ("patient:alice", "Show me John Smith's MRI"),
        ("patient:alice", "When is my surgery?"),
    ]
    for scope, msg in cases:
        r = handle_chat(scope, msg, mode="graph")
        print(json.dumps({"message": msg, **{k: r[k] for k in ("blocked", "status", "engine", "answer", "citations")}}, indent=2))
        print("---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
