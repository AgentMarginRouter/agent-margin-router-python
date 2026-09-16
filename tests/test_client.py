"""Offline unit tests for the agent-margin-router client.

These tests use httpx's MockTransport, so they never touch the network and are
safe to run in CI. They cover: wallet validation, auth-header selection, and the
HTTP status -> exception mapping (200, 402, 429, 401).
"""
import json

import httpx
import pytest

from agent_margin_router import (
    Client,
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
)


def _mock(client: Client, handler):
    """Swap the client's underlying httpx.Client for one backed by a mock."""
    client._client.close()
    client._client = httpx.Client(
        base_url=client.base_url,
        transport=httpx.MockTransport(handler),
    )
    return client


def test_wallet_validation_rejects_bad_address():
    with pytest.raises(ValueError):
        Client(wallet="not-a-wallet")


def test_wallet_validation_accepts_good_address():
    c = Client(wallet="0x" + "a" * 40)
    assert c.wallet == "0x" + "a" * 40
    c.close()


def test_api_key_header_takes_precedence():
    # When an API key is set it is used exclusively; the wallet header is omitted.
    c = Client(api_key="secret-key", wallet="0x" + "b" * 40)
    headers = c._headers()
    assert headers["X-API-KEY"] == "secret-key"
    assert "X-WALLET" not in headers
    c.close()


def test_wallet_header_when_no_key():
    c = Client(wallet="0x" + "c" * 40)
    headers = c._headers()
    assert headers["X-WALLET"] == "0x" + "c" * 40
    assert "X-API-KEY" not in headers
    c.close()


def test_successful_response_is_returned_as_dict():
    def handler(request):
        return httpx.Response(200, json={"price": 3125.42, "token": "FREE", "cost_usdc": 0.0})

    c = _mock(Client(wallet="0x" + "d" * 40), handler)
    result = c.token_price(asset="ETH")
    assert result["price"] == 3125.42
    assert result["token"] == "FREE"
    c.close()


def test_402_raises_payment_required_with_accepts():
    accepts = [{"payTo": "0xf7a181bbe5d29924e800df4ba93418ef94f4e7c2",
                "maxAmountRequired": "20000", "network": "base"}]

    def handler(request):
        return httpx.Response(402, json={"accepts": accepts, "error": "payment required"})

    c = _mock(Client(), handler)
    with pytest.raises(PaymentRequiredError) as exc:
        c.contract_info(address="0x0000000000000000000000000000000000000000")
    assert exc.value.accepts[0]["payTo"].endswith("e7c2")
    c.close()


def test_429_raises_rate_limit_with_retry_after():
    def handler(request):
        return httpx.Response(429, headers={"Retry-After": "7"}, json={"error": "slow down"})

    c = _mock(Client(wallet="0x" + "e" * 40), handler)
    with pytest.raises(RateLimitError) as exc:
        c.fear_greed()
    assert exc.value.retry_after == 7.0
    c.close()


def test_401_raises_authentication_error():
    def handler(request):
        return httpx.Response(401, json={"error": "bad key"})

    c = _mock(Client(api_key="nope"), handler)
    with pytest.raises(AuthenticationError):
        c.web_search(query="test")
    c.close()
