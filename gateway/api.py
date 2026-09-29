"""API gateway — the single entry point the UI calls into the backend.

Forwards every request to the backend (gateway/backend.py). Swap
backend.answer for a real HTTP call to a backend service later; the UI
only depends on this module's `get_response` signature.
"""

from gateway import backend


def get_response(message: str, history: list) -> str:
    return backend.answer(message, history)
