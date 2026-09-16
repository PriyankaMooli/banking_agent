"""Mock banking tools the agent can call. Swap for real account-service calls later."""

_ACCOUNTS = {
    "checking": 4231.87,
    "savings": 12890.00,
}

_TRANSACTIONS = [
    {"date": "2026-09-12", "merchant": "Whole Foods", "amount": -52.40},
    {"date": "2026-09-10", "merchant": "Payroll Deposit", "amount": 3200.00},
    {"date": "2026-09-08", "merchant": "Shell Gas Station", "amount": -41.15},
]


def get_balance(account: str = "checking") -> dict:
    """Get the current balance of a customer's bank account.

    Args:
        account: Which account to check — "checking" or "savings".
    """
    balance = _ACCOUNTS.get(account.lower())
    if balance is None:
        return {"error": f"No account named '{account}'. Known accounts: {list(_ACCOUNTS)}"}
    return {"account": account, "balance": balance}


def get_recent_transactions(count: int = 3) -> dict:
    """Get the customer's most recent transactions, newest first.

    Args:
        count: How many recent transactions to return.
    """
    return {"transactions": _TRANSACTIONS[:count]}


def get_card_status() -> dict:
    """Get the status of the customer's debit/credit card."""
    return {"card_last4": "4471", "status": "active"}


def get_loan_status() -> dict:
    """Get the customer's active loans, if any."""
    return {"active_loans": []}
