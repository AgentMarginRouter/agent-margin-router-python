"""Offline unit tests for the optional AutoPay (x402 auto-settlement) helper.

These never touch the network. They cover: config/validation, requirement
selection, the spend cap, EIP-3009 header construction (decoded and verified by
recovering the signer), and the client's 402 -> auto-retry integration via an
httpx MockTransport.

They require ``eth-account`` (the ``autopay`` extra). Tests that need it are
skipped automatically when it is not installed.
"""
import base64
import json

import httpx
import pytest

from agent_margin_router import AutoPay, AutoPayError, Client

try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data

    _HAS_ETH_ACCOUNT = True
except ImportError:  # pragma: no cover
    _HAS_ETH_ACCOUNT = False

requires_eth = pytest.mark.skipif(
    not _HAS_ETH_ACCOUNT, reason="eth-account not installed (autopay extra)"
)

# A throwaway key generated once for the whole module. Never a real wallet.
if _HAS_ETH_ACCOUNT:
    _ACCT = Account.create()
    _TEST_KEY = _ACCT.key.hex()
    _TEST_ADDR = _ACCT.address
else:  # pragma: no cover
    _TEST_KEY = "0x" + "1" * 64
    _TEST_ADDR = "0x" + "a" * 40

USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDT = "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2"
PAY_TO = "0xf7a181bbe5d29924e800df4ba93418ef94f4e7c2"


def _requirement(symbol="USDC", asset=USDC, price=0.02, amount="20000",
                 name="USD Coin", version="2"):
    return {
        "scheme": "exact",
        "network": "base",
        "asset": asset,
        "assetSymbol": symbol,
        "maxAmountRequired": amount,
        "priceUsd": price,
        "payTo": PAY_TO,
        "resource": "/token-price",
        "description": "token price",
        "mimeType": "application/json",
        "maxTimeoutSeconds": 300,
        "extra": {"name": name, "version": version, "chainId": 8453, "decimals": 6},
    }


# -- construction / validation ----------------------------------------------
def test_requires_some_credential():
    with pytest.raises(ValueError):
        AutoPay()  # no key, no env var, no signer


def test_signer_without_address_rejected():
    with pytest.raises(ValueError):
        AutoPay(signer=lambda td: "0x" + "0" * 130)


def test_reads_key_from_env(monkeypatch):
    if not _HAS_ETH_ACCOUNT:
        pytest.skip("eth-account not installed")
    monkeypatch.setenv("AGENT_MARGIN_ROUTER_PRIVATE_KEY", _TEST_KEY)
    ap = AutoPay()
    assert ap.account_address == _TEST_ADDR


# -- requirement selection ---------------------------------------------------
@requires_eth
def test_prefers_usdc_over_usdt():
    ap = AutoPay(private_key=_TEST_KEY)  # default prefer USDC
    header = ap.build_payment_header([_requirement("USDT", USDT, name="Tether USD",
                                                   version="1"), _requirement("USDC")])
    payload = json.loads(base64.b64decode(header))
    assert payload["payload"]["asset"] == USDC


@requires_eth
def test_prefer_symbol_override():
    ap = AutoPay(private_key=_TEST_KEY, prefer_symbol="USDT")
    header = ap.build_payment_header([_requirement("USDC"),
                                      _requirement("USDT", USDT, name="Tether USD",
                                                   version="1")])
    payload = json.loads(base64.b64decode(header))
    assert payload["payload"]["asset"] == USDT


def test_no_exact_requirement_raises():
    ap = AutoPay(private_key=_TEST_KEY) if _HAS_ETH_ACCOUNT else AutoPay(
        signer=lambda td: "0x0", account_address=_TEST_ADDR)
    with pytest.raises(AutoPayError):
        ap.build_payment_header([{"scheme": "upto", "assetSymbol": "USDC"}])


