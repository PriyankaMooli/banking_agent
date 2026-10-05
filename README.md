# banking_agent

Chat UI skeleton for a banking assistant. See [docs/architecture.md](docs/architecture.md) for the folder layout.

## Run

```
pip install -r requirements.txt
cp .env.example .env   # fill in GEMINI_API_KEY, Keycloak values, and secrets

uvicorn backend.main:app --port 8001   # backend API + agent layer
chainlit run ui/app.py                 # chat UI (separate terminal)
```

Set `CHAINLIT_AUTH_SECRET` with `chainlit create-secret` and set
`AUTHZ_SHARED_SECRET` to a random value (for example, `openssl rand -hex 32`).
The UI and backend must load the same `AUTHZ_SHARED_SECRET`; keep it server-side.

Tools are checked against a deny-by-default tier policy before execution.
Users default to `customer`; Keycloak must expose either a `tier: privileged`
user-info claim or the `privileged` / `banking-privileged` role in user-info
data to grant elevated access. The `raise_customer_credit_limit` policy is
privileged-only, but the mutation tool has not been implemented yet.

The coordinator uses the Gemini-based intent classifier to route flexible user
wording to the appropriate specialist. If the classifier is unavailable, it
falls back to the coordinator's keyword routes.

For in-boundary local reasoning, set `USE_SELF_HOSTED_LLM=true` with a local
OpenAI-compatible endpoint such as Ollama (`SELF_HOSTED_LLM_BASE_URL=http://localhost:11434/v1`)
and a matching model name like `llama3.1:8b`. When enabled, the general
banking reasoning path uses the self-hosted model as its primary backend and
keeps Gemini as the fallback for other specialist flows unless a local model is
configured for those as well.

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
