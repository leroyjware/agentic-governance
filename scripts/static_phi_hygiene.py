#!/usr/bin/env python3
"""Fail if committed fixtures look like real US SSN / non-synthetic MRN.

Synthetic demo data must use SYN-MRN-* (or be absent). This is hygiene, not a HIPAA scanner.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "knowledge", ROOT / "evaluation", ROOT / "agent" / "prompts"]

# US SSN-like
SSN = re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
# Bare MRN tokens that are NOT our SYN-MRN-* convention
BAD_MRN = re.compile(r"(?<!SYN-)MRN[:\s#-]*\d{5,}", re.I)


def main() -> int:
    failures: list[str] = []
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in {".json", ".jsonl", ".md", ".py", ".txt", ".yaml"}:
                continue
            # Allow regex definitions in these modules
            if path.name in {"output_guardrails.py", "static_phi_hygiene.py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = path.relative_to(ROOT)
            for m in SSN.finditer(text):
                failures.append(f"{rel}: SSN-like pattern {m.group(0)}")
            for m in BAD_MRN.finditer(text):
                failures.append(f"{rel}: non-synthetic MRN-like {m.group(0)}")

    if failures:
        print("FAIL static PHI hygiene:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("PASS static PHI hygiene (synthetic fixtures only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
