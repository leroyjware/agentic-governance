#!/usr/bin/env python3
"""Structural harness validation — all harness/**/*.jsonld files.

For full Semantic Harness CLI validation when semantic-runtimes is checked out:
  make validate-harness
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = ROOT / "harness"

REQUIRED_TYPES = {
    "sh:Harness",
    "sh:Agent",
    "sh:Workflow",
    "sh:Tool",
    "sh:Policy",
    "sh:Invariant",
    "sh:Metric",
}


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    if "@context" not in data:
        errors.append("missing @context")
    graph = data.get("@graph") or []
    if not graph:
        errors.append("empty @graph")
        return errors

    by_type: dict[str, list[dict]] = {}
    by_id: dict[str, dict] = {}
    for obj in graph:
        if not isinstance(obj, dict) or "@id" not in obj or "@type" not in obj:
            errors.append("object missing @id/@type")
            continue
        t = obj["@type"]
        by_type.setdefault(t, []).append(obj)
        by_id[obj["@id"]] = obj

    missing = sorted(REQUIRED_TYPES - set(by_type))
    if missing:
        errors.append(f"missing types: {missing}")

    for wf in by_type.get("sh:Workflow", []):
        for step in wf.get("sh:steps") or []:
            ref = step.get("sh:agentRef") or step.get("sh:toolRef")
            if ref and ref not in by_id:
                errors.append(f"workflow step refs unknown id {ref}")

    for pol in by_type.get("sh:Policy", []):
        for ref in pol.get("sh:allowlist") or []:
            if ref not in by_id:
                errors.append(f"policy allowlist unknown id {ref}")

    for agent in by_type.get("sh:Agent", []):
        for ref in agent.get("sh:hasTool") or []:
            if ref not in by_id:
                errors.append(f"agent {agent.get('sh:name')} hasTool unknown {ref}")

    return errors


def main() -> int:
    files = sorted(HARNESS_ROOT.rglob("*.jsonld"))
    if not files:
        print("FAIL: no harness jsonld files", file=sys.stderr)
        return 1

    failed = 0
    for path in files:
        rel = path.relative_to(ROOT)
        errs = validate_file(path)
        if errs:
            failed += 1
            print(f"FAIL {rel}", file=sys.stderr)
            for e in errs:
                print(f"  {e}", file=sys.stderr)
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            n = len(data.get("@graph") or [])
            agents = [
                o.get("sh:name")
                for o in data.get("@graph") or []
                if o.get("@type") == "sh:Agent"
            ]
            print(f"PASS {rel} — {n} objects, agents={agents}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
