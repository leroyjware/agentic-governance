"""Authorization for the claims vertical — before any claim retrieval."""

from __future__ import annotations

import re

_NAME_TO_SCOPE = {
    "alice": "member:alice",
    "alice chen": "member:alice",
    "john": "member:john",
    "john smith": "member:john",
}

_PATTERN = re.compile(
    r"\b(john(?:\s+smith)?|alice(?:\s+chen)?|member:alice|member:john)\b",
    re.I,
)


def parse_requested_member(message: str) -> str | None:
    m = _PATTERN.search(message)
    if not m:
        return None
    key = m.group(1).lower().strip()
    if key.startswith("member:"):
        return key
    return _NAME_TO_SCOPE.get(key)


def authorize(user_scope: str, message: str) -> tuple[bool, str | None]:
    requested = parse_requested_member(message)
    if requested is None:
        return True, None
    if user_scope != requested:
        return False, "unauthorized_member_access"
    return True, None
