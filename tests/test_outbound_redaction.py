"""Raw PII must be removed before any model adapter sends prompts."""

from privacy.redaction import redact_pii
from llm.escalation import ThirdPartyReasoningModel


def test_redacts_street_addresses_and_labeled_account_numbers():
    prompt = "Mail my statement to 123 Main Street, Springfield, NY 10001. Account number: 123456789012."

    result = redact_pii(prompt)

    assert "123 Main Street" not in result
    assert "Springfield" not in result
    assert "10001" not in result
    assert "123456789012" not in result
    assert "[ADDRESS]" in result
    assert "[ACCOUNT_NUMBER]" in result


def test_third_party_adapter_sanitizes_all_outbound_text():
    captured = {}

    class DummyResponse:
        text = "safe response"

    class DummyChat:
        def send_message(self, prompt):
            captured["prompt"] = prompt
            return DummyResponse()

    class DummyChats:
        def create(self, **kwargs):
            captured.update(kwargs)
            return DummyChat()

    model = ThirdPartyReasoningModel.__new__(ThirdPartyReasoningModel)
    model._client = type("Client", (), {"chats": DummyChats()})()
    model._model = "test-model"

    result = model.generate(
        "My email is alice@example.com and account number: 123456789012",
        [{"role": "user", "content": "Address: 123 Main Street, Springfield, NY 10001"}],
        system_instruction="Contact alice@example.com if needed.",
    )

    outbound_text = [captured["prompt"], captured["config"].system_instruction]
    outbound_text.extend(turn.parts[0].text for turn in captured["history"])
    outbound_text = " ".join(outbound_text)
    assert result == "safe response"
    assert "alice@example.com" not in outbound_text
    assert "123456789012" not in outbound_text
    assert "123 Main Street" not in outbound_text
    assert "[EMAIL]" in outbound_text
    assert "[ACCOUNT_NUMBER]" in outbound_text
    assert "[ADDRESS]" in outbound_text
