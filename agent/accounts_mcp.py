"""Accounts MCP server exposing the balance API."""

from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from agent.tools import get_balance

AccountName = Literal["checking", "savings"]


class BalanceRequest(BaseModel):
    """Validated input for a balance lookup."""

    account: AccountName = Field(default="checking")


class BalanceData(BaseModel):
    """Successful balance payload."""

    account: AccountName
    balance: float


class BalanceError(BaseModel):
    """Stable error payload returned by the MCP tool."""

    code: Literal["INVALID_ACCOUNT", "ACCOUNT_SERVICE_ERROR"]
    message: str


class BalanceResponse(BaseModel):
    """Result envelope for the balance API."""

    ok: bool
    data: BalanceData | None = None
    error: BalanceError | None = None


mcp = FastMCP("accounts")


@mcp.tool()
def get_account_balance(account: AccountName = "checking") -> BalanceResponse:
    """Return the current balance for a checking or savings account."""
    request = BalanceRequest(account=account)
    try:
        result = get_balance(request.account)
    except Exception:
        return BalanceResponse(
            ok=False,
            error=BalanceError(
                code="ACCOUNT_SERVICE_ERROR",
                message="The account balance service is unavailable.",
            ),
        )

    if "error" in result:
        return BalanceResponse(
            ok=False,
            error=BalanceError(code="INVALID_ACCOUNT", message=str(result["error"])),
        )

    try:
        data = BalanceData(
            account=request.account,
            balance=float(result["balance"]),
        )
    except (KeyError, TypeError, ValueError):
        return BalanceResponse(
            ok=False,
            error=BalanceError(
                code="ACCOUNT_SERVICE_ERROR",
                message="The account balance response was invalid.",
            ),
        )
    return BalanceResponse(ok=True, data=data)


if __name__ == "__main__":
    mcp.run()