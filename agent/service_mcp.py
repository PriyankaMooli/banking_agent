"""Service MCP server exposing checkbook, address, and credit-limit APIs."""

from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

from agent.tools import (
    get_address as get_address_api,
    get_checkbook_info as get_checkbook_api,
    get_credit_limit as get_credit_limit_api,
)


class ServiceError(BaseModel):
    """Stable error payload returned by service tools."""

    code: Literal["SERVICE_ERROR"]
    message: str


class CheckbookData(BaseModel):
    """Successful checkbook payload."""

    checkbook_available: bool
    checks_remaining: int


class CheckbookResponse(BaseModel):
    """Result envelope for the checkbook API."""

    ok: bool
    data: CheckbookData | None = None
    error: ServiceError | None = None


class AddressData(BaseModel):
    """Successful mailing-address payload."""

    address: str


class AddressResponse(BaseModel):
    """Result envelope for the address API."""

    ok: bool
    data: AddressData | None = None
    error: ServiceError | None = None


class CreditLimitData(BaseModel):
    """Successful credit-limit payload."""

    credit_limit: float
    available_credit: float


class CreditLimitResponse(BaseModel):
    """Result envelope for the credit-limit API."""

    ok: bool
    data: CreditLimitData | None = None
    error: ServiceError | None = None


mcp = FastMCP("service")


def _service_error(message: str) -> ServiceError:
    return ServiceError(code="SERVICE_ERROR", message=message)


@mcp.tool()
def get_checkbook() -> CheckbookResponse:
    """Return verified checkbook ordering information."""
    try:
        data = CheckbookData.model_validate(get_checkbook_api())
    except (TypeError, ValueError, ValidationError):
        return CheckbookResponse(
            ok=False,
            error=_service_error("The checkbook service response was invalid."),
        )
    except Exception:
        return CheckbookResponse(
            ok=False,
            error=_service_error("The checkbook service is unavailable."),
        )
    return CheckbookResponse(ok=True, data=data)


@mcp.tool()
def get_customer_address() -> AddressResponse:
    """Return the verified mailing address on file."""
    try:
        data = AddressData.model_validate(get_address_api())
    except (TypeError, ValueError, ValidationError):
        return AddressResponse(
            ok=False,
            error=_service_error("The address service response was invalid."),
        )
    except Exception:
        return AddressResponse(
            ok=False,
            error=_service_error("The address service is unavailable."),
        )
    return AddressResponse(ok=True, data=data)


@mcp.tool()
def get_customer_credit_limit() -> CreditLimitResponse:
    """Return the verified credit limit and available credit."""
    try:
        data = CreditLimitData.model_validate(get_credit_limit_api())
    except (TypeError, ValueError, ValidationError):
        return CreditLimitResponse(
            ok=False,
            error=_service_error("The credit-limit service response was invalid."),
        )
    except Exception:
        return CreditLimitResponse(
            ok=False,
            error=_service_error("The credit-limit service is unavailable."),
        )
    return CreditLimitResponse(ok=True, data=data)


if __name__ == "__main__":
    mcp.run()