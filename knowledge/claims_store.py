"""Synthetic claims store — in-memory, no real member data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DATA = Path(__file__).parent / "data" / "claims.json"


def load_members() -> list[dict[str, Any]]:
    return json.loads(_DATA.read_text(encoding="utf-8"))


def get_member(member_id: str) -> dict[str, Any] | None:
    for m in load_members():
        if m["member_id"] == member_id:
            return m
    return None


def claims_for(member_id: str, query: str = "") -> list[dict[str, Any]]:
    member = get_member(member_id)
    if not member:
        return []
    docs = []
    for c in member.get("claims", []):
        docs.append(
            {
                "doc_id": f"{member_id}:claim:{c['claim_id']}",
                "member_id": member_id,
                "kind": "claim",
                "text": (
                    f"{member['display_name']} claim {c['claim_id']} "
                    f"({c['type']}, {c['service_date']}): status={c['status']}, "
                    f"amount=${c['amount_usd']}."
                ),
                "claim": c,
            }
        )
    q = query.lower()
    if "pending" in q:
        return [d for d in docs if d["claim"]["status"] == "pending"]
    if "denied" in q or "deny" in q:
        return [d for d in docs if d["claim"]["status"] == "denied"]
    if "approved" in q:
        return [d for d in docs if d["claim"]["status"] == "approved"]
    return docs
