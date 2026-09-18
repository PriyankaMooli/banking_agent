"""Transactions specialist for transaction-related reasoning."""

import os

from google import genai
from google.genai import types

from agent.tools import get_recent_transactions

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are the transactions specialist for a banking assistant. Handle only "
    "transaction and spending questions. Always use the "
    "get_recent_transactions tool before answering. You may summarize, count, "
    "or calculate totals from the returned transactions, but never invent a "
    "transaction, merchant, date, or amount. Be concise and clearly explain "
    "debits and credits."
)


class TransactionsAgent:
    """Answer transaction questions using only verified transaction data."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_recent_transactions],
        )

    def run(self, message: str, history: list[dict]) -> str:
        """Answer one transaction-related request."""
        chat = self._client.chats.create(
            model=MODEL,
            config=self._config,
            history=[
                types.Content(
                    role="model" if turn["role"] == "assistant" else "user",
                    parts=[types.Part(text=turn["content"])],
                )
                for turn in history
            ],
        )
        response = chat.send_message(message)
        return response.text