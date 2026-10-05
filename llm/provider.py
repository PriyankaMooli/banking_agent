"""Self-hosted open-weight LLM adapter for in-boundary reasoning."""

from __future__ import annotations

import os
from typing import Any

import httpx

from privacy.redaction import redact_pii, sanitize_for_llm


class OpenWeightReasoningModel:
    """OpenAI-compatible local model client for a self-hosted LLM server."""

    def __init__(self) -> None:
        self.base_url = os.environ.get("SELF_HOSTED_LLM_BASE_URL", "http://localhost:11434/v1")
        self.api_key = os.environ.get("SELF_HOSTED_LLM_API_KEY", "ollama")
        self.model = os.environ.get("SELF_HOSTED_LLM_MODEL", "llama3.1:8b")
        self.enabled = os.environ.get("USE_SELF_HOSTED_LLM", "false").lower() in {"1", "true", "yes", "on"}

    def _build_messages(
        self,
        prompt: str,
        history: list[dict[str, str]] | None = None,
        system_instruction: str | None = None,
    ) -> list[dict[str, str]]:
        safe_prompt, safe_history = sanitize_for_llm(prompt, history)
        messages: list[dict[str, str]] = []
        if system_instruction:
            messages.append({"role": "system", "content": redact_pii(system_instruction)})
        for turn in safe_history:
            role = turn.get("role")
            content = turn.get("content", "")
            if role in {"user", "assistant"}:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": safe_prompt})
        return messages

    def generate(
        self,
        prompt: str,
        history: list[dict[str, str]] | None = None,
        system_instruction: str | None = None,
    ) -> str:
        if not self.enabled:
            raise RuntimeError("Self-hosted LLM is disabled; set USE_SELF_HOSTED_LLM=true")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": self._build_messages(prompt, history, system_instruction),
            "temperature": 0.2,
        }
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=60.0,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Self-hosted LLM request failed: {response.text}")

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Invalid response from self-hosted model") from exc


def create_reasoning_model() -> OpenWeightReasoningModel | None:
    provider = OpenWeightReasoningModel()
    return provider if provider.enabled else None
