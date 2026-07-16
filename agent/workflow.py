"""Multi-agent LangGraph workflow driven by Semantic Harness.

Flow (harness-aligned):

  authorize → route → plan → evaluate ─┬→ finalize
                         ↑             │
                         └─ replan (1)×┘

Write tools only when intent == schedule (tool tiers).
Evaluator reject triggers one replan with feedback, then hard deny.

Adding an agent:
  1. Add sh:Agent (+ skill) to harness/harness.jsonld
  2. Register a node in NODE_REGISTRY below
  3. Wire an edge in build_workflow()
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from agent.harness_loader import load_harness
from agent.llm import build_chat_model
from agent.tools import get_citations, set_request_scope, tools_by_names
from governance import audit, authorization, output_guardrails
from governance.tool_tiers import filter_tools_for_intent

NodeFn = Callable[["WorkflowState"], dict[str, Any]]


class WorkflowState(TypedDict, total=False):
    user_scope: str
    message: str
    authorized: bool
    deny_reason: str | None
    intent: str
    draft: str
    citations: list[str]
    evaluator_approved: bool
    evaluator_feedback: str
    evaluator_score: float
    retry_count: int
    answer: str
    status: str
    blocked: bool
    reason: str | None
    engine: str
    trace: list[dict[str, Any]]


_SCOPE_NAMES = {
    "patient:alice": {"alice", "alice chen"},
    "patient:john": {"john", "john smith"},
}


def _trace(state: WorkflowState, step: str, **extra: Any) -> list[dict[str, Any]]:
    entry = {"step": step, **extra}
    return list(state.get("trace") or []) + [entry]


def _parse_json_blob(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    return {}


# --- Nodes -----------------------------------------------------------------


def node_authorize(state: WorkflowState) -> dict[str, Any]:
    scope = state["user_scope"]
    message = state["message"]
    allowed, reason = authorization.authorize(scope, message)
    if not allowed:
        audit.log_event(
            "governance.block",
            user_scope=scope,
            reason=reason,
            message=message,
            step="authorize",
        )
        return {
            "authorized": False,
            "deny_reason": reason,
            "blocked": True,
            "status": "denied",
            "answer": "Access denied. You are not authorized to view those records.",
            "citations": [],
            "engine": "langgraph-workflow",
            "trace": _trace(state, "authorize", allowed=False, reason=reason),
        }
    return {
        "authorized": True,
        "deny_reason": None,
        "blocked": False,
        "trace": _trace(state, "authorize", allowed=True),
    }


def node_route(state: WorkflowState) -> dict[str, Any]:
    h = load_harness()
    prompt = h.system_prompt("Router")
    model_name = h.model_for("Router")
    agent = h.agent_by_name("Router")
    temp = float(agent.get("temperature") or 0.0) if agent else 0.0
    llm = build_chat_model(model=model_name, temperature=temp)

    resp = llm.invoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(content=state["message"]),
        ]
    )
    raw = getattr(resp, "content", "") or ""
    data = _parse_json_blob(raw if isinstance(raw, str) else str(raw))
    intent = str(data.get("intent") or "unknown").lower()
    if intent not in ("appointments", "imaging", "summary", "schedule", "unknown"):
        intent = "unknown"
    return {
        "intent": intent,
        "trace": _trace(state, "route", intent=intent, rationale=data.get("rationale")),
    }


def node_plan(state: WorkflowState) -> dict[str, Any]:
    h = load_harness()
    prompt = h.system_prompt("Healthcare Planner")
    intent = state.get("intent") or "unknown"
    prompt = (
        f"{prompt}\n\n## Routed intent\n{intent}\n"
        "Use only the tools provided. Write/schedule tools appear only for schedule intent."
    )

    retry_count = int(state.get("retry_count") or 0)
    # Replan after evaluator rejection: incorporate feedback and bump retry
    if state.get("evaluator_approved") is False and state.get("evaluator_feedback"):
        retry_count = retry_count + 1
        prompt += (
            f"\n\n## Evaluator feedback (revise draft — attempt {retry_count})\n"
            f"{state.get('evaluator_feedback')}\n"
            "Fix citations and grounding. Do not invent clinical facts."
        )

    model_name = h.model_for("Healthcare Planner")
    agent = h.agent_by_name("Healthcare Planner")
    temp = float(agent.get("temperature") or 0.2) if agent else 0.2

    # hasTool ∩ sh:Policy ∩ intent tier (write tools only for schedule)
    allowed_tool_names = filter_tools_for_intent(
        h.allowed_tools_for_agent("Healthcare Planner"),
        intent,
    )
    tools = tools_by_names(allowed_tool_names)

    set_request_scope(state["user_scope"])
    llm = build_chat_model(model=model_name, temperature=temp)
    react = create_react_agent(llm, tools, prompt=prompt)

    result = react.invoke({"messages": [("user", state["message"])]})
    messages = result.get("messages") or []
    draft = ""
    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if content and getattr(msg, "type", None) == "ai":
            if isinstance(content, str) and content.strip():
                draft = content.strip()
                break

    if not draft:
        draft = "I don't have enough information to answer that."

    citations = get_citations()
    if citations and "sources:" not in draft.lower():
        draft = f"{draft} [sources: {', '.join(citations)}]"

    return {
        "draft": draft,
        "citations": citations,
        "retry_count": retry_count,
        "evaluator_approved": None,  # clear before next evaluate
        "trace": _trace(
            state,
            "plan",
            draft_preview=draft[:200],
            citations=citations,
            tools=sorted(allowed_tool_names),
            retry_count=retry_count,
            write_tools=("schedule_appointment" in allowed_tool_names),
        ),
    }


def node_evaluate(state: WorkflowState) -> dict[str, Any]:
    h = load_harness()
    prompt = h.system_prompt("Grounding Evaluator")
    model_name = h.model_for("Grounding Evaluator")
    agent = h.agent_by_name("Grounding Evaluator")
    temp = float(agent.get("temperature") or 0.0) if agent else 0.0
    llm = build_chat_model(model=model_name, temperature=temp)

    payload = {
        "user_scope": state["user_scope"],
        "message": state["message"],
        "intent": state.get("intent"),
        "citations": state.get("citations") or [],
        "draft": state.get("draft") or "",
    }
    resp = llm.invoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(content=json.dumps(payload, indent=2)),
        ]
    )
    raw = getattr(resp, "content", "") or ""
    data = _parse_json_blob(raw if isinstance(raw, str) else str(raw))

    # Deterministic safety net if LLM JSON is weak
    draft = state.get("draft") or ""
    citations = state.get("citations") or []
    is_refusal = "don't have enough information" in draft.lower()
    requires_citation = not is_refusal and any(
        k in (state.get("message") or "").lower()
        for k in ("appointment", "mri", "imaging", "schedule", "summary", "visit")
    )
    approved = bool(data.get("approved", False))
    if is_refusal:
        approved = True
    elif requires_citation and not citations:
        approved = False
        data["feedback"] = data.get("feedback") or "Rejected: factual answer missing citations."

    score = float(data.get("score") or (1.0 if approved else 0.0))
    feedback = str(data.get("feedback") or ("approved" if approved else "rejected"))

    return {
        "evaluator_approved": approved,
        "evaluator_feedback": feedback,
        "evaluator_score": score,
        "trace": _trace(
            state,
            "evaluate",
            approved=approved,
            score=score,
            feedback=feedback[:300],
        ),
    }


def node_finalize(state: WorkflowState) -> dict[str, Any]:
    if state.get("blocked"):
        return {
            "engine": "langgraph-workflow",
            "trace": _trace(state, "finalize", skipped=True),
        }

    draft = state.get("draft") or ""
    citations = list(state.get("citations") or [])
    approved = state.get("evaluator_approved", False)

    if not approved:
        audit.log_event(
            "governance.block",
            user_scope=state["user_scope"],
            reason="evaluator_rejected",
            feedback=state.get("evaluator_feedback"),
            step="evaluate",
        )
        return {
            "blocked": True,
            "status": "denied",
            "reason": "evaluator_rejected",
            "answer": (
                "Response held by grounding evaluator. "
                f"{state.get('evaluator_feedback') or 'Draft failed policy checks.'}"
            ),
            "citations": [],
            "engine": "langgraph-workflow",
            "trace": _trace(state, "finalize", approved=False),
        }

    names = _SCOPE_NAMES.get(state["user_scope"], set())
    safe, guard_reason = output_guardrails.scan_response(
        draft, names, user_scope=state["user_scope"]
    )
    if not safe:
        audit.log_event(
            "governance.block",
            user_scope=state["user_scope"],
            reason=guard_reason,
            step="output_guardrails",
        )
        return {
            "blocked": True,
            "status": "denied",
            "reason": guard_reason,
            "answer": "Response blocked by output guardrails.",
            "citations": [],
            "engine": "langgraph-workflow",
            "trace": _trace(state, "finalize", guardrails=False),
        }

    is_refusal = "don't have enough information" in draft.lower()
    if is_refusal:
        audit.log_event(
            "agent.refuse",
            user_scope=state["user_scope"],
            engine="langgraph-workflow",
            intent=state.get("intent"),
        )
        return {
            "answer": "I don't have enough information to answer that.",
            "citations": [],
            "blocked": False,
            "status": "refused",
            "engine": "langgraph-workflow",
            "trace": _trace(state, "finalize", approved=True, status="refused"),
        }

    audit.log_event(
        "agent.response",
        user_scope=state["user_scope"],
        citations=citations,
        engine="langgraph-workflow",
        intent=state.get("intent"),
    )
    return {
        "answer": draft,
        "citations": citations,
        "blocked": False,
        "status": "ok",
        "engine": "langgraph-workflow",
        "trace": _trace(state, "finalize", approved=True, status="ok"),
    }


# Registry — add agents here when you extend the harness
NODE_REGISTRY: dict[str, NodeFn] = {
    "authorize": node_authorize,
    "route": node_route,
    "plan": node_plan,
    "evaluate": node_evaluate,
    "finalize": node_finalize,
}


def _after_authorize(state: WorkflowState) -> Literal["route", "finalize"]:
    return "finalize" if state.get("blocked") else "route"


def _after_evaluate(state: WorkflowState) -> Literal["plan", "finalize"]:
    """One replan after reject; then finalize (deny path inside finalize)."""
    if state.get("evaluator_approved"):
        return "finalize"
    if int(state.get("retry_count") or 0) < 1:
        return "plan"
    return "finalize"


def build_workflow():
    """Compile the multi-agent StateGraph."""
    g: StateGraph = StateGraph(WorkflowState)
    for name, fn in NODE_REGISTRY.items():
        g.add_node(name, fn)

    g.add_edge(START, "authorize")
    g.add_conditional_edges("authorize", _after_authorize, {"route": "route", "finalize": "finalize"})
    g.add_edge("route", "plan")
    g.add_edge("plan", "evaluate")
    g.add_conditional_edges(
        "evaluate",
        _after_evaluate,
        {"plan": "plan", "finalize": "finalize"},
    )
    g.add_edge("finalize", END)
    return g.compile()


_compiled = None


def reset_workflow_cache() -> None:
    global _compiled
    _compiled = None


def get_workflow():
    global _compiled
    if _compiled is None:
        _compiled = build_workflow()
    return _compiled


def run_workflow(user_scope: str, message: str) -> dict[str, Any]:
    """Execute the harness-aligned multi-agent workflow."""
    graph = get_workflow()
    final: WorkflowState = graph.invoke(
        {
            "user_scope": user_scope,
            "message": message,
            "trace": [],
            "citations": [],
            "retry_count": 0,
            "engine": "langgraph-workflow",
        }
    )
    return {
        "blocked": bool(final.get("blocked")),
        "status": final.get("status") or ("denied" if final.get("blocked") else "ok"),
        "answer": final.get("answer") or "",
        "citations": final.get("citations") or [],
        "reason": final.get("reason") or final.get("deny_reason"),
        "engine": final.get("engine") or "langgraph-workflow",
        "intent": final.get("intent"),
        "evaluator_approved": final.get("evaluator_approved"),
        "evaluator_score": final.get("evaluator_score"),
        "evaluator_feedback": final.get("evaluator_feedback"),
        "retry_count": final.get("retry_count") or 0,
        "trace": final.get("trace") or [],
    }
