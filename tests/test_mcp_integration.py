"""Integration tests for the banking MCP servers.

These exercise the real stdio MCP client/server round trip through
agent/mcp_bridge.py — no mocking of the bridge or the MCP layer. The
servers are currently backed by the mock data in agent/tools.py; once
agent/tools.py is replaced with real bank API calls, these same tests
should keep passing unchanged against the live APIs.

Covers: balance, transactions, checkbook, address, credit-limit.
Statement is intentionally out of scope — no statement tool/server exists yet.
"""

import pytest

from agent.mcp_bridge import call_mcp_tool
from identity.authorization import use_principal


@pytest.fixture(autouse=True)
def authenticated_customer():
    with use_principal({"subject": "test-customer", "tier": "customer"}):
        yield


# --- Balance ---------------------------------------------------------------


@pytest.mark.parametrize("account", ["checking", "savings"])
def test_get_account_balance_known_account(account):
    result = call_mcp_tool("agent.accounts_mcp", "get_account_balance", {"account": account})

    assert result["ok"] is True
    assert result["error"] is None
    assert result["data"]["account"] == account
    assert isinstance(result["data"]["balance"], float)


def test_get_account_balance_invalid_account_errors():
    with pytest.raises(RuntimeError):
        call_mcp_tool("agent.accounts_mcp", "get_account_balance", {"account": "bogus"})


# --- Transactions ------------------------------------------------------------


def test_get_account_transactions_default_count():
    result = call_mcp_tool("agent.transactions_mcp", "get_account_transactions", {"count": 3})

    assert result["ok"] is True
    transactions = result["data"]["transactions"]
    assert len(transactions) <= 3
    for txn in transactions:
        assert {"date", "merchant", "amount"} <= txn.keys()


def test_get_account_transactions_custom_count():
    result = call_mcp_tool("agent.transactions_mcp", "get_account_transactions", {"count": 2})

    assert result["ok"] is True
    assert len(result["data"]["transactions"]) == 2


def test_get_account_transactions_invalid_count_returns_error_envelope():
    result = call_mcp_tool("agent.transactions_mcp", "get_account_transactions", {"count": 0})

    assert result["ok"] is False
    assert result["data"] is None
    assert result["error"]["code"] == "INVALID_COUNT"


# --- Checkbook ---------------------------------------------------------------


def test_get_checkbook():
    result = call_mcp_tool("agent.service_mcp", "get_checkbook", {})

    assert result["ok"] is True
    assert isinstance(result["data"]["checkbook_available"], bool)
    assert isinstance(result["data"]["checks_remaining"], int)


# --- Address -----------------------------------------------------------------


def test_get_customer_address():
    result = call_mcp_tool("agent.service_mcp", "get_customer_address", {})

    assert result["ok"] is True
    assert isinstance(result["data"]["address"], str)
    assert result["data"]["address"] != ""


# --- Credit limit --------------------------------------------------------------


def test_get_customer_credit_limit():
    result = call_mcp_tool("agent.service_mcp", "get_customer_credit_limit", {})

    assert result["ok"] is True
    assert result["data"]["credit_limit"] >= 0
    assert result["data"]["available_credit"] <= result["data"]["credit_limit"]
