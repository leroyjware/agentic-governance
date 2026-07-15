"""Structured audit events."""

from __future__ import annotations

import json
import time
from typing import Any

_events: list[dict[str, Any]] = []


def log_event(event: str, **fields: Any) -> dict[str, Any]:
    entry = {"event": event, "timestamp": time.time(), **fields}
    _events.append(entry)
    return entry


def get_events() -> list[dict[str, Any]]:
    return list(_events)


def clear_events() -> None:
    _events.clear()


def export_json() -> str:
    return json.dumps(_events, indent=2)
