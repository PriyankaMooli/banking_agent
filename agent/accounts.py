"""Accounts specialist for balance and account-related reasoning."""

import os

from google import genai
from google.genai import types

from agent.mcp_bridge import call_mcp_tool
from privacy.redaction import sanitize_for_llm

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are the accounts specialist and MCP tool selector. Handle only "
    "balance and account questions. Select get_account_balance when account "
    "data is needed. Use only the MCP result; never invent account information. "
    "You may compare verified balances or calculate a verified total."
)


def get_account_balance(account: str = "checking") -> dict:
    """Call the Accounts MCP server for one account balance."""
    return call_mcp_tool(
        "agent.accounts_mcp",
        "get_account_balance",
        {"account": account},
    )


class AccountsAgent:
    """Answer balance questions using only verified account data."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_account_balance],
        )

    def run(self, message: str, history: list[dict]) -> str:
        """Answer one balance-related request."""
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