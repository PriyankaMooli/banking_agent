"""In-memory session store for chat history."""

from __future__ import annotations

from threading import Lock
from typing import Any


class SessionStore:
    """Track conversation history per user session."""

    def __init__(self) -> None:
        self._history: dict[str, list[dict[str, str]]] = {}
        self._lock = Lock()

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        with self._lock:
            return [turn.copy() for turn in self._history.get(session_id, [])]

    def append_turn(self, session_id: str, role: str, content: str) -> list[dict[str, str]]:
        with self._lock:
            history = self._history.setdefault(session_id, [])
            history.append({"role": role, "content": content})
            return [turn.copy() for turn in history]

    def clear_session(self, session_id: str) -> None:
        with self._lock:
            self._history.pop(session_id, None)


SESSION_STORE = SessionStore()
