"""Transactions MCP server exposing the recent-transactions API."""

from datetime import date
from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ValidationError

from agent.tools import get_recent_transactions


class TransactionsRequest(BaseModel):
    """Validated input for a recent-transactions lookup."""

    count: int = Field(default=3, ge=1, le=50)


class Transaction(BaseModel):
    """A single verified transaction."""

    date: date
    merchant: str
    amount: float


class TransactionsData(BaseModel):
    """Successful recent-transactions payload."""

    transactions: list[Transaction]


class TransactionsError(BaseModel):
    """Stable error payload returned by the MCP tool."""

    code: Literal[
        "INVALID_COUNT",
        "TRANSACTION_SERVICE_ERROR",
    ]
    message: str


class TransactionsResponse(BaseModel):
    """Result envelope for the recent-transactions API."""

    ok: bool
    data: TransactionsData | None = None
    error: TransactionsError | None = None


mcp = FastMCP("transactions")


@mcp.tool()
def get_account_transactions(count: int = 3) -> TransactionsResponse:
    """Return the customer's most recent transactions, newest first."""
    try:
        request = TransactionsRequest(count=count)
    except ValidationError:
        return TransactionsResponse(
            ok=False,
            error=TransactionsError(
                code="INVALID_COUNT",
                message="count must be an integer between 1 and 50.",
            ),
        )

    try:
        result = get_recent_transactions(request.count)
    except Exception:
        return TransactionsResponse(
            ok=False,
            error=TransactionsError(
                code="TRANSACTION_SERVICE_ERROR",
                message="The transaction service is unavailable.",
            ),
        )

    if "error" in result:
        return TransactionsResponse(
            ok=False,
            error=TransactionsError(
                code="TRANSACTION_SERVICE_ERROR",
                message="The transaction service returned an error.",
            ),
        )

    try:
        data = TransactionsData.model_validate(result)
    except (TypeError, ValueError, ValidationError):
        return TransactionsResponse(
            ok=False,
            error=TransactionsError(
                code="TRANSACTION_SERVICE_ERROR",
                message="The transaction service response was invalid.",
            ),
        )
    return TransactionsResponse(ok=True, data=data)


if __name__ == "__main__":
    mcp.run()