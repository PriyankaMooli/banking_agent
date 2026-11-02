# Prompt Changelog

Prompts are maintained in `agent/prompts.py`. Every prompt must have an explicit
version and a concise change note. Keep this file updated whenever prompt text
or intended behavior changes.

## Versioning policy

- **PATCH**: wording or formatting clarification with no intended behavior change.
- **MINOR**: behavior change within the prompt's existing role or scope.
- **MAJOR**: role, safety policy, data-use rules, or scope changes incompatibly.

Review prompt changes like code changes: describe the behavior impact and run
relevant routing, privacy, and agent tests. Do not reuse a version number after
changing prompt text.

## 1.0.0 - 2026-10-05

- `banking_response`: Initial local response prompt; requires verified results
  for account-specific claims.
- `intent_classifier`: Initial routing classifier prompt.
- `accounts_specialist`: Initial account-balance specialist prompt.
- `service_specialist`: Initial checkbook, address, and credit-limit prompt.
- `transactions_specialist`: Initial transaction specialist prompt.
- `complex_reasoning`: Initial third-party prompt for complex banking analysis.
