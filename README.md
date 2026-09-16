# banking_agent

Chat UI skeleton for a banking assistant. See [docs/architecture.md](docs/architecture.md) for the folder layout.

## Run

```
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY and the OAUTH_KEYCLOAK_* values

uvicorn backend.main:app --port 8001   # backend API + agent layer
chainlit run ui/app.py                 # chat UI (separate terminal)
```
