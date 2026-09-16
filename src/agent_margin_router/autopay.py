"""Optional automatic on-chain settlement for HTTP 402 (x402) responses.

When the free tier is exhausted the Agent Margin Router answers with HTTP 402 and
a set of *payment requirements* (asset, network, amount, pay-to address). In
v0.1 the SDK simply raised :class:`~agent_margin_router.PaymentRequiredError` and
left settlement to the caller.

This module adds an **opt-in** :class:`AutoPay` helper that, given the caller's
own wallet private key, signs an EIP-3009 ``TransferWithAuthorization`` (the exact
scheme x402 facilitators expect) and returns the base64 ``X-PAYMENT`` header the
client replays to settle the call automatically.

Security model
--------------
* The private key belongs to the **caller** (the paying agent), never to the
  router operator. It is only used locally to sign the transfer authorization and
  is never transmitted anywhere.
* Only an EIP-3009 *authorization* is signed – a gasless, single-use, exact-amount
  transfer to the address the server put in ``payTo``. It cannot be replayed
  (random 32-byte nonce, server-side replay cache) and cannot move more than the
  signed ``value``.
* :attr:`AutoPay.max_price_usd` is a hard client-side spend cap: any 402 that asks
  for more than the cap is re-raised instead of paid.

``eth-account`` is an **optional** dependency. Install it with::

    pip install "agent-margin-router[autopay]"

Usage::

    from agent_margin_router import Client, AutoPay

    client = Client(auto_pay=AutoPay(private_key="0x...", max_price_usd=0.10))
    data = client.token_price(asset="ETH")   # 402s are settled transparently
"""
from __future__ import annotations

import base64
import json
import os
import re
import time
from typing import Any, Callable, Dict, List, Optional

_WALLET_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")

# EIP-3009 typed-data shape (identical across USDC/USDT on Base).
_EIP712_TYPES = {
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
}

# Signature of a custom signer: (typed_data_dict) -> "0x"-prefixed signature hex.
Signer = Callable[[Dict[str, Any]], str]


class AutoPayError(Exception):
    """Raised when an automatic settlement cannot be prepared."""


def _select_requirement(
    accepts: List[Dict[str, Any]], prefer_symbol: Optional[str]
) -> Optional[Dict[str, Any]]:
    """Pick a payment requirement from the server's ``accepts`` list.

    Prefers ``prefer_symbol`` (default USDC), otherwise the first entry. Only the
    ``exact`` scheme is supported – anything else is skipped.
    """
    exact = [r for r in accepts if str(r.get("scheme", "exact")).lower() == "exact"]
    if not exact:
        return None
    if prefer_symbol:
        want = prefer_symbol.strip().upper()
        for r in exact:
            if str(r.get("assetSymbol", "")).upper() == want:
                return r
    return exact[0]


def _price_usd(requirement: Dict[str, Any]) -> Optional[float]:
    val = requirement.get("priceUsd")
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


