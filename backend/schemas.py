"""Request/response schemas for the backend chat API."""

from typing import Literal

from pydantic import BaseModel


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[Turn] = []


class ChatResponse(BaseModel):
    reply: str
