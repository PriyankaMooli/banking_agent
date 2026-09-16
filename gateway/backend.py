"""Dummy backend business logic, fronted by the gateway.

Swap `answer` for a real HTTP/LLM call to backend banking services
later; the gateway only depends on this function's signature.
"""

import random
import time

_CANNED_RESPONSES = {
    "balance": "Your checking account balance is $4,231.87.",
    "transfer": "Sure — how much would you like to transfer, and to which account?",
    "transaction": "Your last transaction was a $52.40 charge at Whole Foods on Sep 12.",
    "card": "Your card ending in 4471 is active and in good standing.",
    "loan": "You currently have no active loans on this account.",
    "hello": "Hi! I'm your banking assistant. Ask me about balances, transfers, or recent transactions.",
}

_FALLBACK_RESPONSES = [
    "Got it — let me look into that for you.",
    "I can help with that. Could you give me a bit more detail?",
    "Thanks for the info. Here's a placeholder response until the real API is wired up.",
]


def answer(message: str, history: list[dict]) -> str:
    """Return a dummy backend reply for the given user message.

    `history` is the list of prior {"role", "content"} turns, unused by
    the dummy implementation but kept in the signature so the real
    backend can use it for context.
    """
    time.sleep(0.4)  # simulate network latency

    lowered = message.lower()
    for keyword, response in _CANNED_RESPONSES.items():
        if keyword in lowered:
            return response

    return random.choice(_FALLBACK_RESPONSES)
