"""Outbound response guardrails."""

from __future__ import annotations

import re

# Synthetic MRN patterns only — demo guardrail
_MRN_PATTERN = re.compile(r"SYN-MRN-\d{5}")


def scan_response(text: str, allowed_patient_names: set[str]) -> tuple[bool, str | None]:
    """
    Block if response mentions another patient's identifiable info.
    Returns (safe, reason).
    """
    lower = text.lower()
    for name in ("john smith", "john's", "john "):
        if name in lower and "john" not in allowed_patient_names and "john smith" not in allowed_patient_names:
            return False, "phi_scope_violation"
    for name in ("alice chen", "alice's"):
        if name in lower and "alice" not in allowed_patient_names and "alice chen" not in allowed_patient_names:
            return False, "phi_scope_violation"
    return True, None
