import json
from types import SimpleNamespace

import pytest

from app.agents import llm


class FakeClient:
    def __init__(self, response):
        self.responses = SimpleNamespace(create=lambda **_kwargs: SimpleNamespace(output_text=json.dumps(response)))


@pytest.mark.parametrize("sensitive_context", [
    "Earlier message: What salary range are you targeting?",
    "Previous thread discussed interview scheduling.",
    "Please confirm your passport details.",
])
def test_recruiter_context_sensitive_topics_require_human(monkeypatch, sensitive_context):
    monkeypatch.setattr(llm, "_client", lambda: FakeClient({
        "reply": "Thanks, I will get back to you.",
        "confidence": 0.9,
        "requires_human": False,
        "reason": "simple acknowledgment",
    }))

    _reply, _confidence, requires_human, _reason = llm.recruiter_reply(
        "Thanks for the update.", [], context=sensitive_context,
    )

    assert requires_human is True


def test_recruiter_honors_json_false_when_context_is_not_sensitive(monkeypatch):
    monkeypatch.setattr(llm, "_client", lambda: FakeClient({
        "reply": "Thanks, I will review this.",
        "confidence": 0.9,
        "requires_human": "false",
        "reason": "acknowledgment only",
    }))

    _reply, _confidence, requires_human, _reason = llm.recruiter_reply(
        "Thank you for sharing the role.", [], context="",
    )

    assert requires_human is False
