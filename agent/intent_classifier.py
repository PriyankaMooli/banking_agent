"""Gemini-based intent classification for coordinator routing."""

import json
import os

from google import genai
from google.genai import types

from agent.prompts import get_prompt
from privacy.redaction import redact_pii

MODEL = "gemini-3.5-flash-lite"
SUPPORTED_INTENTS = ("balance", "transactions", "service", "card", "loan")

class IntentClassifier:
    """Classify a message into the coordinator's supported specialist routes."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=get_prompt("intent_classifier").text,
            response_mime_type="application/json",
        )

    def classify(self, message: str) -> list[str]:
        """Return validated intent names, or raise if Gemini returns bad output."""
        safe_message = redact_pii(message)
        chat = self._client.chats.create(
            model=MODEL,
            config=self._config,
        )
        response = chat.send_message(safe_message)
        payload = json.loads(response.text)
        intents = payload["intents"]
        if not isinstance(intents, list):
            raise ValueError("intents must be a list")

        valid_intents = []
        for intent in intents:
            if intent in SUPPORTED_INTENTS and intent not in valid_intents:
                valid_intents.append(intent)
        return valid_intents