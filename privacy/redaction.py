"""PII redaction for outbound LLM prompts."""

from __future__ import annotations

import re

EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9._%+-])"
)
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})(?!\d)"
)
SSN_RE = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")


def redact_pii(text: str) -> str:
    """Replace common personal information with neutral placeholders."""
    redacted = text
    redacted = EMAIL_RE.sub("[EMAIL]", redacted)
    redacted = PHONE_RE.sub("[PHONE]", redacted)
    redacted = SSN_RE.sub("[SSN]", redacted)
    redacted = CARD_RE.sub("[CARD_NUMBER]", redacted)
    return redacted


def redact_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
    """Redact PII in a list of chat turns while preserving message shape."""
    sanitized: list[dict[str, str]] = []
    for turn in history:
        sanitized_turn = {"role": turn.get("role", "user"), "content": redact_pii(turn.get("content", ""))}
        sanitized.append(sanitized_turn)
    return sanitized


def sanitize_for_llm(message: str, history: list[dict[str, str]] | None = None) -> tuple[str, list[dict[str, str]]]:
    """Return a prompt-safe version of the message and history."""
    sanitized_history = redact_history(history or [])
    return redact_pii(message), sanitized_history
