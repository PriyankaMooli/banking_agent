"""Service specialist for checkbook, address, and credit-limit questions."""

import os

from google import genai
from google.genai import types

from agent.tools import get_address, get_checkbook_info, get_credit_limit

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are the banking service specialist. Handle only checkbook, mailing "
    "address, and credit-limit questions. Always use the relevant tool before "
    "answering. You may explain the verified service information, but never "
    "invent an address, checkbook detail, or credit limit. Be concise and "
    "protect sensitive information by sharing only what the tool returns."
)


class ServiceAgent:
    """Answer service questions using verified service information only."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_checkbook_info, get_address, get_credit_limit],
        )

    def run(self, message: str, history: list[dict]) -> str:
        """Answer one checkbook, address, or credit-limit request."""
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