class AutoPay:
    """Automatic x402 settlement using the caller's own wallet.

    Parameters
    ----------
    private_key:
        The paying wallet's private key (``0x``-prefixed hex). Read from the
        ``AGENT_MARGIN_ROUTER_PRIVATE_KEY`` env var when omitted. Required unless
        a custom ``signer`` is supplied.
    signer:
        Advanced: a callable ``(typed_data) -> signature_hex`` for hardware
        wallets or remote signers. When given, ``private_key`` is only used to
        derive the ``from`` address (or pass ``account_address`` explicitly).
    account_address:
        The ``from`` address to put in the authorization. Derived from
        ``private_key`` when omitted; required when only a ``signer`` is given.
    max_price_usd:
        Hard client-side cap. A 402 asking for more than this is re-raised
        instead of paid. ``None`` (default) means no cap – set one in production.
    prefer_symbol:
        Preferred stablecoin symbol when the server accepts several. Default
        ``"USDC"``.
    """

    def __init__(
        self,
        private_key: Optional[str] = None,
        *,
        signer: Optional[Signer] = None,
        account_address: Optional[str] = None,
        max_price_usd: Optional[float] = None,
        prefer_symbol: str = "USDC",
    ) -> None:
        if private_key is None:
            private_key = os.environ.get("AGENT_MARGIN_ROUTER_PRIVATE_KEY")
        self._private_key = private_key
        self._signer = signer
        self.max_price_usd = max_price_usd
        self.prefer_symbol = prefer_symbol

        if account_address is not None:
            if not _WALLET_RE.match(account_address):
                raise ValueError(f"account_address must be a 0x address, got {account_address!r}")
            self._account_address = account_address
        elif private_key is not None:
            self._account_address = self._derive_address(private_key)
        elif signer is not None:
            raise ValueError(
                "account_address is required when only a custom signer is supplied"
            )
        else:
            raise ValueError(
                "AutoPay needs a private_key (or the AGENT_MARGIN_ROUTER_PRIVATE_KEY "
                "env var), or a custom signer plus account_address"
            )

    # -- public --------------------------------------------------------------
    @property
    def account_address(self) -> str:
        """The paying wallet address (``from`` in the authorization)."""
        return self._account_address

    def build_payment_header(self, accepts: List[Dict[str, Any]]) -> str:
        """Sign an EIP-3009 authorization and return the base64 ``X-PAYMENT`` value.

        Raises :class:`AutoPayError` if no supported requirement is present or the
        amount exceeds :attr:`max_price_usd`.
        """
        requirement = _select_requirement(accepts, self.prefer_symbol)
        if requirement is None:
            raise AutoPayError("no 'exact'-scheme payment requirement in the 402 response")

        price = _price_usd(requirement)
        if self.max_price_usd is not None and price is not None and price > self.max_price_usd:
            raise AutoPayError(
                f"required price ${price} exceeds max_price_usd cap ${self.max_price_usd}"
            )

        pay_to = str(requirement.get("payTo", ""))
        asset = str(requirement.get("asset", ""))
        network = str(requirement.get("network", "base"))
        symbol = str(requirement.get("assetSymbol", "USDC"))
        amount = str(requirement.get("maxAmountRequired", ""))
        if not (_WALLET_RE.match(pay_to) and _WALLET_RE.match(asset) and amount.isdigit()):
            raise AutoPayError(
                "402 requirement is missing a valid payTo/asset/maxAmountRequired"
            )

        extra = requirement.get("extra") or {}
        domain_name = str(extra.get("name", "USD Coin"))
        domain_version = str(extra.get("version", "2"))
        chain_id = int(extra.get("chainId", 8453))
        timeout = int(requirement.get("maxTimeoutSeconds", 300) or 300)

        now = int(time.time())
        valid_after = 0
        valid_before = now + max(timeout, 60)
        nonce_bytes = os.urandom(32)
        nonce_hex = "0x" + nonce_bytes.hex()

        typed_data = {
            "types": _EIP712_TYPES,
            "domain": {
                "name": domain_name,
                "version": domain_version,
                "chainId": chain_id,
                "verifyingContract": asset,
            },
            "primaryType": "TransferWithAuthorization",
            "message": {
                "from": self._account_address,
                "to": pay_to,
                "value": int(amount),
                "validAfter": valid_after,
                "validBefore": valid_before,
                "nonce": nonce_bytes,
            },
        }

        signature = self._sign(typed_data)

        payload = {
            "x402Version": 1,
            "scheme": "exact",
            "network": network,
            "payload": {
                "signature": signature,
                "authorization": {
                    "from": self._account_address,
                    "to": pay_to,
                    "value": amount,
                    "validAfter": str(valid_after),
                    "validBefore": str(valid_before),
                    "nonce": nonce_hex,
                },
                "asset": asset,
            },
        }
        raw = json.dumps(payload, separators=(",", ":")).encode()
        return base64.b64encode(raw).decode()

    def token_hint(self) -> str:
        """Preferred token symbol, sent as the ``X-PAYMENT-TOKEN`` header hint."""
        return self.prefer_symbol

    # -- internals -----------------------------------------------------------
    def _sign(self, typed_data: Dict[str, Any]) -> str:
        if self._signer is not None:
            sig = self._signer(typed_data)
            if not isinstance(sig, str) or not sig.startswith("0x"):
                raise AutoPayError("custom signer must return a 0x-prefixed signature string")
            return sig
        account = self._account(self._private_key)  # type: ignore[arg-type]
        encode_typed_data = self._encode_typed_data()
        signable = encode_typed_data(full_message=typed_data)
        signed = account.sign_message(signable)
        sig = signed.signature
        sig_hex = sig.hex() if hasattr(sig, "hex") else str(sig)
        if not sig_hex.startswith("0x"):
            sig_hex = "0x" + sig_hex
        return sig_hex

    @staticmethod
    def _eth_account():
        try:
            from eth_account import Account  # type: ignore
        except ImportError as exc:  # pragma: no cover - exercised via message
            raise AutoPayError(
                "automatic payment needs the 'eth-account' package. Install it with "
                "'pip install \"agent-margin-router[autopay]\"'."
            ) from exc
        return Account

    @classmethod
    def _account(cls, private_key: str):
        return cls._eth_account().from_key(private_key)

    @staticmethod
    def _encode_typed_data():
        try:
            from eth_account.messages import encode_typed_data  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise AutoPayError(
                "automatic payment needs the 'eth-account' package. Install it with "
                "'pip install \"agent-margin-router[autopay]\"'."
            ) from exc
        return encode_typed_data

    @classmethod
    def _derive_address(cls, private_key: str) -> str:
        return cls._account(private_key).address
