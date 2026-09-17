"""Accounts specialist for balance and account-related reasoning."""

import os

from google import genai
from google.genai import types

from agent.tools import get_balance

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are the accounts specialist for a banking assistant. Handle only "
    "balance and account questions. Always use the get_balance tool before "
    "answering. You may compare account balances or calculate a total when "
    "the user asks, but never invent account information. Be concise and "
    "clearly identify each account and amount."
)


class AccountsAgent:
    """Answer balance questions using only verified account data."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_balance],
        )

    def run(self, message: str, history: list[dict]) -> str:
        """Answer one balance-related request."""
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