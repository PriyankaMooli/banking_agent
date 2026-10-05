"""Transactions specialist for transaction-related reasoning."""

import os

from google import genai
from google.genai import types

from agent.mcp_bridge import call_mcp_tool
from agent.prompts import get_prompt
from privacy.redaction import sanitize_for_llm

MODEL = "gemini-3.5-flash-lite"

def get_account_transactions(count: int = 3) -> dict:
    """Call the Transactions MCP server for recent transactions."""
    return call_mcp_tool(
        "agent.transactions_mcp",
        "get_account_transactions",
        {"count": count},
    )


class TransactionsAgent:
    """Answer transaction questions using only verified transaction data."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=get_prompt("transactions_specialist").text,
            tools=[get_account_transactions],
        )

    def run(self, message: str, history: list[dict]) -> str:
        """Answer one transaction-related request."""
        safe_message, safe_history = sanitize_for_llm(message, history)
        chat = self._client.chats.create(
            model=MODEL,
            config=self._config,
            history=[
                types.Content(
                    role="model" if turn["role"] == "assistant" else "user",
                    parts=[types.Part(text=turn["content"])],
                )
                for turn in safe_history
            ],
        )
        response = chat.send_message(safe_message)
        return response.text