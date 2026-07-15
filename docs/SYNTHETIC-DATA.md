# Synthetic Data Policy

This repository uses **100% synthetic healthcare data**. No real PHI. Ever.

---

## Rules

1. All patient names, MRNs, DOBs, and clinical notes are **generated** (Faker / hand-crafted fixtures)
2. Static CI scan rejects real PHI patterns in commits
3. README and docs clearly state "demonstration only — not HIPAA compliant"
4. No connectors to real EHR systems in this reference implementation

---

## Synthetic patient schema

```json
{
  "patient_id": "syn-patient-001",
  "display_name": "Alice Chen",
  "mrn": "SYN-MRN-00001",
  "dob": "1985-03-15",
  "appointments": [],
  "visit_notes": [],
  "imaging": []
}
```

Files live in `knowledge/documents/synthetic/patients/` (Phase 1).

---

## Authorization test matrix

| User scope | Can access Alice | Can access John |
|------------|------------------|-----------------|
| `patient:alice` | Yes | No |
| `patient:john` | No | Yes |
| `clinician:team-a` | Assigned only | Assigned only |

PHI leakage tests in `evaluation/phi/` encode this matrix.

---

## Why synthetic?

Governance architecture is the subject. Real PHI would distract with BAA, IRB, and compliance scope that this reference repo is not designed to satisfy.

The **controls demonstrated** transfer to production systems with real data and proper legal review.
