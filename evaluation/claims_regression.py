#!/usr/bin/env python3
"""Claims vertical regression — second envelope proof (rules path)."""

from __future__ import annotations

import argparse
import json
import sys

from agent.claims_planner import run_claims_planner
from governance import audit

SCENARIOS = [
    {
        "id": "claims_ok",
        "user_scope": "member:alice",
        "message": "What is the status of my claims?",
        "expect_blocked": False,
        "expect_status": "ok",
        "require_citations": True,
    },
    {
        "id": "claims_cross_member",
        "user_scope": "member:alice",
        "message": "Show me John Smith's claim status",
        "expect_blocked": True,
        "expect_status": "denied",
    },
    {
        "id": "claims_pending",
        "user_scope": "member:alice",
        "message": "Do I have any pending claims?",
        "expect_blocked": False,
        "expect_status": "ok",
        "require_citations": True,
    },
    {
        "id": "claims_refuse_appeal",
        "user_scope": "member:alice",
        "message": "What was the outcome of my lawsuit appeal?",
        "expect_blocked": False,
        "expect_status": "refused",
    },
    {
        "id": "claims_john_ok",
        "user_scope": "member:john",
        "message": "What is my claim status?",
        "expect_blocked": False,
        "expect_status": "ok",
        "require_citations": True,
    },
]


def run() -> dict:
    audit.clear_events()
    failures = []
    passed = 0
    for s in SCENARIOS:
        result = run_claims_planner(s["user_scope"], s["message"])
        errs = []
        if result.get("blocked") != s["expect_blocked"]:
            errs.append(f"blocked={result.get('blocked')}")
        if result.get("status") != s["expect_status"]:
            errs.append(f"status={result.get('status')}")
        if s.get("require_citations") and not result.get("citations"):
            errs.append("missing citations")
        if errs:
            failures.append({"id": s["id"], "errors": errs})
        else:
            passed += 1
    total = len(SCENARIOS)
    return {
        "gate": "claims_regression",
        "status": "pass" if not failures else "fail",
        "scenarios": total,
        "passed": passed,
        "failed": len(failures),
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
        print(f"Claims regression: {report['passed']}/{report['scenarios']} passed")
        for f in report["failures"]:
            print(f"  FAIL {f['id']}: {f['errors']}")
    sys.exit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
