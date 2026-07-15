"""Authorization — identity and scope checks before retrieval."""

from __future__ import annotations

import re

# Map display names / first names to patient scopes (synthetic only)
_NAME_TO_SCOPE = {
    "alice": "patient:alice",
    "alice chen": "patient:alice",
    "john": "patient:john",
    "john smith": "patient:john",
}

_PATIENT_PATTERN = re.compile(
    r"\b(john(?:\s+smith)?|alice(?:\s+chen)?|patient:alice|patient:john)\b",
    re.I,
)


def parse_requested_patient(message: str) -> str | None:
    """Extract which patient's records the query targets, if any."""
    m = _PATIENT_PATTERN.search(message)
    if not m:
        return None
    key = m.group(1).lower().strip()
    if key.startswith("patient:"):
        return key
    return _NAME_TO_SCOPE.get(key)


def can_access(user_scope: str, requested_scope: str | None) -> bool:
    """User may only access their own scope unless no specific patient named."""
    if requested_scope is None:
        return True
    return user_scope == requested_scope


def authorize(user_scope: str, message: str) -> tuple[bool, str | None]:
    """
    Returns (allowed, denial_reason).
    Critical: run BEFORE retrieval so the model never sees unauthorized PHI.
    """
    requested = parse_requested_patient(message)
    if not can_access(user_scope, requested):
        return False, "unauthorized_patient_access"
    return True, None
