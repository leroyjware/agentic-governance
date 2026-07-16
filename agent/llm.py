"""OpenAI-compatible LLM factory (Groq preferred, then OpenAI)."""

from __future__ import annotations

import os

from langchain_openai import ChatOpenAI


def llm_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY"))


def build_chat_model(model: str | None = None, temperature: float | None = None) -> ChatOpenAI:
    """Build chat model. Prefer Groq when GROQ_API_KEY is set."""
    temp = 0.2 if temperature is None else temperature
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        return ChatOpenAI(
            model=model
            or os.getenv("GROQ_MODEL", os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")),
            api_key=groq_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1"),
            temperature=temp,
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No LLM API key. Set GROQ_API_KEY (preferred) or OPENAI_API_KEY "
            "(or use AGENT_MODE=rules)."
        )

    kwargs: dict = {
        "model": model or os.getenv("MODEL_NAME", "gpt-4o-mini"),
        "api_key": api_key,
        "temperature": temp,
    }
    base = os.getenv("OPENAI_BASE_URL")
    if base:
        kwargs["base_url"] = base
    return ChatOpenAI(**kwargs)
