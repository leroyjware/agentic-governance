# Agentic Governance

**An Enterprise Agentic AI SDLC Reference Architecture**

**Leroy Ware**  
**July 2026**

---

## Executive Summary

Enterprises are racing to deploy agentic AI. Most teams can stand up a LangGraph or LangChain agent in a weekend. Very few can answer the question that actually matters in healthcare, insurance, and other regulated industries:

> *How do we prove this agent is safe enough to ship — and keep it that way after every prompt change?*

**Agentic Governance** is an open-source reference architecture that puts that question at the center. It is not a chatbot demo. It is a working skeleton of the discipline mature AI platforms require: quality gates in CI/CD, authorization before retrieval, runtime guardrails, audit logging, and portable architecture declarations.

The reference implementation uses a deliberately simple **Healthcare Appointment Assistant** on **100% synthetic data**. The agent is intentionally modest. The governance around it is the product.

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

At design time, the system declares what it is allowed to do.  
During development, CI/CD gates fail the pipeline when thresholds are violated.  
At runtime, middleware enforces authorization, tool policy, and output validation.  
In production, metrics and audit logs prove the controls are working.

That is the same mental model as DevSecOps — applied to agentic systems.

---

## Architecture Overview

### What the repository contains

```
agentic-governance/
├── harness/           Semantic Harness declaration (architecture as data)
├── governance/        Authorization, guardrails, audit
├── agent/             Planner (orchestrator — swappable)
├── knowledge/         Synthetic patient records (no real PHI)
├── evaluation/        PHI, hallucination, grounding, latency gates
├── api/               FastAPI entrypoint with governance chain
├── observability/     Prometheus metrics
├── .github/workflows/ AI SDLC CI pipeline
└── docs/              Architecture, SDLC, interview framing
```

### Runtime request path

Every request passes through governance — not around it:

```
User Request
    ↓
Authentication / Identity Scope
    ↓
Authorization                    ← block cross-patient access HERE
    ↓
Scoped Retrieval                 ← LLM never receives unauthorized records
    ↓
Planner / Answer Generation
    ↓
Output Guardrails
    ↓
Audit Logger
    ↓
Response (+ Prometheus metrics)
```

**Critical design choice:** authorization happens *before* retrieval.  
The model cannot leak what it never received. That is a stronger architectural answer than “we told the prompt not to reveal PHI.”

---

## The Sample Agent (Intentionally Simple)

**Healthcare Appointment Assistant** (synthetic only):

- Answer appointment questions  
- Retrieve fake patient records  
- Summarize visit notes  
- Refuse when context is insufficient  

Capabilities are simple so reviewers can focus on controls:

| Behavior | Governance control |
|----------|-------------------|
| “What are my appointments?” | Grounded answer with document citations |
| “Show me John Smith’s MRI” (as Alice) | Access denied + audit event |
| “When is my surgery?” (no matching data) | Refusal — no hallucinated clinical fact |

**Disclaimer:** This is a demonstration architecture. It is not a HIPAA-covered production system. The *controls* transfer; the data does not.

---

## AI SDLC: Quality Gates as the Star

The CI/CD pipeline is the centerpiece of the reference architecture:

```
Developer → Commit → Build → Unit Tests
    → PHI Leakage Tests
    → Hallucination / Refusal Tests
    → Grounding / Citation Tests
    → Latency Budget
    → Architecture Validation (harness)
    → Deploy
    → Runtime Monitoring
    → Feedback into evaluation datasets
```

**If any gate fails, the pipeline stops.**

That is the operational definition of “production-ready” this project defends: not a self-assessment by the agent, but machine-checkable thresholds.

### Gate examples (implemented today)

| Gate | Pass criterion |
|------|----------------|
| PHI leakage | Unauthorized cross-patient access blocked (100% on suite) |
| Hallucination / refusal | No-context clinical questions produce refusal |
| Grounding | Factual answers include retrieval citations |
| Latency | p95 under budget (local planner) |
| Harness validation | Architecture graph remains coherent |

---

## Semantic Harness: Architecture as Declarative Data

Alongside the Python runtime, the repository includes a **Semantic Harness** — a JSON-LD graph declaring agents, tools, policies, goals, metrics, and invariants.

This is not configuration theater. It is a portable contract that:

1. Documents what the system claims to be  
2. Links invariants to evaluation probes  
3. Aligns design-time intent with CI and runtime enforcement  

```
harness.jsonld  →  CI probes (evaluation/)  →  Runtime middleware  →  Metrics
```

**Semantic Harness declares the agent. Agentic Governance operationalizes the declaration.**

That bridge — from declarative architecture to executable gates — is a durable platform pattern, independent of which LLM or graph framework is fashionable next year.

---

## Observability and Audit

The reference exposes Prometheus metrics such as:

- Request counts by status  
- PHI violation / block counters  
- Refusal counters  
- Request latency histograms  

Audit events record who asked what, whether access was denied, and why. In regulated environments, that auditability is not optional — it is the difference between an experiment and a system of record for AI behavior.

---

## What This Is — and Is Not

| This project **is** | This project **is not** |
|---------------------|-------------------------|
| An enterprise AI SDLC reference | A production EHR integration |
| A working governance + evaluation skeleton | A claim of HIPAA certification |
| A pattern for auth-before-retrieval | A novel LLM training method |
| Compatible with LangGraph as a swap-in | Locked to a single agent framework |
| Thought leadership you can run locally | Slideware without code |

Honesty about scope is part of the architecture. Overclaiming is itself a governance failure.

---

## Why This Matters for Enterprise Hiring

Principal and staff AI platform roles increasingly ask:

- Where does governance live?  
- How do you prevent PHI leakage without trusting the model?  
- What fails the deployment pipeline?  
- How do you know a prompt change didn’t regress safety?  
- How do you monitor agentic systems in production?

This repository is a concrete answer to those questions — runnable, reviewable, and extensible.

Most candidates can build an agent.  
Fewer can show **how to industrialize one**.

---

## Getting Started (for Reviewers)

```bash
git clone https://github.com/leroyjware/agentic-governance
cd agentic-governance
pip install -r requirements.txt

# Quality gates (no API keys required)
make eval

# Unit + API tests
make test

# Local API
make run
# → http://localhost:8080/docs
```

Try the three canonical scenarios:

1. Authorized appointment query → grounded answer with citations  
2. Cross-patient MRI request → access denied  
3. Surgery date with no context → refusal  

---

## Roadmap

| Phase | Focus |
|-------|--------|
| **Shipped** | Governance chain, eval gates, FastAPI, Prometheus, harness, CI |
| **Next** | LangGraph + live LLM behind the same middleware |
| **Next** | Grafana dashboards, richer eval corpora |
| **Later** | Human-in-the-loop approval for high-risk tools |

The orchestrator can evolve. The governance envelope should not have to be reinvented.

---

## Closing

The industry does not need another demo that answers a patient’s question.  
It needs platforms that can **refuse**, **block**, **cite**, **audit**, and **fail the build** when trust is broken.

Agentic Governance is a reference for that discipline: an Enterprise Agentic AI SDLC you can clone, run, and extend.

**You stop being the pipeline. You become the architect of the gates.**

---

**Author:** Leroy Ware  
**Repository:** https://github.com/leroyjware/agentic-governance *(private during review)*  
**Related work:** [Semantic Harness](https://semantic-harness.org) — open standard for declaring intelligent systems as portable graphs  
**License:** Apache 2.0  

*For recruiting and technical review. Synthetic healthcare data only — demonstration architecture, not a clinical system.*
