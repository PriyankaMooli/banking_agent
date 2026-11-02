"""Third-party reasoning used only after local complexity escalation."""

from __future__ import annotations

import os

from google import genai
from google.genai import types

from agent.prompts import get_prompt
from privacy.redaction import redact_pii, sanitize_for_llm


class ThirdPartyReasoningModel:
    """Gemini-backed reasoning adapter, instantiated only for complex requests."""

    def __init__(self) -> None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required for complex reasoning escalation")
        self._client = genai.Client(api_key=api_key)
        self._model = os.environ.get("THIRD_PARTY_LLM_MODEL", "gemini-3.5-flash-lite")

    def generate(
        self,
        prompt: str,
        history: list[dict[str, str]] | None = None,
        system_instruction: str | None = None,
    ) -> str:
        safe_prompt, safe_history = sanitize_for_llm(prompt, history)
        chat = self._client.chats.create(
            model=self._model,
            config=types.GenerateContentConfig(
                system_instruction=redact_pii(
                    system_instruction or get_prompt("complex_reasoning").text
                )
            ),
            history=[
                types.Content(
                    role="model" if turn["role"] == "assistant" else "user",
                    parts=[types.Part(text=turn["content"])],
                )
                for turn in safe_history
            ],
        )
        response = chat.send_message(safe_prompt)
        return response.text
