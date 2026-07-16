# Agentic Governance

**An Enterprise Agentic AI SDLC Reference Architecture**

**Leroy Ware**  
**July 2026 · v0.7**

---

## Executive Summary

Enterprises are racing to deploy agentic AI. Most teams can stand up a LangGraph or LangChain agent in a weekend. Very few can answer the question that actually matters in healthcare, insurance, and other regulated industries:

> *How do we prove this agent is safe enough to ship — and keep it that way after every prompt change?*

**Agentic Governance** is an open-source reference architecture that puts that question at the center. It is not a chatbot demo. It is a working skeleton of the discipline mature AI platforms require: quality gates in CI/CD, authorization before retrieval, runtime guardrails, audit logging, per-request evidence, and portable architecture declarations.

The reference uses two deliberately simple assistants on **100% synthetic data**: a **Healthcare Appointment Assistant** (LangGraph flagship) and a **Claims Status Assistant** (second vertical). The agents are modest on purpose. The governance around them is the product.

LangGraph (or any orchestrator) is an implementation detail. **Governance is the product.**

---

## The Problem

### The gap between “we built an agent” and “we can operate one”

Typical agent projects deliver:

- A planner and a handful of tools  
- A RAG pipeline  
- A demo that looks impressive in a slide deck  

What they usually lack:

| Gap | Consequence |
|-----|-------------|
| No CI quality gates for AI behavior | Prompt changes ship without regression proof |
| Security left to the model prompt | PHI leakage is a hope, not a control |
| No authorization at retrieval | The LLM sees records it should never see |
| No machine-checkable “done” | Teams argue about readiness in meetings |
| No architecture metadata | Capabilities live in code and Slack threads |
| No per-request proof | Auditors get traces, not claims tied to policy |

Enterprise reviewers — especially in healthcare — are not hiring for another RAG notebook. They are hiring for people who know how to **industrialize** AI: evaluate, gate, authorize, audit, and monitor.

### Three meanings of “governance” that get conflated

| Term | Focus |
|------|--------|
| **AI Governance** | Policy, compliance, risk, auditability |
| **Agentic Governance** | Runtime control of tools, autonomy, and agent behavior |
| **AI SDLC Governance** | Build → evaluate → approve → deploy → monitor |

This repository implements all three as one coherent system — not as a compliance checklist bolted on after the demo.

---

## The Thesis

**Governance is not a component. It is a set of controls woven through the AI lifecycle.**

```
Design → Development → Evaluation → Deployment → Production
   │          │             │            │            │
   └──────────┴─────────────┴────────────┴────────────┘
                    Governance at every stage
```

At design time, the system declares what it is allowed to do (Semantic Harness).  
During development, CI/CD gates fail the pipeline when thresholds are violated.  
At runtime, the envelope enforces authorization, tool policy, evaluator checks, and output validation.  
Each response carries an **evidence pack** and a lightweight **governance score**.  
In production, metrics and audit logs show the controls are still firing.

That is the same mental model as DevSecOps — applied to agentic systems.

---

## Architecture Overview

### What the repository contains

```
agentic-governance/
├── harness/           Semantic Harness declarations (healthcare + claims)
├── governance/        Authorization, guardrails, audit, evidence, score
├── agent/             LangGraph workflow + rules planners (swappable)
├── knowledge/         Synthetic patient / member records (no real PHI)
├── evaluation/        PHI, hallucination, grounding, latency, prompt, claims
├── api/               FastAPI + control plane UI at /ui
├── observability/     Prometheus metrics + optional Grafana
├── .github/workflows/ AI SDLC CI pipeline
└── docs/              Architecture, SDLC, evidence, interview framing
```

### Runtime request path

Every request passes through governance — not around it:

