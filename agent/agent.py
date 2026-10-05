"""The agent layer — a tool-using Gemini agent for banking questions.

Called by backend/main.py. Owns the system prompt and does only tool
selection reasoning: balance and transaction lookups are delegated to the
MCP-backed wrappers in agent/accounts.py and agent/transactions.py, while
card and loan status (no MCP server yet) still call the mocks in
agent/tools.py directly. Gemini's automatic function calling decides when
to call each tool and feeds results back in.
"""

from llm.provider import create_reasoning_model
from privacy.redaction import sanitize_for_llm

SYSTEM_PROMPT = (
    "You are a helpful banking assistant. The coordinator may include "
    "verified banking tool results in the request. Use only those results "
    "for account-specific facts, and never claim to have called a tool. "
    "If a requested fact is not included, say it is unavailable. For "
    "general questions, be concise and friendly. Never invent account data."
)


class BankingAgent:
    def __init__(self) -> None:
        self._reasoning_model = create_reasoning_model()

    def run(self, message: str, history: list[dict]) -> str:
        """Answer one user message, using tools as needed, and return the reply text."""
        safe_message, safe_history = sanitize_for_llm(message, history)
        if self._reasoning_model is None:
            raise RuntimeError(
                "Self-hosted reasoning is required for routine requests; "
                "set USE_SELF_HOSTED_LLM=true"
            )
        return self._reasoning_model.generate(
            safe_message,
            safe_history,
            system_instruction=SYSTEM_PROMPT,
        )
