.PHONY: help install test eval gate run smoke demo live showcase lint validate-harness hygiene

export PYTHONPATH := .
export AGENT_MODE ?= rules
export AUDIT_LOG_PATH ?= off

help:
	@echo "  make install            pip install -r requirements.txt"
	@echo "  make test               pytest (rules mode)"
	@echo "  make eval               PHI / hallucination / grounding / latency / prompt regression"
	@echo "  make hygiene            static synthetic-PHI fixture scan"
	@echo "  make validate-harness   structural (+ sibling CLI if present)"
	@echo "  make lint               ruff if available, else compileall"
	@echo "  make gate               test + eval + hygiene + validate-harness + lint"
	@echo "  make run                API on :8080 — open /ui control plane"
	@echo "  make showcase           narrative hard-path demo (rules + optional graph)"
	@echo "  make demo|live|smoke    LangGraph scripts (needs GROQ_API_KEY)"
	@echo "  See docs/LOCAL.md and PLAN.md"

install:
	pip install -r requirements.txt

test:
	AGENT_MODE=rules AUDIT_LOG_PATH=off pytest tests/ -q

eval:
	AGENT_MODE=rules AUDIT_LOG_PATH=off python evaluation/phi.py
	AGENT_MODE=rules AUDIT_LOG_PATH=off python evaluation/hallucination.py
	AGENT_MODE=rules AUDIT_LOG_PATH=off python evaluation/grounding.py
	AGENT_MODE=rules AUDIT_LOG_PATH=off python evaluation/latency.py
	AGENT_MODE=rules AUDIT_LOG_PATH=off python evaluation/prompt_regression.py

hygiene:
	python scripts/static_phi_hygiene.py

lint:
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check agent governance api evaluation knowledge observability scripts tests; \
	else \
		python -m compileall -q agent governance api evaluation knowledge observability scripts; \
		echo "lint: compileall ok (install ruff for stricter checks)"; \
	fi

validate-harness:
	python scripts/validate_harness.py
	@if [ -f ../semantic-runtimes/cli/bin/harness.js ]; then \
		node ../semantic-runtimes/cli/bin/harness.js validate harness/harness.jsonld; \
	else \
		echo "note: sibling semantic-runtimes not found — structural validate only"; \
	fi

gate: test eval hygiene validate-harness lint

run:
	AGENT_MODE=auto uvicorn api.main:app --reload --port 8080

demo:
	python scripts/demo_workflow.py

live:
	python scripts/live_graph_cases.py

smoke:
	python scripts/smoke_langgraph.py

showcase:
	python scripts/showcase.py
