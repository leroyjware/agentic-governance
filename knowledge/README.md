# Knowledge — synthetic store

```
knowledge/
├── data/patients.json   # Alice + John (synthetic only)
└── synthetic.py         # In-memory keyword retrieval by authorized scope
```

Not pgvector. Authorization must run before `retrieve_for_scope`. See [docs/SYNTHETIC-DATA.md](../docs/SYNTHETIC-DATA.md).
