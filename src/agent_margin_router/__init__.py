"""Agent Margin Router – official Python SDK.

One pay-per-call HTTP endpoint for web scraping, market data, on-chain reads,
DeFi, and developer utilities. Pay with USDC on Base via x402 – or use an API
key – with 3 free calls per wallet.

Quickstart::

    from agent_margin_router import Client

    client = Client(wallet="0xYourWallet...")  # 3 free calls per wallet
    data = client.token_price(asset="ETH")
    print(data["data"])

See https://agentmarginrouter.com/docs for the full reference.
"""
from .autopay import AutoPay, AutoPayError
from .client import Client
from .exceptions import (
    AgentMarginRouterError,
    APIError,
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
)

__version__ = "0.2.0"

__all__ = [
    "Client",
    "AutoPay",
    "AutoPayError",
    "AgentMarginRouterError",
    "APIError",
    "AuthenticationError",
    "PaymentRequiredError",
    "RateLimitError",
    "__version__",
]
