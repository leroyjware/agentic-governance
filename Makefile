.PHONY: help install test eval gate run smoke demo live showcase lint validate-harness hygiene obs-up obs-down

export PYTHONPATH := .
export AGENT_MODE ?= rules
export AUDIT_LOG_PATH ?= off

help:
	@echo "  make install            pip install -r requirements.txt"
	@echo "  make test               pytest (rules mode)"
	@echo "  make eval               PHI / hall / ground / latency / prompt / claims"
	@echo "  make hygiene            static synthetic-PHI fixture scan"
	@echo "  make validate-harness   structural (+ sibling CLI if present)"
	@echo "  make lint               ruff if available, else compileall"
	@echo "  make gate               test + eval + hygiene + validate-harness + lint"
	@echo "  make run                API on :8080 — open /ui control plane"
	@echo "  make obs-up             Prometheus + Grafana (docker-compose.obs.yml)"
	@echo "  make obs-down           stop obs stack"
	@echo "  make showcase           narrative hard-path demo"
	@echo "  See docs/LOCAL.md docs/ADOPTERS.md PLAN.md"

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
	AGENT_MODE=rules AUDIT_LOG_PATH=off python evaluation/claims_regression.py

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
		node ../semantic-runtimes/cli/bin/harness.js validate harness/examples/claims-assistant.jsonld; \
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

obs-up:
	docker compose -f docker-compose.obs.yml up -d prometheus grafana
	@echo "Prometheus http://localhost:9090  Grafana http://localhost:3000"
	@echo "Scrape target: compose api service OR host.docker.internal:8080 (make run)"

obs-down:
	docker compose -f docker-compose.obs.yml down
