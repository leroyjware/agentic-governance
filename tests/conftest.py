"""Test defaults — no audit file noise, rules mode unless opted in."""

import os

os.environ.setdefault("AUDIT_LOG_PATH", "off")
os.environ.setdefault("AGENT_MODE", "rules")
os.environ.setdefault("AUTH_STRICT", "0")
