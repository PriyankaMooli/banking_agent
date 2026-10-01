"""Authorization checks at banking tool execution boundaries."""

import pytest

from agent.mcp_bridge import call_mcp_tool
from agent.tools import get_card_status
from identity.authorization import authorize_tool, use_principal
from identity.principal import sign_principal, verify_principal


def test_customer_cannot_raise_credit_limit():
    with use_principal({"subject": "customer-1", "tier": "customer"}):
        with pytest.raises(PermissionError):
            authorize_tool("raise_customer_credit_limit")


def test_privileged_user_can_raise_credit_limit():
    with use_principal({"subject": "staff-1", "tier": "privileged"}):
        authorize_tool("raise_customer_credit_limit")


def test_tool_execution_requires_principal():
    with pytest.raises(PermissionError):
        call_mcp_tool("agent.accounts_mcp", "get_account_balance", {"account": "checking"})


def test_direct_tool_execution_is_authorized():
    with pytest.raises(PermissionError):
        get_card_status()
    with use_principal({"subject": "customer-1", "tier": "customer"}):
        assert get_card_status()["status"] == "active"


def test_unknown_tools_are_denied():
    with use_principal({"subject": "staff-1", "tier": "privileged"}):
        with pytest.raises(PermissionError):
            authorize_tool("unregistered_tool")


def test_signed_principal_round_trip_and_tampering(monkeypatch):
    monkeypatch.setenv("AUTHZ_SHARED_SECRET", "test-shared-secret")
    token = sign_principal("staff-1", "privileged")

    assert verify_principal(token) == {"subject": "staff-1", "tier": "privileged"}
    with pytest.raises(ValueError):
        verify_principal(token[:-1] + ("A" if token[-1] != "A" else "B"))