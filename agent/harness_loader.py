"""Load Semantic Harness JSON-LD — architecture declaration for this runtime.

Semantic Harness *declares* agents, skills, tools, workflow, policies, invariants.
This module makes that declaration queryable so LangGraph nodes are not hard-coded
string soup — add an sh:Agent to harness.jsonld and register a node factory.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

HARNESS_PATH = Path(__file__).resolve().parents[1] / "harness" / "harness.jsonld"


@dataclass
class HarnessObject:
    raw: dict[str, Any]

    @property
    def id(self) -> str:
        return self.raw["@id"]

    @property
    def type(self) -> str:
        t = self.raw["@type"]
        return t if isinstance(t, str) else t[0]

    def get(self, key: str, default: Any = None) -> Any:
        # Support both sh:foo and foo
        if key in self.raw:
            return self.raw[key]
        if not key.startswith("sh:"):
            return self.raw.get(f"sh:{key}", default)
        return default


@dataclass
class LoadedHarness:
    path: Path
    objects: list[HarnessObject]
    by_id: dict[str, HarnessObject] = field(default_factory=dict)
    by_type: dict[str, list[HarnessObject]] = field(default_factory=dict)

    def agents(self) -> list[HarnessObject]:
        return self.by_type.get("sh:Agent", [])

    def agent_by_name(self, name: str) -> HarnessObject | None:
        for a in self.agents():
            if a.get("name") == name:
                return a
        return None

    def skills_for(self, agent: HarnessObject) -> list[str]:
        bodies: list[str] = []
        for ref in agent.get("hasSkill") or []:
            skill = self.by_id.get(ref)
            if skill and skill.get("body"):
                bodies.append(str(skill.get("body")))
        return bodies

    def tools_for(self, agent: HarnessObject) -> list[str]:
        names: list[str] = []
        for ref in agent.get("hasTool") or []:
            tool = self.by_id.get(ref)
            if tool and tool.get("name"):
                names.append(str(tool.get("name")))
        return names

    def workflow(self) -> HarnessObject | None:
        workflows = self.by_type.get("sh:Workflow", [])
        return workflows[0] if workflows else None

    def system_prompt(self, agent_name: str) -> str:
        agent = self.agent_by_name(agent_name)
        if not agent:
            raise KeyError(f"Agent not in harness: {agent_name}")
        role = agent.get("systemRole") or ""
        skills = self.skills_for(agent)
        parts = [role.strip()]
        if skills:
            parts.append("\n## Skills (from Semantic Harness)\n")
            parts.extend(skills)
        return "\n".join(parts).strip()

    def model_for(self, agent_name: str, default: str = "llama-3.3-70b-versatile") -> str:
        agent = self.agent_by_name(agent_name)
        if not agent:
            return default
        # Harness may declare OpenAI names; runtime maps via env / llm.py
        return str(agent.get("model") or default)

    def policies(self) -> list[HarnessObject]:
        return self.by_type.get("sh:Policy", [])

    def policy_tool_names(self, policy_name: str | None = None) -> set[str]:
        """Resolve sh:Policy allowlist URNs to tool names."""
        policies = self.policies()
        if not policies:
            return set()
        if policy_name:
            selected = [p for p in policies if p.get("name") == policy_name]
        else:
            selected = policies
        names: set[str] = set()
        for pol in selected:
            for ref in pol.get("allowlist") or []:
                tool = self.by_id.get(ref)
                if tool and tool.get("name"):
                    names.add(str(tool.get("name")))
        return names

    def allowed_tools_for_agent(self, agent_name: str) -> set[str]:
        """Intersection of agent hasTool and global sh:Policy allowlist (when present)."""
        agent = self.agent_by_name(agent_name)
        agent_tools = set(self.tools_for(agent)) if agent else set()
        policy_tools = self.policy_tool_names()
        # check_authorization is a governance step, not a LangChain tool
        policy_tools.discard("check_authorization")
        if not policy_tools:
            return agent_tools
        if not agent_tools:
            return policy_tools
        return agent_tools & policy_tools


@lru_cache(maxsize=1)
def load_harness(path: str | None = None) -> LoadedHarness:
    p = Path(path) if path else HARNESS_PATH
    data = json.loads(p.read_text(encoding="utf-8"))
    graph = data.get("@graph") or []
    objects = [HarnessObject(o) for o in graph if isinstance(o, dict) and "@id" in o]
    by_id = {o.id: o for o in objects}
    by_type: dict[str, list[HarnessObject]] = {}
    for o in objects:
        by_type.setdefault(o.type, []).append(o)
    return LoadedHarness(path=p, objects=objects, by_id=by_id, by_type=by_type)
