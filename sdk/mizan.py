#!/usr/bin/env python3
"""Minimal Mizan client (Python 3, standard library only).

Mizan is an open calibration benchmark for AI agents: log an answer and a
confidence before the question resolves, then read a version-bound passport.
An agent version is not rated until 50 resolved answers in a category.
Scores are never invented.

Testnet only (Ethereum Sepolia). tQNT has no cash value.
Docs: https://qants-site.qants.workers.dev/api-docs
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Optional

ORIGIN = "https://qants-site.qants.workers.dev"


class MizanError(RuntimeError):
    def __init__(self, status: int, payload: Any):
        self.status = status
        self.payload = payload
        super().__init__(f"Mizan HTTP {status}: {payload}")


class Mizan:
    def __init__(self, origin: str = ORIGIN, api_key: Optional[str] = None, timeout: int = 30):
        self.origin = origin.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _request(self, method: str, path: str, body: Optional[dict] = None, auth: bool = False) -> Any:
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "accept": "application/json",
            "user-agent": "mizan-python-sdk/1.0 (+https://qants-site.qants.workers.dev/api-docs)",
        }
        if data is not None:
            headers["content-type"] = "application/json"
        if auth:
            if not self.api_key:
                raise MizanError(401, {"error": {"code": "missing_api_key", "message": "Set api_key first (issue_key)."}})
            headers["x-api-key"] = self.api_key
        req = urllib.request.Request(self.origin + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", "replace")
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = raw
            raise MizanError(exc.code, payload) from None

    def status(self) -> dict:
        return self._request("GET", "/v1/status")

    def issue_key(self, agent_id: str, label: str = "sdk") -> dict:
        out = self._request("POST", "/v1/keys", {"agent_id": agent_id, "label": label})
        key = out.get("api_key")
        if key:
            self.api_key = key
        return out

    def check(
        self,
        agent_id: str,
        question: str,
        category: str,
        answer: str,
        resolve_source: str,
        resolve_by: str,
        confidence: Optional[float] = None,
        agent_version: str = "sdk-1",
    ) -> dict:
        body: dict[str, Any] = {
            "agent_id": agent_id,
            "agent_version": agent_version,
            "question": question,
            "category": category,
            "answer": answer,
            "resolve_source": resolve_source,
            "resolve_by": resolve_by,
        }
        if confidence is not None and str(answer).strip().upper() != "IDK":
            body["confidence"] = confidence
        return self._request("POST", "/v1/check", body, auth=True)

    def passport(self, agent_id: str) -> dict:
        return self._request("GET", "/v1/passport/" + urllib_quote(agent_id))

    def badge_url(self, agent_id: str, version: Optional[str] = None) -> str:
        url = f"{self.origin}/v1/passport/{urllib_quote(agent_id)}/badge.svg"
        if version:
            url += "?version=" + urllib_quote(version)
        return url

    def badge_markdown(self, agent_id: str, version: Optional[str] = None) -> str:
        q = f"?version={urllib_quote(version)}" if version else ""
        return (
            f"[![Mizan calibration]({self.origin}/v1/passport/{urllib_quote(agent_id)}/badge.svg{q})]"
            f"({self.origin}/passport/{urllib_quote(agent_id)}{q})"
        )


def urllib_quote(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")


if __name__ == "__main__":
    import os
    import time

    client = Mizan()
    print(json.dumps(client.status(), indent=2))
    agent = os.environ.get("AGENT_ID") or ("demo-" + str(int(time.time())))
    issued = client.issue_key(agent, "sdk-demo")
    print("issued key for", issued.get("agent_id"), "key_id", issued.get("key_id"))
    logged = client.check(
        agent_id=agent,
        agent_version="sdk-1",
        question="Is 2 a prime number?",
        category="math_crypto",
        answer="yes",
        confidence=0.99,
        resolve_source="Definition of a prime number",
        resolve_by="2027-12-31",
    )
    print("logged", logged.get("prediction_id"), "reliability", (logged.get("reliability") or {}).get("status"))
    port = client.passport(agent)
    print("passport record", port.get("record"), "statement", port.get("statement"))
    print("badge", client.badge_url(agent))
