# Semantic Harness Bridge

This repo **operationalizes** a Semantic Harness — it is not a parallel agent framework.

> **Semantic Harness declares what the system IS.**  
> **LangGraph executes a compatible workflow.**  
> **Governance gates prove it can be trusted.**

---

## Division of labor

| Concern | Where |
|---------|--------|
| Agents, skills, tools, workflow, policies, invariants | `harness/harness.jsonld` |
| Load / query declaration | `agent/harness_loader.py` |
| Multi-agent execution | `agent/workflow.py` |
| Auth, guardrails, audit | `governance/` |
| Prove readiness | `evaluation/` + CI |
| Spec / full CLI validate | sibling [semantic-runtimes](https://github.com/leroyjware/semantic-runtimes) |

---

## Runtime mapping

| Harness | Code |
|---------|------|
| `sh:Agent` systemRole + skills | Node system prompts |
| `sh:Agent` model / temperature | `build_chat_model(...)` |
| `sh:Agent` hasTool ∩ `sh:Policy` allowlist | Planner tool filter |
| `sh:Workflow` step IDs | Must match `NODE_REGISTRY` (tested) |
| Graph **edges** | Explicit in `build_workflow()` — not auto-compiled from JSON-LD |
| `sh:Invariant` probes | Backed by `evaluation/*.py` scripts in CI |
| Structural validate | `scripts/validate_harness.py` (always in CI) |

Honesty matters: topology is **harness-aligned**, not harness-compiled. That keeps the graph reviewable in Python while prompts/tools/policy stay declarative.

---

## Validate

```bash
make validate-harness
# structural always; full CLI if ../semantic-runtimes exists
```

---

## Related

- [LOCAL.md](./LOCAL.md) — Groq multi-agent local run  
- [ADD-AN-AGENT.md](./ADD-AN-AGENT.md) — extend the mesh  
- [PLAN.md](../PLAN.md) — living roadmap  
