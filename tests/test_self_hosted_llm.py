"""Self-hosted open-weight model adapter for in-boundary reasoning."""

from llm.provider import OpenWeightReasoningModel


def test_self_hosted_model_builds_openai_compatible_payload(monkeypatch):
    captured = {}

    class DummyResponse:
        status_code = 200

        def json(self):
            return {
                "choices": [{"message": {"content": "Local answer"}}]
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return DummyResponse()

    monkeypatch.setenv("SELF_HOSTED_LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("SELF_HOSTED_LLM_API_KEY", "ollama")
    monkeypatch.setenv("SELF_HOSTED_LLM_MODEL", "llama3.1:8b")
    monkeypatch.setenv("USE_SELF_HOSTED_LLM", "true")
    monkeypatch.setattr("llm.provider.httpx.post", fake_post)

    llm = OpenWeightReasoningModel()
    result = llm.generate(
        "Email alice@example.com, account number: 123456789012",
        [{"role": "user", "content": "Mail to 123 Main Street, Springfield, NY 10001"}],
        system_instruction="Contact alice@example.com only if needed.",
    )

    assert result == "Local answer"
    assert captured["url"] == "http://localhost:11434/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer ollama"
    assert captured["json"]["model"] == "llama3.1:8b"
    sent_text = " ".join(message["content"] for message in captured["json"]["messages"])
    assert "alice@example.com" not in sent_text
    assert "123456789012" not in sent_text
    assert "123 Main Street" not in sent_text
    assert "[EMAIL]" in sent_text
    assert "[ACCOUNT_NUMBER]" in sent_text
    assert "[ADDRESS]" in sent_text
