.PHONY: help install test eval gate run smoke validate-harness

export PYTHONPATH := .
export AGENT_MODE ?= rules

help:
	@echo "  make install   pip install -r requirements.txt"
	@echo "  make test      pytest (rules mode)"
	@echo "  make eval      PHI / hallucination / grounding / latency gates"
	@echo "  make gate      test + eval"
	@echo "  make run       API on :8080 (auto → LangGraph if key set)"
	@echo "  make smoke     live LangGraph smoke (requires API key)"

install:
	pip install -r requirements.txt

test:
	AGENT_MODE=rules pytest tests/ -q

eval:
	AGENT_MODE=rules python evaluation/phi.py
	AGENT_MODE=rules python evaluation/hallucination.py
	AGENT_MODE=rules python evaluation/grounding.py
	AGENT_MODE=rules python evaluation/latency.py

gate: test eval
	@$(MAKE) validate-harness

validate-harness:
	@if [ -f ../semantic-runtimes/cli/bin/harness.js ]; then \
		node ../semantic-runtimes/cli/bin/harness.js validate harness/harness.jsonld; \
	else \
		echo "skip harness validate (semantic-runtimes not sibling)"; \
	fi

run:
	AGENT_MODE=auto uvicorn api.main:app --reload --port 8080

smoke:
	python scripts/smoke_langgraph.py
