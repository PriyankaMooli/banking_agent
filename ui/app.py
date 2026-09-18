"""Chat UI skeleton for the banking agent, backed by a dummy gateway API."""

import sys
from pathlib import Path

import chainlit as cl

# Make sibling packages (gateway, identity) importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gateway.api import get_response
import identity.auth  # noqa: F401 - registers the Keycloak oauth_callback


@cl.on_chat_start
async def start():
    user = cl.user_session.get("user")
    name = user.display_name or user.identifier if user else "there"
    cl.user_session.set("history", [])
    await cl.Message(
        content=f"Hi {name}! I'm your banking assistant. How can I help today?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    reply = get_response(message.content, history)

    history.append({"role": "assistant", "content": reply})
    await cl.Message(content=reply).send()
