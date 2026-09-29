# Architecture

Skeleton layout for the banking agent, organized by responsibility:

- **ui/** — Chainlit chat frontend (`app.py`). Renders the conversation,
  reads the logged-in user from the session, and calls into the gateway.
- **gateway/** — The single entry point the UI calls into.
  - `api.py` — forwards a request to `gateway/backend.py`. This is what the UI calls.
  - `backend.py` — HTTP client for the backend API (`POST /chat`). Only
    module that knows the backend is a separate network service.
- **backend/** — Standalone FastAPI service. Receives chat requests over
  HTTP and calls the agent layer.
  - `main.py` — FastAPI app, `POST /chat` endpoint, `GET /health`.
  - `schemas.py` — request/response models.
- **agent/** — The agent layer: plans requests with LangGraph, runs the
  relevant banking specialists in order, and uses Gemini to compose the reply.
  - `agent.py` — `BankingAgent`, backed by the Gemini API (`google-genai`).
  - `coordinator.py` — `CoordinatorAgent`, backed by LangGraph, which routes
    single- and multi-intent requests through the specialist tools.
  - `tools.py` — mock account/transaction/card/loan data, exposed as tools.
    Swap the function bodies for real account-service calls later.
- **identity/** — Authentication:
  - `auth.py` — *authentication* ("who is this user"). A Chainlit
    `@cl.oauth_callback` backed by Keycloak SSO (see
    [identity/keycloak/README.md](../identity/keycloak/README.md)).
- **docs/** — Project documentation.

## Request flow

```
ui/app.py --on login-->     identity/auth.oauth_callback(...)           (authenticates via Keycloak)
ui/app.py --per message-->  gateway/api.get_response(message, history)
                                 |
                                 v
                             gateway/backend.answer(message, history)    (HTTP POST /chat)
                                 |
                                 v
                             backend/main.chat(request)                  (separate FastAPI process, :8001)
                                 |
                                 v
                             agent/coordinator.CoordinatorAgent.run(message, history)
                                 |
                                 v
                           LangGraph coordinator
                            /          \
                             v            v
                         specialist tools   BankingAgent
                                    |
                                    v
                                  Gemini API
```

`gateway/backend.py` is the one seam between the UI process and the
backend process — it's the only module that knows the backend lives over
HTTP. `agent/tools.py` is the seam between the agent and real account
data — swap its function bodies for real service calls without touching
the agent's tool-use loop or `backend/main.py`.
