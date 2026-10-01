"""Backend API — receives chat requests (from gateway/backend.py) and calls
the agent layer (agent/agent.py).

Run with: uvicorn backend.main:app --port 8001
"""

from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from fastapi import FastAPI, Header, HTTPException

from agent.coordinator import CoordinatorAgent
from backend.schemas import ChatRequest, ChatResponse
from identity.authorization import use_principal
from identity.principal import verify_principal

app = FastAPI(title="Banking Agent Backend")
agent = CoordinatorAgent()


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authenticated_principal: str | None = Header(default=None, alias="X-Authenticated-Principal"),
) -> ChatResponse:
    if authenticated_principal is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        principal = verify_principal(authenticated_principal)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication") from exc
    history = [turn.model_dump() for turn in request.history]
    with use_principal(principal):
        reply = agent.run(request.message, history, principal)
    return ChatResponse(reply=reply)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
