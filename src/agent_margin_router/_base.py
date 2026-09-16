"""HTTP transport, authentication and error handling shared by the clients."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
)

if TYPE_CHECKING:  # pragma: no cover
    from .autopay import AutoPay

DEFAULT_BASE_URL = "https://agent-margin-router-production.up.railway.app"
_WALLET_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


class BaseClient:
    """Shared configuration and request logic.

    Authentication (pick one):
      * ``api_key`` – sent as the ``X-API-KEY`` header. Ties usage and billing to
        the wallet that owns the key.
      * ``wallet`` – a ``0x...`` address sent as the ``X-WALLET`` header. Grants
        the free tier (3 calls per wallet) with no signup.
      * neither – anonymous, subject to a stricter per-IP limit.

    On HTTP 402 (free tier exhausted, no payment) the behavior depends on
    ``auto_pay``:

      * ``auto_pay`` unset (default) – a :class:`PaymentRequiredError` is raised
        carrying the server's payment requirements, exactly as in v0.1.
      * ``auto_pay`` set to an :class:`~agent_margin_router.AutoPay` – the SDK
        signs an EIP-3009 USDC authorization with the caller's own wallet and
        transparently retries the request with an ``X-PAYMENT`` header, settling
        the call on-chain. See :class:`~agent_margin_router.AutoPay`.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        wallet: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 2,
        extra_headers: Optional[Dict[str, str]] = None,
        auto_pay: Optional["AutoPay"] = None,
    ) -> None:
        if wallet is not None and not _WALLET_RE.match(wallet):
            raise ValueError(
                f"wallet must be a 0x-prefixed 40-hex-character address, got {wallet!r}"
            )
        self.api_key = api_key
        self.wallet = wallet
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.auto_pay = auto_pay
        self._extra_headers = dict(extra_headers or {})
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"User-Agent": self._user_agent()},
        )

    # -- lifecycle -----------------------------------------------------------
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BaseClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- internals -----------------------------------------------------------
    @staticmethod
    def _user_agent() -> str:
        from . import __version__

        return f"agent-margin-router-python/{__version__}"

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        elif self.wallet:
            headers["X-WALLET"] = self.wallet
        headers.update(self._extra_headers)
        return headers

    def _request(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        url = "/" + path.lstrip("/")
        resp = self._post_with_retries(url, body, self._headers())

        # Automatic on-chain settlement: on 402, if an AutoPay signer is
        # configured, sign an EIP-3009 authorization and retry once with the
        # X-PAYMENT header. Any failure to prepare payment (e.g. over the spend
        # cap) falls through to the normal PaymentRequiredError below.
        if resp.status_code == 402 and self.auto_pay is not None:
            pay_headers = self._prepare_payment_headers(resp)
            if pay_headers is not None:
                headers = {**self._headers(), **pay_headers}
                resp = self._post_with_retries(url, body, headers)

        return self._handle_response(resp)

    def _post_with_retries(
        self, url: str, body: Dict[str, Any], headers: Dict[str, str]
    ) -> httpx.Response:
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                return self._client.post(url, json=body, headers=headers)
            except httpx.HTTPError as exc:  # network/timeout
                last_exc = exc
                if attempt < self.max_retries:
                    continue
                raise APIError(f"request to {url} failed: {exc}", status_code=0) from exc
        # unreachable, but keeps type checkers happy
        raise APIError(f"request to {url} failed: {last_exc}", status_code=0)

    def _prepare_payment_headers(self, resp: httpx.Response) -> Optional[Dict[str, str]]:
        """Build the ``X-PAYMENT`` headers for a 402 response, or ``None``.

        Returns ``None`` (so the caller sees the normal ``PaymentRequiredError``)
        when the body has no usable requirements or the AutoPay helper declines
        (e.g. the price exceeds its spend cap).
        """
        assert self.auto_pay is not None
        try:
            body = resp.json()
        except Exception:
            return None
        accepts: Optional[List[Dict[str, Any]]] = (
            body.get("accepts") if isinstance(body, dict) else None
        )
        if not accepts:
            return None
        from .autopay import AutoPayError

        try:
            header_value = self.auto_pay.build_payment_header(accepts)
        except AutoPayError:
            return None
        return {"X-PAYMENT": header_value, "X-PAYMENT-TOKEN": self.auto_pay.token_hint()}

    def _handle_response(self, resp: httpx.Response) -> Dict[str, Any]:
        code = resp.status_code
        if 200 <= code < 300:
            if not resp.content:
                return {}
            return resp.json()

        body: Any
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        message = _extract_message(body) or f"HTTP {code}"

        if code == 402:
            accepts = body.get("accepts") if isinstance(body, dict) else None
            raise PaymentRequiredError(message, accepts=accepts, body=body)
        if code == 429:
            retry_after = _parse_retry_after(resp.headers.get("Retry-After"))
            raise RateLimitError(message, retry_after=retry_after, body=body)
        if code in (401, 403):
            raise AuthenticationError(message, status_code=code, body=body)
        raise APIError(message, status_code=code, body=body)


def _extract_message(body: Any) -> Optional[str]:
    if isinstance(body, dict):
        for key in ("error", "message", "detail"):
            val = body.get(key)
            if isinstance(val, str) and val:
                return val
            if isinstance(val, dict):
                msg = val.get("message")
                if isinstance(msg, str) and msg:
                    return msg
    if isinstance(body, str) and body:
        return body[:300]
    return None


def _parse_retry_after(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
