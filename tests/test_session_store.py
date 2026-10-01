"""Session-store behavior for multi-turn conversation context."""

from session_store import SessionStore


def test_session_store_keeps_history_per_user():
    store = SessionStore()

    assert store.get_history("user-1") == []

    store.append_turn("user-1", "user", "hello")
    store.append_turn("user-1", "assistant", "hi there")

    assert store.get_history("user-1") == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi there"},
    ]


def test_session_store_keeps_users_isolated():
    store = SessionStore()

    store.append_turn("user-1", "user", "first")
    store.append_turn("user-2", "user", "second")

    assert store.get_history("user-1") == [{"role": "user", "content": "first"}]
    assert store.get_history("user-2") == [{"role": "user", "content": "second"}]