# -- spend cap ---------------------------------------------------------------
def test_spend_cap_blocks_expensive_call():
    ap = AutoPay(signer=lambda td: "0x" + "0" * 130, account_address=_TEST_ADDR,
                 max_price_usd=0.01)
    with pytest.raises(AutoPayError):
        ap.build_payment_header([_requirement(price=0.05)])


def test_spend_cap_allows_cheap_call():
    if not _HAS_ETH_ACCOUNT:
        pytest.skip("eth-account not installed")
    ap = AutoPay(private_key=_TEST_KEY, max_price_usd=0.10)
    header = ap.build_payment_header([_requirement(price=0.02)])
    assert isinstance(header, str) and len(header) > 0


# -- EIP-3009 header correctness --------------------------------------------
@requires_eth
def test_header_fields_and_signature_recover():
    ap = AutoPay(private_key=_TEST_KEY)
    header = ap.build_payment_header([_requirement()])
    payload = json.loads(base64.b64decode(header))

    assert payload["x402Version"] == 1
    assert payload["scheme"] == "exact"
    assert payload["network"] == "base"
    auth = payload["payload"]["authorization"]
    assert auth["from"] == _TEST_ADDR
    assert auth["to"] == PAY_TO
    assert auth["value"] == "20000"
    assert auth["validAfter"] == "0"
    assert int(auth["validBefore"]) > 0
    assert auth["nonce"].startswith("0x") and len(auth["nonce"]) == 66
    assert payload["payload"]["asset"] == USDC

    # Reconstruct the typed data and recover the signer -> must be our address.
    typed = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "domain": {"name": "USD Coin", "version": "2", "chainId": 8453,
                   "verifyingContract": USDC},
        "primaryType": "TransferWithAuthorization",
        "message": {
            "from": _TEST_ADDR,
            "to": PAY_TO,
            "value": 20000,
            "validAfter": 0,
            "validBefore": int(auth["validBefore"]),
            "nonce": bytes.fromhex(auth["nonce"][2:]),
        },
    }
    signable = encode_typed_data(full_message=typed)
    recovered = Account.recover_message(signable, signature=payload["payload"]["signature"])
    assert recovered == _TEST_ADDR


# -- client integration: 402 -> auto retry ----------------------------------
def _mock(client, handler):
    client._client.close()
    client._client = httpx.Client(base_url=client.base_url,
                                  transport=httpx.MockTransport(handler))
    return client


@requires_eth
def test_client_auto_settles_on_402():
    calls = {"n": 0, "payment_header": None}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(402, json={"error": "payment required",
                                             "accepts": [_requirement()]})
        calls["payment_header"] = request.headers.get("x-payment")
        return httpx.Response(200, json={"data": {"price": 1234.5}})

    client = _mock(Client(auto_pay=AutoPay(private_key=_TEST_KEY, max_price_usd=1.0)),
                   handler)
    out = client.token_price(asset="ETH")
    assert out["data"]["price"] == 1234.5
    assert calls["n"] == 2
    assert calls["payment_header"]  # X-PAYMENT header was replayed
    # decodes to a valid authorization
    payload = json.loads(base64.b64decode(calls["payment_header"]))
    assert payload["payload"]["authorization"]["to"] == PAY_TO
    client.close()


@requires_eth
def test_client_raises_402_when_over_cap():
    def handler(request):
        return httpx.Response(402, json={"error": "payment required",
                                         "accepts": [_requirement(price=5.0)]})

    from agent_margin_router import PaymentRequiredError

    client = _mock(Client(auto_pay=AutoPay(private_key=_TEST_KEY, max_price_usd=0.10)),
                   handler)
    with pytest.raises(PaymentRequiredError):
        client.token_price(asset="ETH")
    client.close()


def test_client_without_autopay_still_raises_402():
    def handler(request):
        return httpx.Response(402, json={"error": "payment required",
                                         "accepts": [_requirement()]})

    from agent_margin_router import PaymentRequiredError

    client = _mock(Client(wallet="0x" + "a" * 40), handler)
    with pytest.raises(PaymentRequiredError):
        client.token_price(asset="ETH")
    client.close()
