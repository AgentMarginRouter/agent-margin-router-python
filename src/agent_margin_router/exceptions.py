"""Exception hierarchy for the Agent Margin Router SDK."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class AgentMarginRouterError(Exception):
    """Base class for all SDK errors."""


class APIError(AgentMarginRouterError):
    """Raised when the API returns a non-success status that is not handled
    by a more specific exception.
    """

    def __init__(self, message: str, status_code: int, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class PaymentRequiredError(AgentMarginRouterError):
    """Raised on HTTP 402 when the free tier is exhausted and no valid payment
    was supplied.

    The ``accepts`` attribute contains the payment requirements returned by the
    server (asset, network, amount, pay-to address, facilitator). Use it to
    settle payment out-of-band and retry with an ``X-PAYMENT`` header, or top up
    an API key.
    """

    def __init__(
        self,
        message: str,
        accepts: Optional[List[Dict[str, Any]]] = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.accepts = accepts or []
        self.body = body

    def __str__(self) -> str:
        base = super().__str__()
        if not self.accepts:
            return base
        first = self.accepts[0]
        detail = (
            f" (pay {first.get('priceUsd')} USD in {first.get('assetSymbol', 'USDC')} "
            f"on {first.get('network')} to {first.get('payTo')})"
        )
        return base + detail


class RateLimitError(AgentMarginRouterError):
    """Raised on HTTP 429 when the per-IP or per-wallet request rate is exceeded."""

    def __init__(self, message: str, retry_after: Optional[float] = None, body: Any = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after
        self.body = body


class AuthenticationError(AgentMarginRouterError):
    """Raised on HTTP 401/403 for an invalid or unauthorized API key."""

    def __init__(self, message: str, status_code: int, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body
