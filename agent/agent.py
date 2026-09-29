"""The agent layer — a tool-using Gemini agent for banking questions.

Called by backend/main.py. Owns the system prompt and does only tool
selection reasoning: balance and transaction lookups are delegated to the
MCP-backed wrappers in agent/accounts.py and agent/transactions.py, while
card and loan status (no MCP server yet) still call the mocks in
agent/tools.py directly. Gemini's automatic function calling decides when
to call each tool and feeds results back in.
"""

import os

from google import genai
from google.genai import types

from agent.accounts import get_account_balance
from agent.tools import get_card_status, get_loan_status
from agent.transactions import get_account_transactions

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are a helpful banking assistant. Answer questions about the "
    "customer's balances, transactions, card status, and loans using the "
    "tools provided. Be concise and friendly. Never make up account "
    "information — always call a tool to look it up."
)


class BankingAgent:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_account_balance, get_account_transactions, get_card_status, get_loan_status],
        )

    def run(self, message: str, history: list[dict]) -> str:
        """Answer one user message, using tools as needed, and return the reply text."""
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
