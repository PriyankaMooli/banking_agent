"""Only complex coordinator responses use the third-party model."""

import agent.coordinator as coordinator


def _state(message):
    return {
        "message": message,
        "history": [{"role": "user", "content": message}],
        "principal": {"subject": "test-user", "tier": "customer"},
        "plan": [],
        "next_agent": 0,
        "findings": [],
        "reply": "",
    }


def test_routine_response_uses_self_hosted_model(monkeypatch):
    calls = []

    class LocalModel:
        def run(self, prompt, history):
            calls.append((prompt, history))
            return "local reply"

    class ExternalModel:
        def __init__(self):
            raise AssertionError("routine request must not instantiate Gemini")

    monkeypatch.setattr(coordinator, "requires_external_reasoning", lambda _message: False)
    monkeypatch.setattr(coordinator, "BankingAgent", LocalModel)
    monkeypatch.setattr(coordinator, "ThirdPartyReasoningModel", ExternalModel)

    result = coordinator._respond(_state("Hi"))

    assert result["reply"] == "local reply"
    assert calls[0][1] == []


def test_complex_response_uses_third_party_model(monkeypatch):
    calls = []

    class ExternalModel:
        def generate(self, prompt, history, system_instruction):
            calls.append((prompt, history, system_instruction))
            return "complex reply"

    class LocalModel:
        def run(self, _prompt, _history):
            raise AssertionError("complex request should use external reasoning")

    monkeypatch.setattr(coordinator, "requires_external_reasoning", lambda _message: True)
    monkeypatch.setattr(coordinator, "BankingAgent", LocalModel)
    monkeypatch.setattr(coordinator, "ThirdPartyReasoningModel", ExternalModel)

    result = coordinator._respond(_state("Compare checking and savings balances"))

    assert result["reply"] == "complex reply"
    assert calls[0][1] == []
