"""Backend client — calls the backend API over HTTP.

The backend API (backend/main.py) receives the request and calls the agent
layer (agent/agent.py). Run it separately with:
    uvicorn backend.main:app --port 8001
"""

import logging
import os

import httpx

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")

logger = logging.getLogger(__name__)


def answer(message: str, history: list[dict]) -> str:
    """Return the backend API's reply for the given user message.

    `history` is the list of prior {"role", "content"} turns, forwarded
    so the agent layer has conversation context.
    """
    try:
        response = httpx.post(
            f"{BACKEND_URL}/chat",
            json={"message": message, "history": history},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["reply"]
    except httpx.HTTPError:
        logger.exception("Backend API call failed")
        return (
            "Sorry, I'm having trouble reaching the banking backend right now. "
            "Please try again shortly."
        )
