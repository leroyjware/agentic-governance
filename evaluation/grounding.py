"""Grounding eval — factual answers must include citations."""

from __future__ import annotations

import argparse
import json
import sys

from agent.planner import run_planner
from governance import audit

SCENARIOS = [
    {"user_scope": "patient:alice", "message": "What are my upcoming appointments?"},
    {"user_scope": "patient:john", "message": "Show me my MRI"},
]


def run() -> dict:
    audit.clear_events()
    passed = 0
    failures = []

    for i, s in enumerate(SCENARIOS):
        result = run_planner(s["user_scope"], s["message"])
        has_citations = len(result.get("citations", [])) > 0
        not_blocked = not result.get("blocked")
        ok = has_citations and not_blocked and result.get("status") == "ok"
        if ok:
            passed += 1
        else:
            failures.append({"scenario": i, "result": result})

    total = len(SCENARIOS)
    citation_rate = passed / total if total else 0.0
    return {
        "gate": "grounding",
        "status": "pass" if citation_rate >= 0.95 else "fail",
        "scenarios": total,
        "passed": passed,
        "citation_rate": citation_rate,
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run()
    if args.json:
        print(json.dumps(report))
    else:
        print(f"Grounding eval: {report['passed']}/{report['scenarios']} with citations")
    sys.exit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
