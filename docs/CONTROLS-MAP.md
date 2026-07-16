# Controls map — alignment to common frameworks

Honest mapping of **this reference** to widely cited frameworks.  
We do **not** claim certification, audit readiness, or completeness.

| This repo control | Where | NIST AI RMF (approx.) | OWASP LLM Top 10 (approx.) |
|-------------------|-------|----------------------|----------------------------|
| Auth before retrieval | `governance/authorization.py` | GOVERN / MAP — access control | LLM06 Sensitive Information Disclosure (prevent) |
| Cross-scope isolation tests | `evaluation/phi.py`, claims regression | MEASURE — verification | LLM06 |
| Output guardrails | `governance/output_guardrails.py` | MANAGE — runtime monitoring | LLM02 / LLM06 |
| Grounding / refusal gates | `evaluation/grounding.py`, `hallucination.py` | MEASURE | LLM09 Overreliance (mitigate via refuse) |
| Tool allowlist + write tiers | harness `sh:Policy`, `tool_tiers.py` | GOVERN — least privilege | LLM08 Excessive Agency |
| Maker-checker evaluator | LangGraph evaluate node | MANAGE — human/system oversight pattern | LLM01 (prompt injection impact limit) |
| Prompt regression | `evaluation/prompt_regression.py` | MEASURE — ongoing testing | LLM04 (data/poisoning adjacent: behavior drift) |
| Audit JSONL + `request_id` | `governance/audit.py` | GOVERN — accountability | Logging for forensics |
| Evidence pack + score | `governance/evidence.py` | MEASURE — evidence of control operation | Operational transparency |
| Harness declaration | `harness/*.jsonld` | GOVERN — documentation of system | Architecture as code |

### How to use in interviews

> “We map controls to NIST AI RMF functions and OWASP LLM risks so architects see familiar vocabulary — then we show the **runnable** gate that fails CI when the control regresses.”

Do not say: “We are NIST certified” or “We solve OWASP.”

Related: Singapore Model AI Governance discussions often emphasize accountability, human oversight, and testing — our HITL path is still **deferred**; our evidence pack + CI are the current accountability story.
