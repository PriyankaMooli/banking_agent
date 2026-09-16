"""Backend API — receives chat requests (from gateway/backend.py) and calls
the agent layer (agent/agent.py).

Run with: uvicorn backend.main:app --port 8001
"""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from agent.agent import BankingAgent
from backend.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Banking Agent Backend")
agent = BankingAgent()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    history = [turn.model_dump() for turn in request.history]
    reply = agent.run(request.message, history)
    return ChatResponse(reply=reply)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
