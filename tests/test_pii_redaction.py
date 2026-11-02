"""PII redaction behavior before sending prompts to the LLM."""

from privacy.redaction import redact_history, redact_pii


def test_redacts_common_pii_patterns():
    text = (
        "My email is alice@example.com and my phone is 555-123-4567. "
        "Card 4111 1111 1111 1111 and SSN 123-45-6789."
    )

    redacted = redact_pii(text)

    assert "alice@example.com" not in redacted
    assert "555-123-4567" not in redacted
    assert "4111 1111 1111 1111" not in redacted
    assert "123-45-6789" not in redacted
    assert "[EMAIL]" in redacted
    assert "[PHONE]" in redacted
    assert "[CARD_NUMBER]" in redacted
    assert "[SSN]" in redacted


def test_redacts_history_without_touching_normal_text():
    history = [
        {"role": "user", "content": "Hi, my email is bob@example.com"},
        {"role": "assistant", "content": "Sure, I can help you."},
    ]

    sanitized = redact_history(history)

    assert sanitized[0]["content"] == "Hi, my email is [EMAIL]"
    assert sanitized[1]["content"] == "Sure, I can help you."
