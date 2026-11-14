#!/usr/bin/env python3
"""Log one check and read the passport. Does not print the API key."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sdk"))
from mizan import Mizan

AGENT = "your-agent-v1.0.0"
client = Mizan()
issued = client.issue_key(AGENT, "example")
print("issued key_id", issued.get("key_id"), "for", issued.get("agent_id"))
logged = client.check(
    agent_id=AGENT,
    agent_version="example-1",
    question="What is 2+2?",
    category="math_crypto",
    answer="4",
    confidence=0.9,
    resolve_source="Elementary arithmetic",
    resolve_by="2027-12-31T00:00:00Z",
)
print("logged", logged.get("prediction_id"))
print(json.dumps(client.passport(AGENT), indent=2))
print("badge markdown:")
print(client.badge_markdown(AGENT))
