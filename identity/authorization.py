"""Request-scoped principal and tool authorization policy."""

from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Iterator


TOOL_ALLOWED_TIERS = {
    "get_account_balance": frozenset({"customer", "privileged"}),
    "get_account_transactions": frozenset({"customer", "privileged"}),
    "get_checkbook": frozenset({"customer", "privileged"}),
    "get_customer_address": frozenset({"customer", "privileged"}),
    "get_customer_credit_limit": frozenset({"customer", "privileged"}),
    "get_card_status": frozenset({"customer", "privileged"}),
    "get_loan_status": frozenset({"customer", "privileged"}),
    "raise_customer_credit_limit": frozenset({"privileged"}),
}

_current_principal: ContextVar[dict[str, str] | None] = ContextVar(
    "current_principal", default=None
)


@contextmanager
def use_principal(principal: dict[str, str]) -> Iterator[None]:
    token: Token = _current_principal.set(principal)
    try:
        yield
    finally:
        _current_principal.reset(token)


def authorize_tool(tool_name: str) -> None:
    principal = _current_principal.get()
    allowed_tiers = TOOL_ALLOWED_TIERS.get(tool_name)
    if principal is None or allowed_tiers is None or principal.get("tier") not in allowed_tiers:
        raise PermissionError(f"Not authorized to execute tool {tool_name!r}")
