#!/usr/bin/env python3
"""Prompt regression — golden prompts must not drift on the rules path.

Fails CI if status/blocked/citations/intent expectations regress.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent.planner import run_planner
from governance import audit

GOLDEN = Path(__file__).parent / "baselines" / "golden.jsonl"


def load_cases() -> list[dict]:
    cases = []
    for line in GOLDEN.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cases.append(json.loads(line))
    return cases


def check_case(case: dict, result: dict) -> list[str]:
    errors: list[str] = []
    if result.get("blocked") != case.get("expect_blocked"):
        errors.append(f"blocked={result.get('blocked')} want {case.get('expect_blocked')}")
    if case.get("expect_status") and result.get("status") != case["expect_status"]:
        errors.append(f"status={result.get('status')} want {case['expect_status']}")
    if case.get("require_citations") and not result.get("citations"):
        errors.append("missing citations")
    if case.get("expect_intent") and result.get("intent") != case["expect_intent"]:
        errors.append(f"intent={result.get('intent')} want {case['expect_intent']}")
    return errors


def run() -> dict:
    audit.clear_events()
    cases = load_cases()
    failures = []
    passed = 0
    for case in cases:
        result = run_planner(case["user_scope"], case["message"])
        errs = check_case(case, result)
        if errs:
            failures.append({"id": case.get("id"), "errors": errs, "result": {
                "status": result.get("status"),
                "blocked": result.get("blocked"),
                "intent": result.get("intent"),
                "citations": result.get("citations"),
            }})
        else:
            passed += 1
    total = len(cases)
    return {
        "gate": "prompt_regression",
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
        print(f"Prompt regression: {report['passed']}/{report['scenarios']} passed")
        for f in report["failures"]:
            print(f"  FAIL {f['id']}: {f['errors']}")
    sys.exit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
