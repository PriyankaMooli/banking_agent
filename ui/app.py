"""Chat UI skeleton for the banking agent, backed by a dummy gateway API."""

import sys
from pathlib import Path

import chainlit as cl
from dotenv import load_dotenv

# Make sibling packages (gateway, identity) importable regardless of cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from gateway.api import get_response
import identity.auth  # noqa: F401 - registers the Keycloak oauth_callback
from session_store import SESSION_STORE


@cl.on_chat_start
async def start():
    user = cl.user_session.get("user")
    name = user.display_name or user.identifier if user else "there"
    session_id = user.identifier if user else "anonymous"
    cl.user_session.set("history", SESSION_STORE.get_history(session_id))
    await cl.Message(
        content=f"Hi {name}! I'm your banking assistant. How can I help today?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    user = cl.user_session.get("user")
    if user is None:
        await cl.Message(content="Please sign in before using banking tools.").send()
        return

    session_id = user.identifier
    SESSION_STORE.append_turn(session_id, "user", message.content)
    history = SESSION_STORE.get_history(session_id)

    principal = {
        "subject": user.identifier,
        "tier": user.metadata.get("tier", "customer"),
    }
    reply = get_response(message.content, history, principal)

    SESSION_STORE.append_turn(session_id, "assistant", reply)
    cl.user_session.set("history", SESSION_STORE.get_history(session_id))
    await cl.Message(content=reply).send()
