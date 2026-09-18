"""Keycloak SSO login for the banking assistant.

Chainlit's built-in Keycloak OAuth provider handles the actual
authorization-code flow (configured entirely via the OAUTH_KEYCLOAK_*
env vars in .env — see identity/keycloak/README.md). This module only
decides which Keycloak users are allowed in and what to call them.
"""

from typing import Optional

import chainlit as cl


@cl.oauth_callback
async def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: dict,
    default_app_user: cl.User,
    id_token: Optional[str] = None,
) -> Optional[cl.User]:
    if provider_id != "keycloak":
        return None

    default_app_user.display_name = raw_user_data.get(
        "preferred_username", default_app_user.identifier
    )
    # Dummy role assignment — swap for real Keycloak realm roles/scopes later.
    default_app_user.metadata["role"] = "customer"
    return default_app_user
