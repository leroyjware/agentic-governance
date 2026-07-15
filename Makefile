.PHONY: help install test gate eval run validate-harness

export PYTHONPATH := .

help:
	@echo "  make install   pip install -r requirements.txt"
	@echo "  make test      pytest"
	@echo "  make eval      run all evaluation gates"
	@echo "  make gate      test + eval + harness validate"
	@echo "  make run       start API on :8080"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -q

eval:
	python evaluation/phi.py
	python evaluation/hallucination.py
	python evaluation/grounding.py
	python evaluation/latency.py

gate: test eval
	@$(MAKE) validate-harness

validate-harness:
	@if [ -f ../semantic-runtimes/cli/bin/harness.js ]; then \
		node ../semantic-runtimes/cli/bin/harness.js validate harness/harness.jsonld; \
	else \
		echo "skip harness validate (semantic-runtimes not sibling)"; \
	fi

run:
	uvicorn api.main:app --reload --port 8080
