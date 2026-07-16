"""Intent-scoped tool tiers — write tools only when policy allows."""

from __future__ import annotations

# Tools that mutate state (synthetic schedule). Require intent == schedule.
WRITE_TOOLS = frozenset({"schedule_appointment"})

READ_TOOLS = frozenset({"retrieve_records", "summarize_visit"})


def filter_tools_for_intent(tool_names: set[str], intent: str | None) -> set[str]:
    """Drop write tools unless routed intent is schedule."""
    intent = (intent or "unknown").lower().strip()
    if intent == "schedule":
        return set(tool_names)
    return {n for n in tool_names if n not in WRITE_TOOLS}
