"""Structured audit events — in-memory + optional JSONL persistence."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

_events: list[dict[str, Any]] = []


def _audit_path() -> Path | None:
    raw = os.environ.get("AUDIT_LOG_PATH", "data/audit.jsonl").strip()
    if raw in {"", "off", "none", "-"}:
        return None
    return Path(raw)


def log_event(event: str, **fields: Any) -> dict[str, Any]:
    entry = {"event": event, "timestamp": time.time(), **fields}
    _events.append(entry)
    path = _audit_path()
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    return entry


def get_events() -> list[dict[str, Any]]:
    return list(_events)


def clear_events() -> None:
    _events.clear()


def export_json() -> str:
    return json.dumps(_events, indent=2)
