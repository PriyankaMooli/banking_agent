"""Gemini-based intent classification for coordinator routing."""

import json
import os

from google import genai
from google.genai import types

MODEL = "gemini-3.5-flash-lite"
SUPPORTED_INTENTS = ("balance", "transactions", "service", "card", "loan")

SYSTEM_PROMPT = (
    "Classify banking user requests for routing. Return JSON only in the form "
    '{"intents": ["balance", "transactions"]}. Choose zero or more intents '
    "from this exact list: balance, transactions, service, card, loan. "
    "Use balance for account balances, transactions for purchases and spending, "
    "service for checkbooks, addresses, and credit limits, card for card status, "
    "and loan for loan status. Preserve the order in which the user asks for "
    "topics. For greetings or unrelated questions, return an empty list."
)


class IntentClassifier:
    """Classify a message into the coordinator's supported specialist routes."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        )

    def classify(self, message: str) -> list[str]:
        """Return validated intent names, or raise if Gemini returns bad output."""
        response = self._client.models.generate_content(
            model=MODEL,
            contents=message,
            config=self._config,
        )
        payload = json.loads(response.text)
        intents = payload["intents"]
        if not isinstance(intents, list):
            raise ValueError("intents must be a list")

        valid_intents = []
        for intent in intents:
            if intent in SUPPORTED_INTENTS and intent not in valid_intents:
                valid_intents.append(intent)
        return valid_intents