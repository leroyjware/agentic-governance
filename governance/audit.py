"""Structured audit events — in-memory + JSONL persistence.

Schema: docs/AUDIT-SCHEMA.md
Default path: data/audit.jsonl (set AUDIT_LOG_PATH=off in CI/tests).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from governance.request_context import get_request_id

_events: list[dict[str, Any]] = []


def _audit_path() -> Path | None:
    raw = os.environ.get("AUDIT_LOG_PATH", "data/audit.jsonl").strip()
    if raw in {"", "off", "none", "-"}:
        return None
    return Path(raw)


def log_event(event: str, **fields: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {"event": event, "timestamp": time.time(), **fields}
    rid = get_request_id()
    if rid and "request_id" not in entry:
        entry["request_id"] = rid
    _events.append(entry)
    path = _audit_path()
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    return entry


def _load_jsonl_tail(path: Path, limit: int) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def get_events(limit: int | None = None) -> list[dict[str, Any]]:
    """In-memory events, or JSONL tail after restart when memory is empty."""
    if _events:
        events = list(_events)
    else:
        path = _audit_path()
        events = _load_jsonl_tail(path, limit or 500) if path else []
    if limit is not None:
        return events[-limit:]
    return events


def clear_events() -> None:
    _events.clear()


def export_json() -> str:
    return json.dumps(get_events(), indent=2)
