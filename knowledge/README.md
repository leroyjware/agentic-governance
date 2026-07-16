# Knowledge — synthetic store

```
knowledge/
├── data/patients.json   # Healthcare: Alice + John
├── data/claims.json     # Claims vertical: member Alice + John
├── synthetic.py         # Healthcare retrieval
└── claims_store.py      # Claims retrieval
```

Not pgvector. Authorization must run before retrieval. See [docs/SYNTHETIC-DATA.md](../docs/SYNTHETIC-DATA.md).
