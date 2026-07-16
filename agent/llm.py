"""OpenAI-compatible LLM factory (OpenAI, Groq, Azure, local)."""

from __future__ import annotations

import os

from langchain_openai import ChatOpenAI


def llm_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY"))


def build_chat_model() -> ChatOpenAI:
    """Prefer Groq if GROQ_API_KEY is set; otherwise OpenAI-compatible OPENAI_*."""
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        return ChatOpenAI(
            model=os.getenv("GROQ_MODEL", os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")),
            api_key=groq_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1"),
            temperature=0.2,
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No LLM API key. Set OPENAI_API_KEY or GROQ_API_KEY "
            "(or use AGENT_MODE=rules for the rule-based planner)."
        )

    kwargs: dict = {
        "model": os.getenv("MODEL_NAME", "gpt-4o-mini"),
        "api_key": api_key,
        "temperature": 0.2,
    }
    base = os.getenv("OPENAI_BASE_URL")
    if base:
        kwargs["base_url"] = base
    return ChatOpenAI(**kwargs)
