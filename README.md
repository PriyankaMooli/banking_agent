# banking_agent

Chat UI skeleton for a banking assistant. See [docs/architecture.md](docs/architecture.md) for the folder layout.

## Run

```
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY and the OAUTH_KEYCLOAK_* values

uvicorn backend.main:app --port 8001   # backend API + agent layer
chainlit run ui/app.py                 # chat UI (separate terminal)
```

The coordinator uses the Gemini-based intent classifier to route flexible user
wording to the appropriate specialist. If the classifier is unavailable, it
falls back to the coordinator's keyword routes.

The Accounts MCP server exposes the typed `get_account_balance` tool over
stdio. Chainlit starts it automatically when MCP is enabled in
`.chainlit/config.toml`; it can also be run directly with:

```
python -m agent.accounts_mcp
```

The Transactions MCP server exposes the typed `get_account_transactions` tool:

```
python -m agent.transactions_mcp
```

The Service MCP server exposes typed checkbook, address, and credit-limit tools:

```
python -m agent.service_mcp
```
