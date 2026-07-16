#!/usr/bin/env python3
"""Structural harness validation — always available in CI (no Node sibling required).

For full Semantic Harness CLI validation when semantic-runtimes is checked out:
  make validate-harness
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "harness" / "harness.jsonld"

REQUIRED_TYPES = {
    "sh:Harness",
    "sh:Agent",
    "sh:Workflow",
    "sh:Tool",
    "sh:Policy",
    "sh:Invariant",
    "sh:Metric",
}


def main() -> int:
    data = json.loads(HARNESS.read_text(encoding="utf-8"))
    if "@context" not in data:
        print("FAIL: missing @context", file=sys.stderr)
        return 1
    graph = data.get("@graph") or []
    if not graph:
        print("FAIL: empty @graph", file=sys.stderr)
        return 1

    by_type: dict[str, list[dict]] = {}
    by_id: dict[str, dict] = {}
    for obj in graph:
        if not isinstance(obj, dict) or "@id" not in obj or "@type" not in obj:
            print("FAIL: object missing @id/@type", file=sys.stderr)
            return 1
        t = obj["@type"]
        by_type.setdefault(t, []).append(obj)
        by_id[obj["@id"]] = obj

    missing = sorted(REQUIRED_TYPES - set(by_type))
    if missing:
        print(f"FAIL: missing types: {missing}", file=sys.stderr)
        return 1

    # Workflow step agents/tools must resolve
    for wf in by_type["sh:Workflow"]:
        for step in wf.get("sh:steps") or []:
            ref = step.get("sh:agentRef") or step.get("sh:toolRef")
            if ref and ref not in by_id:
                print(f"FAIL: workflow step refs unknown id {ref}", file=sys.stderr)
                return 1

    # Policy allowlist entries must resolve to tools
    for pol in by_type["sh:Policy"]:
        for ref in pol.get("sh:allowlist") or []:
            if ref not in by_id:
                print(f"FAIL: policy allowlist unknown id {ref}", file=sys.stderr)
                return 1

    # Agent hasTool refs must resolve
    for agent in by_type["sh:Agent"]:
        for ref in agent.get("sh:hasTool") or []:
            if ref not in by_id:
                print(f"FAIL: agent {agent.get('sh:name')} hasTool unknown {ref}", file=sys.stderr)
                return 1

    agents = [a.get("sh:name") for a in by_type["sh:Agent"]]
    print(
        f"PASS {HARNESS.relative_to(ROOT)} — "
        f"{len(graph)} objects, agents={agents}, "
        f"policies={len(by_type['sh:Policy'])}, invariants={len(by_type['sh:Invariant'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