```
User Request (+ X-User-Scope, request_id)
    ↓
Authorization                    ← block cross-scope access HERE
    ↓
Scoped Retrieval / Tools         ← LLM never receives unauthorized records
    ↓
Plan → Evaluate (graph) or rules planner
    ↓
Output Guardrails
    ↓
Audit Logger
    ↓
Response (+ evidence pack, governance score, Prometheus metrics)
```

**Critical design choice:** authorization happens *before* retrieval.  
The model cannot leak what it never received. That is a stronger architectural answer than “we told the prompt not to reveal PHI.”

---

## The Sample Assistants (Intentionally Simple)

### Healthcare Appointment Assistant

- Answer appointment questions  
- Retrieve fake patient records  
- Summarize visit notes  
- Refuse when context is insufficient  
- Schedule path uses write-tier tools only when intent warrants it  

| Behavior | Governance control |
|----------|-------------------|
| “What are my appointments?” | Grounded answer with citations + evidence claims |
| “Show me John Smith’s MRI” (as Alice) | Access denied + audit + high score (controls worked) |
| “When is my surgery?” (no matching data) | Refusal — no hallucinated clinical fact |

### Claims Status Assistant (second vertical)

Same envelope, different harness and domain vocabulary (`member:*`). Proves the pattern is reusable — not a one-off healthcare demo. See [SECOND-VERTICAL.md](./SECOND-VERTICAL.md).

**Disclaimer:** This is a demonstration architecture. It is not a HIPAA-covered production system. The *controls* transfer; the data does not.

---

## AI SDLC: Quality Gates as the Star

```
Developer → Commit → Build → Unit Tests
    → Prompt regression (golden.jsonl)
    → PHI Leakage Tests
    → Hallucination / Refusal Tests
    → Grounding / Citation Tests
    → Latency Budget
    → Claims vertical regression
    → Architecture Validation (harness)
    → (optional) Live LangGraph if API key present
    → Deploy
    → Runtime Monitoring
```

**If any required gate fails, the pipeline stops.** Run locally with `make gate`.

That is the operational definition of “production-ready” this project defends: not a self-assessment by the agent, but machine-checkable thresholds. Details: [AI-SDLC.md](./AI-SDLC.md).

| Gate | Pass criterion |
|------|----------------|
| Prompt regression | Golden prompts keep status / block / citations |
| PHI leakage | Unauthorized cross-patient access blocked |
| Hallucination / refusal | No-context clinical questions produce refusal |
| Grounding | Factual answers include retrieval citations |
| Latency | Rules-path p95 under budget |
| Claims vertical | Cross-member isolation + envelope reuse |
| Harness validation | Architecture graph remains coherent |

---

## Semantic Harness: Architecture as Declarative Data

Alongside the Python runtime, the repository includes **Semantic Harness** JSON-LD graphs declaring agents, tools, policies, goals, metrics, and invariants.

This is not configuration theater. It is a portable contract that:

1. Documents what the system claims to be  
2. Links invariants to evaluation probes  
3. Aligns design-time intent with CI and runtime enforcement  

```
harness.jsonld  →  CI probes (evaluation/)  →  Runtime envelope  →  Evidence + metrics
```

**Semantic Harness declares the agent. Agentic Governance operationalizes the declaration.**

That bridge — from declarative architecture to executable gates — is a durable platform pattern, independent of which LLM or graph framework is fashionable next year. See [SEMANTIC-HARNESS-BRIDGE.md](./SEMANTIC-HARNESS-BRIDGE.md).

---

## Evidence, Score, Observability, and Audit

### Per-request evidence (v0.7)

Every `/chat` response includes an **evidence pack**: harness identity, outcomes, and machine-checkable claims (authz-before-retrieval, cross-scope isolation, grounding-or-refusal, maker-checker, correlation). A lightweight **governance score** (0–100) and residual-risk band make the result demoable in the control plane.

This is a **receipt**, not a legal attestation. See [EVIDENCE.md](./EVIDENCE.md).

### Prometheus / Grafana

Runtime counters: requests by status, PHI blocks, refusals, latency. Optional stack: `make obs-up`. See [KPI.md](./KPI.md).

