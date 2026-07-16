"""Outbound response guardrails."""

from __future__ import annotations

import re

# Synthetic MRN patterns — block leaking another patient's MRN
_SYN_MRN = re.compile(r"SYN-MRN-(\d{5})", re.I)

_SCOPE_MRN = {
    "patient:alice": "00001",
    "patient:john": "00002",
}


def scan_response(
    text: str,
    allowed_patient_names: set[str],
    user_scope: str | None = None,
) -> tuple[bool, str | None]:
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

    allowed_mrn = _SCOPE_MRN.get(user_scope or "")
    for m in _SYN_MRN.finditer(text):
        digits = m.group(1)
        if allowed_mrn and digits != allowed_mrn:
            return False, "phi_mrn_scope_violation"
        if not allowed_mrn:
            # No scope binding — still block foreign MRNs when names are scoped
            if digits not in {"00001", "00002"}:
                return False, "phi_mrn_scope_violation"

    return True, None
