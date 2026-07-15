"""Latency eval — planner must stay under budget."""

from __future__ import annotations

import argparse
import json
import sys
import time

from agent.planner import run_planner
from governance import audit

BUDGET_MS = 2000


def run() -> dict:
    audit.clear_events()
    times: list[float] = []

    for _ in range(20):
        start = time.perf_counter()
        run_planner("patient:alice", "What are my upcoming appointments?")
        times.append((time.perf_counter() - start) * 1000)

    times.sort()
    p95 = times[int(len(times) * 0.95)]
    return {
        "gate": "latency",
        "status": "pass" if p95 <= BUDGET_MS else "fail",
        "p95_ms": round(p95, 2),
        "budget_ms": BUDGET_MS,
        "samples": len(times),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run()
    if args.json:
        print(json.dumps(report))
    else:
        print(f"Latency p95: {report['p95_ms']}ms (budget {report['budget_ms']}ms)")
    sys.exit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
