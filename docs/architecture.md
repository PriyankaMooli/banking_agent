# Architecture

Skeleton layout for the banking agent, organized by responsibility:

- **ui/** — Chainlit chat frontend (`app.py`). Renders the conversation,
  reads the logged-in user from the session, and calls into the gateway.
- **gateway/** — The single entry point into the backend.
  - `api.py` — forwards a request to the backend. This is what the UI calls.
  - `backend.py` — dummy business logic (canned responses). Swap for real
    HTTP calls to backend services (accounts, transfers, transactions) later.
- **identity/** — Authentication:
  - `auth.py` — *authentication* ("who is this user"). A Chainlit
    `@cl.oauth_callback` backed by Keycloak SSO (see
    [identity/keycloak/README.md](../identity/keycloak/README.md)).
- **docs/** — Project documentation.

## Request flow

```
ui/app.py --on login-->     identity/auth.oauth_callback(...)         (authenticates via Keycloak)
ui/app.py --per message-->  gateway/api.get_response(message, history)
                                 |
                                 v
                             gateway/backend.answer(message, history)
```

Everything below the UI is still in-process function calls, not real
network services. When a real backend exists, only `gateway/backend.py`'s
internals change (e.g., an HTTP call instead of a canned string) — the
UI's call into the gateway stays the same.
