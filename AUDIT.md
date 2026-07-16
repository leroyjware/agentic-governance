# Agentic Governance — Repository Audit

**Audit date:** 2026-07-15  
**Remediation pass:** 2026-07-15 (Waves 1–3)  
**Living roadmap:** [PLAN.md](PLAN.md) — do not revive dead phase checklists here.

---

## Remediation status

| Finding (from original audit) | Status | How |
|-------------------------------|--------|-----|
| Star diagram / AI-SDLC overclaim | **Remediated** | README + `docs/AI-SDLC.md` match CI |
| pgvector / RAG advertised | **Remediated** | Docs say in-memory synthetic store |
| No authentication | **Partial** | `X-User-Scope` + `AUTH_STRICT` (not JWT — Planned) |
| Eval gates only rules path | **Accepted** | Documented; optional live CI job |
| Harness topology not dynamic / policy unused | **Partial** | `sh:Policy` loaded; edges still explicit (documented) |
| Policy engine / runtime.yaml stub | **Remediated** | Policy from harness; YAML points to harness |
| PHI suite size | **Remediated** | 14 scenarios in `evaluation/phi.py` |
| Stale subsystem READMEs | **Remediated** | Rewritten to match tree |
| Synthetic data docs wrong | **Remediated** | `docs/SYNTHETIC-DATA.md` |
| Harness validate not in CI | **Remediated** | `scripts/validate_harness.py` in CI |
| ADD-AN-AGENT API drift | **Remediated** | Rewritten |
| Observability incomplete | **Accepted** | Grafana Planned in PLAN.md |
| `make lint` missing | **Remediated** | Makefile + CI |
| Unused MRN pattern | **Remediated** | Guardrails enforce SYN-MRN scope |
| Version / package drift | **Remediated** | `0.3.0`, pip documented |
| Ephemeral audit | **Partial** | Optional JSONL via `AUDIT_LOG_PATH` |
| PLAN checkboxes vs Done | **Remediated** | Living PLAN.md |
| No docker-compose / Postgres | **Accepted** | Deferred in PLAN.md |

---

## Post-remediation verdict

Honest, demoable **governance reference**: dual-mode runtime, multi-agent LangGraph, harness-driven prompts/tools/policy, CI that matches the README, expanded PHI suite, light identity header, audit JSONL option.

Still **not** a full enterprise platform (no JWT, pgvector, Grafana). That is intentional — see **Next** in [PLAN.md](PLAN.md).

> Working governed agent envelope with LangGraph multi-agent demos, harness policy enforcement, and deterministic quality gates that match what CI runs.

---

## Original audit snapshot (2026-07-15)

Retained for history. Prefer remediation table + PLAN.md for current truth.

### Inventory (then)

~80 source/doc files; dual-mode agent; 2 synthetic patients; CI with 4 eval scripts; docs ahead of code in several places.

### Architecture (still accurate)

```
POST /chat → identity → authorize → rules planner | LangGraph workflow → guardrails → audit
```

### Semantic Harness (updated)

| Construct | Now |
|-----------|-----|
| Agent prompts / models / hasTool | Loaded |
| `sh:Policy` allowlist | Loaded and intersected with hasTool |
| Workflow step IDs | Tested against registry |
| Graph edges | Explicit in Python (by design) |
| Structural validate | CI |

### Showcase guidance

**Lead with:** auth-before-retrieval, dual-mode, harness policy, curl + `make demo` trace.  
**Preempt:** not JWT; not pgvector; eval gates are rules-path; live graph optional.

### Highest-impact items (done this pass)

1. Align docs/CI claims  
2. Harness validate + policy load  
3. PHI expansion + MRN guardrail + identity header + audit JSONL + hygiene scan  
4. Living PLAN.md (no dead phases)
