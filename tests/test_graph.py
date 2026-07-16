"""LangGraph / workflow smoke tests (no API key required)."""

from agent.graph import graph_available
from agent.harness_loader import load_harness
from agent.workflow import NODE_REGISTRY, build_workflow


def test_graph_deps_importable():
    assert graph_available() is True


def test_workflow_compiles():
    g = build_workflow()
    assert g is not None


def test_registry_covers_harness_steps():
    h = load_harness()
    for step in h.workflow().get("steps") or []:
        assert step["sh:stepId"] in NODE_REGISTRY
