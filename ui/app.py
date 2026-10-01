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
    user = cl.user_session.get("user")
    if user is None:
        await cl.Message(content="Please sign in before using banking tools.").send()
        return

    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    principal = {
        "subject": user.identifier,
        "tier": user.metadata.get("tier", "customer"),
    }
    reply = get_response(message.content, history, principal)

    history.append({"role": "assistant", "content": reply})
    await cl.Message(content=reply).send()
