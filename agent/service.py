"""Service specialist for checkbook, address, and credit-limit questions."""

import os

from google import genai
from google.genai import types

from agent.mcp_bridge import call_mcp_tool

MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = (
    "You are the banking service specialist and MCP tool selector. Handle only "
    "checkbook, mailing address, and credit-limit questions. Select the relevant "
    "MCP tool before answering. Use only MCP results; never invent service data."
)


def get_checkbook() -> dict:
    """Call the Service MCP server for checkbook information."""
    return call_mcp_tool("agent.service_mcp", "get_checkbook", {})


def get_customer_address() -> dict:
    """Call the Service MCP server for the customer's address."""
    return call_mcp_tool("agent.service_mcp", "get_customer_address", {})


def get_customer_credit_limit() -> dict:
    """Call the Service MCP server for credit-limit information."""
    return call_mcp_tool("agent.service_mcp", "get_customer_credit_limit", {})


class ServiceAgent:
    """Answer service questions using verified service information only."""

    def __init__(self) -> None:
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_checkbook, get_customer_address, get_customer_credit_limit],
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