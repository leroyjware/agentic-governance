# How to add an agent

A new specialist is mostly a **harness edit** plus a thin LangGraph node.

## 1. Declare the agent in the harness

Edit `harness/harness.jsonld`. Copy an existing `sh:Agent` (e.g. Healthcare Planner):

```json
{
  "@id": "urn:uuid:....",
  "@type": "sh:Agent",
  "sh:name": "Claims Specialist",
  "sh:description": "Answers claim status using tools only.",
  "sh:systemRole": "You answer claim status questions using tools only...",
  "sh:model": "llama-3.3-70b-versatile",
  "sh:temperature": 0.0,
  "sh:maxTurns": 4,
  "sh:hasSkill": ["urn:uuid:...."],
  "sh:hasTool": ["urn:uuid:...."]
}
```

Also:

1. Add the agent id under root `sh:Harness` → `sh:agents`
2. Add any new `sh:Tool` rows and include them in `sh:Policy` `sh:allowlist`
3. Add a `sh:Workflow` step with `sh:agentRef` (documentation of intent)

Validate:

```bash
make validate-harness
```

## 2. Implement the tool (if needed)

Add a `@tool` function in `agent/tools.py` and append it to `ALL_TOOLS`.  
Keep scoping via `set_request_scope` — never trust model-supplied patient ids.

Tool names in Python must match `sh:Tool` `sh:name`.

## 3. Add a LangGraph node

In `agent/workflow.py`:

1. Load prompts with `load_harness().system_prompt("Claims Specialist")`
2. Implement `node_claims(state) -> dict`
3. Register in `NODE_REGISTRY`
4. Wire edges in `build_workflow()` (topology is explicit in Python — harness step IDs must stay aligned)

```python
h = load_harness()
prompt = h.system_prompt("Claims Specialist")
tools = tools_by_names(h.allowed_tools_for_agent("Claims Specialist"))
```

## 4. Prove it

Add scenarios to `evaluation/` (or `scripts/live_graph_cases.py` for graph mode) and run:

```bash
make gate
make live   # if GROQ_API_KEY set
```

## Layering

| Layer | Owns |
|-------|------|
| Semantic Harness | Who the agent is, tools, policy, invariants |
| LangGraph | How steps run and branch |
| Evaluation | Whether the behavior is shippable |
