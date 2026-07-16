# Synthetic Data Policy

This repository uses **100% synthetic healthcare data**. No real PHI. Ever.

---

## Rules

1. Patient names, MRNs, and clinical notes are hand-crafted fixtures (or clearly fake).
2. MRNs use the `SYN-MRN-*` prefix only.
3. CI runs `scripts/static_phi_hygiene.py` to reject SSN-like patterns and non-synthetic MRNs in fixtures.
4. Docs state: demonstration only — **not** HIPAA compliant.
5. No connectors to real EHR systems.

---

## Current corpus

**Path:** `knowledge/data/patients.json`  
**Count:** 2 patients (`patient:alice`, `patient:john`)

```json
{
  "patient_id": "patient:alice",
  "display_name": "Alice Chen",
  "mrn": "SYN-MRN-00001",
  "appointments": [],
  "visit_notes": [],
  "imaging": []
}
```

Retrieval is **in-memory keyword filtering** (`knowledge/synthetic.py`) — not pgvector. That is intentional for a governance showcase.

---

## Authorization test matrix

| User scope | Can access Alice | Can access John |
|------------|------------------|-----------------|
| `patient:alice` | Yes | No |
| `patient:john` | No | Yes |

Encoded in `evaluation/phi.py` and `governance/authorization.py`.

---

## Why synthetic?

Governance architecture is the subject. Real PHI would force BAA / IRB scope this reference repo is not designed to satisfy. The **control patterns** transfer to production systems with proper legal review.