### Audit

Events record who asked what, whether access was denied, and why — correlated by `request_id`. See [AUDIT-SCHEMA.md](./AUDIT-SCHEMA.md).

Framework vocabulary (NIST AI RMF / OWASP LLM — alignment, not certification): [CONTROLS-MAP.md](./CONTROLS-MAP.md).

---

## What This Is — and Is Not

| This project **is** | This project **is not** |
|---------------------|-------------------------|
| An enterprise AI SDLC reference | A production EHR / claims integration |
| A working governance + evaluation skeleton | A claim of HIPAA / NIST certification |
| A pattern for auth-before-retrieval | A novel LLM training method |
| LangGraph multi-agent *inside* the governance envelope | Locked to a single cloud vendor |
| Thought leadership you can run locally | Slideware without code |
| Evidence + score per request | A full HITL approval product |

Honesty about scope is part of the architecture. Overclaiming is itself a governance failure.

---

## Why This Matters for Enterprise Hiring

Principal and staff AI platform roles increasingly ask:

- Where does governance live?  
- How do you prevent PHI leakage without trusting the model?  
- What fails the deployment pipeline?  
- How do you know a prompt change didn’t regress safety?  
- How do you prove a *single* production request followed policy?  
- How do you monitor agentic systems in production?

This repository is a concrete answer — runnable, reviewable, and extensible. Demo path: [INTERVIEW-GUIDE.md](./INTERVIEW-GUIDE.md).

Most candidates can build an agent.  
Fewer can show **how to industrialize one**.

---

## Getting Started (for Reviewers)

```bash
git clone https://github.com/leroyjware/agentic-governance
cd agentic-governance
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

make gate          # full deterministic suite (no API keys)
make showcase      # narrative hard-path demo
make run           # http://localhost:8080/ui
make obs-up        # optional Prometheus :9090 + Grafana :3000
```

Canonical scenarios:

1. Authorized appointment query → grounded answer + citations + evidence  
2. Cross-patient MRI request → access denied + strong governance score  
3. Surgery date with no context → refusal  
4. Claims vertical — cross-member access denied (same envelope)

---

## Dual execution mode

| Mode | Engine | Purpose |
|------|--------|---------|
| `graph` / `auto` + API key | **LangGraph** multi-agent (healthcare) | Realistic inference demos |
| `rules` / CI | Deterministic planner | Quality gates without LLM spend |
| `assistant=claims` | Claims rules planner | Second vertical — envelope reuse |

Unauthorized requests are denied **before** either engine runs. See [LOCAL.md](./LOCAL.md), [SECOND-VERTICAL.md](./SECOND-VERTICAL.md).

---

## Status and roadmap

**Reference is complete through v0.7** (evidence pack, governance score, controls map, interview guide). Living tracker: **[PLAN.md](../PLAN.md)**.

Deferred on purpose (not missing by accident): human-in-the-loop approval UI, JWT/OIDC, pgvector, LangSmith/ELK as required dependencies. Adopters swap those in — see [ADOPTERS.md](./ADOPTERS.md).

The orchestrator can evolve. The governance envelope should not have to be reinvented.

---

## Closing

The industry does not need another demo that answers a patient’s question.  
It needs platforms that can **refuse**, **block**, **cite**, **audit**, **prove a single run**, and **fail the build** when trust is broken.

Agentic Governance is a reference for that discipline: an Enterprise Agentic AI SDLC you can clone, run, and extend.

**You stop being the pipeline. You become the architect of the gates.**

---

**Author:** Leroy Ware  
**Repository:** https://github.com/leroyjware/agentic-governance  
**Related work:** [Semantic Harness](https://semantic-harness.org) — open standard for declaring intelligent systems as portable graphs  
**License:** Apache 2.0  

*For recruiting and technical review. Synthetic healthcare data only — demonstration architecture, not a clinical system.*
