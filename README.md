# Agent Margin Router — Python SDK

[![PyPI](https://img.shields.io/pypi/v/agent-margin-router.svg)](https://pypi.org/project/agent-margin-router/)
[![Python](https://img.shields.io/pypi/pyversions/agent-margin-router.svg)](https://pypi.org/project/agent-margin-router/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Official Python client for the **[Agent Margin Router](https://agentmarginrouter.com)** API — one
pay-per-call HTTP interface that gives AI agents and applications clean, LLM-ready data across
**39 endpoints**: web scraping & search, crypto & market data, on-chain reads, DeFi analytics, and
developer utilities.

- **No signup to start** — every wallet gets **3 free calls** per endpoint family via the `X-WALLET` header.
- **Pay per call** — settle in **USDC on Base** through the [x402](https://www.x402.org/) standard, or use an API key.
- **Typed** — one Python method per endpoint, full type hints, `py.typed` shipped.
- **Small footprint** — a single runtime dependency (`httpx`).

---

## Installation

```bash
pip install agent-margin-router
```

Requires Python 3.9+.

---

## Quickstart

```python
from agent_margin_router import Client

# 3 free calls per wallet — no signup, no key.
client = Client(wallet="0xYourWalletAddress000000000000000000000000")

result = client.token_price(asset="ETH")
print(result["price"])        # median price across venues
print(result["cost_usdc"])    # 0 while on the free tier
print(result["routing"])      # provider, latency, cache hit, fallbacks
```

Using an API key instead (usage billed to the key's wallet):

```python
client = Client(api_key="amr_live_...")
spread = client.market_spread(asset="ETH", buy_venue="binance", sell_venue="coinbase")
```

The client is a context manager and reuses one HTTP connection pool:

```python
with Client(wallet="0x...") as client:
    fg = client.fear_greed()
    news = client.news_search(query="ethereum ETF", max_results=10)
```

---

## Authentication

Pass **one** of the following to `Client(...)`:

| Argument | Header sent | Effect |
|---|---|---|
| `wallet="0x..."` | `X-WALLET` | Free tier: 3 calls per wallet, no signup. |
| `api_key="amr_live_..."` | `X-API-KEY` | Usage & billing tied to the key's wallet. |
| *(neither)* | — | Anonymous, subject to a stricter per-IP limit. |

---

## Paying for calls (x402)

Once the free tier is exhausted and no API key is supplied, the API responds with **HTTP 402**.
The SDK raises `PaymentRequiredError`, which carries the exact payment requirements returned by the
server (asset, network, amount, pay-to address, facilitator):

```python
from agent_margin_router import Client, PaymentRequiredError

client = Client()  # anonymous
try:
    client.gas_fees(chain="base")
except PaymentRequiredError as e:
    print(e)                 # human-readable summary incl. price & pay-to
    print(e.accepts)         # list of accepted payment options (USDC on Base, ...)
```

Payments settle in USDC on Base to the router's fixed receiving address. You can either handle 402s
yourself (settle the amount from `e.accepts` out-of-band and retry with an `X-PAYMENT` header via
`Client(extra_headers={"X-PAYMENT": "..."})`), or let the SDK settle them automatically — see below.

---

## Automatic payment (opt-in, since v0.2)

Give the client an `AutoPay` helper backed by **your own** wallet's private key and 402s are settled
transparently: the SDK signs a single-use, exact-amount EIP-3009 `TransferWithAuthorization` (the
scheme x402 facilitators expect) and retries the call with the `X-PAYMENT` header. Install the extra:

```bash
pip install "agent-margin-router[autopay]"
```

```python
from agent_margin_router import Client, AutoPay

client = Client(auto_pay=AutoPay(
    private_key="0x...",     # the PAYING wallet's key — never leaves your process
    max_price_usd=0.10,      # hard per-call spend cap; pricier 402s are re-raised
))

data = client.token_price(asset="ETH")   # 402 is signed & settled automatically
```

The private key can also come from the `AGENT_MARGIN_ROUTER_PRIVATE_KEY` environment variable
(`AutoPay()` with no argument). Key points:

- **Your key, your control.** The key belongs to the paying agent, is used only locally to sign the
  transfer authorization, and is never transmitted anywhere.
- **Bounded.** Each signature authorizes a gasless, single-use transfer of the exact amount to the
  address the server put in `payTo` — nothing more. A random 32-byte nonce plus the server-side
  replay cache prevent reuse.
- **Capped.** `max_price_usd` is a client-side ceiling; any 402 above it raises `PaymentRequiredError`
  instead of paying. Leave it unset only if you trust every endpoint you call.
- **Token choice.** `prefer_symbol="USDC"` (default) picks the stablecoin when several are accepted.
- **Hardware/remote signers.** Pass `signer=<callable>` plus `account_address="0x..."` to sign with a
  custom backend instead of a raw key.

Without `auto_pay` the behavior is unchanged from v0.1: a `PaymentRequiredError` is raised and you
stay fully in control.

---

## Error handling

All exceptions derive from `AgentMarginRouterError`:

| Exception | Raised on | Key attributes |
|---|---|---|
| `PaymentRequiredError` | HTTP 402 | `accepts`, `body` |
| `RateLimitError` | HTTP 429 | `retry_after`, `body` |
| `AuthenticationError` | HTTP 401 / 403 | `status_code`, `body` |
| `APIError` | any other non-2xx / network error | `status_code`, `body` |

```python
from agent_margin_router import RateLimitError

try:
    client.web_search(query="...")
except RateLimitError as e:
    time.sleep(e.retry_after or 1.0)
```

---

## Response shape

Every endpoint returns a `dict`. Most endpoints put their payload fields **directly on the top
level** of the response, next to a common set of billing and routing metadata fields. For example,
`token_price()` returns `price`, `quote`, `sources`, `confidence`, … right alongside `cost_usdc`
and `routing`:

```jsonc
{
  // --- endpoint-specific fields (vary per endpoint) ---
  "asset": "ETH",
  "price": 3125.42,
  "quote": "USD",
  "sources": [ "..." ],
  "confidence": 0.99,

  // --- common metadata (present on every response) ---
  "cost_usdc": 0.01,
  "token": "USDC",            // or "FREE" while on the free tier
  "fetched_at": "2026-09-16T10:00:00Z",
  "freshness_seconds": 3,
  "routing": {
    "provider": "coinbase",
    "fallback_used": false,
    "providers_tried": ["binance", "coinbase"],
    "cache_hit": false,
    "latency_ms": 180
  }
}
```

A few endpoints (for example `extract_clean()`) instead nest their payload under a `data` key —
inspect `result.keys()` if you are unsure. The common metadata fields (`cost_usdc`, `token`,
`fetched_at`, `freshness_seconds`, `routing`) are always on the top level.

---

## Endpoints

All 39 endpoints, one typed method each. Prices are per successful call; the first 3 calls per
wallet are free.

| Method | Price | Required args | Description |
|---|---|---|---|
| `extract_clean()` | $0.02 | `url` | Clean page extraction from any public URL: title, meta description, main text, JSON-LD, language |
| `market_spread()` | $0.05 | `asset`, `buy_venue`, `sell_venue` | Cross-exchange crypto spread from live tickers: gross spread, fees, modelled slippage, transfer cost and net edge in bps for a given trade size |
| `gas_fees()` | $0.005 | – | Live EIP-1559 gas fees (slow/standard/fast tiers) plus USD cost per transaction type (transfer, ERC-20 transfer, swap, NFT mint) for Base, Ethereum, Arbitrum, Optimism and Polygon |
| `best_price()` | $0.005 | – | Best-price router: queries several independent gas-price sources in parallel, returns the cheapest quote and charges a configurable share of the savings (average - best) as commission |
| `token_price()` | $0.01 | `asset` | Multi-venue median spot price for any major crypto asset (Binance, Coinbase, Kraken, CoinGecko) with min/max, deviation and confidence score – one call instead of four |
| `wallet_balance()` | $0.01 | `address` | Native + stablecoin balances (ETH, USDC, USDT, DAI, WETH) of any EVM wallet with USD valuation, read directly from public RPC nodes on Base, Ethereum, Arbitrum, Optimism or Polygon |
| `web_search()` | $0.02 | `query` | Live web search results (title, URL, domain, snippet) for any query, key-less, region-aware |
| `email_validate()` | $0.01 | `email` | Validate an email address: RFC syntax, MX/A records via DNS-over-HTTPS, disposable and free-provider detection, role-account flag, deliverability score and verdict |
| `dns_whois()` | $0.005 | `domain` | DNS records (A, AAAA, MX, NS, TXT, CNAME, SOA, CAA) via DNS-over-HTTPS plus RDAP/WHOIS registration data (registrar, created/expires, status, nameservers, DNSSEC) |
| `pdf_text()` | $0.02 | `url` | Extract clean text (per page + full) and metadata from any public PDF URL up to 25 MB / 200 pages |
| `seo_check()` | $0.01 | `url` | On-page SEO audit of any URL: title, meta description, canonical, headings, images without alt, links, Open Graph, structured data, robots.txt/sitemap, prioritized issues and a 0-100 score with grade |
| `defi_yields()` | $0.02 | – | Live DeFi pool yields (APY, TVL, stablecoin flag) across 100+ chains and protocols from DefiLlama |
| `currency_convert()` | $0.005 | `from`, `to` | Fiat currency conversion with ECB reference rates (30+ currencies): amount, source currency, one or many targets |
| `geo_ip()` | $0.005 | `ip` | IP geolocation for IPv4/IPv6: country, region, city, coordinates, timezone, ASN, ISP/org, EU flag, private-range detection |
| `rss_feed()` | $0.01 | `url` | Fetch and parse any RSS 2.0 or Atom feed into clean JSON: title, link, published date, author, summary, optional full text content and categories per item |
| `crypto_ohlcv()` | $0.005 | `symbol` | Historical OHLCV candles for any major crypto pair (Binance, Coinbase fallback): intervals 1m-1w, up to 500 candles, with period summary (high, low, volume, change %) |
| `ens_resolve()` | $0.01 | `name` | Resolve an ENS name to its Ethereum address plus text records (url, com.twitter, avatar, ...) via on-chain calls |
| `html_to_markdown()` | $0.01 | `url` | Convert any public web page into clean, LLM-ready Markdown: main content only (boilerplate, nav and ads removed), headings, lists, tables and optional links/images preserved |
| `youtube_transcript()` | $0.02 | `video_id` | Fetch the transcript of a YouTube video (manual or auto-generated captions) as timestamped segments plus full text, with language preference and English fallback |
| `github_repo_summary()` | $0.01 | `repo` | One-call overview of any public GitHub repository: description, stars, forks, open issues, primary language and language split (%), topics, license, default branch, README excerpt and the 5 most recent commits |
| `dex_price()` | $0.01 | – | Live DEX price, 24h change, volume and liquidity for any on-chain token (long-tail tokens not listed on CEXs) by contract address or symbol on Base, Ethereum, Arbitrum, Optimism, Polygon, BSC, Avalanche or Solana, with the top liquidity pairs per DEX (DexScreener) |
| `tx_status()` | $0.01 | `tx_hash` | Status of any EVM transaction on Base, Ethereum, BSC, Polygon, Arbitrum or Optimism: success/failed/pending, block number, confirmations, gas used, effective gas price, fee, from/to/value and all ERC-20 Transfer events decoded from the receipt logs (contract, symbol, decimals, amount) |
| `erc20_balance()` | $0.01 | `wallet_address`, `contract_addresses` | Balances of up to 20 arbitrary ERC-20 tokens for one wallet in a single Multicall3 round-trip: raw and decimal-formatted balance, decimals and symbol per token, on Base, Ethereum, BSC, Polygon, Arbitrum or Optimism |
| `news_search()` | $0.02 | `query` | Global news article search across 65+ languages via the GDELT DOC 2.0 API: title, URL, source domain, publication time, language and country per article, with look-back window (e.g |
| `hn_search()` | $0.01 | `query` | Search Hacker News stories and comments via the Algolia HN API: title, URL, author, points, comment count, timestamp and HN discussion link; sort by relevance or date, optional tag filter (story, comment, ask_hn, show_hn) |
| `reddit_search()` | $0.01 | `query` | Search Reddit posts site-wide or within one subreddit: title, URL, subreddit, author, score, upvote ratio, comment count, timestamp and the first 500 characters of the post text; sort by relevance, hot, new, top or comments with a time filter |
| `defi_tvl()` | $0.005 | – | Total value locked of a DeFi protocol (by DefiLlama slug: TVL, 1d/7d change, market cap, mcap/TVL ratio, TVL per chain, category) or of a whole chain (TVL, native token, protocol count, top-10 protocols) |
| `fear_greed()` | $0.005 | – | Crypto market sentiment: the daily Fear & Greed index (0-100) with classification, 1d/7d change and up to 90 days of history from alternative.me |
| `agent_wallet_snapshot()` | $0.02 | `wallet_address` | One-call wallet overview for autonomous agents: native balance, ERC-20 balances (default stablecoins + WETH, or any contracts you pass), current gas price, tx count, contract check and USD values incl |
| `url_status()` | $0.005 | `url` | Health check for any public URL: HTTP status, full redirect chain, response time, content type, SSL certificate validity/expiry/issuer and a security-header audit (HSTS, CSP, X-Frame-Options, …) with score |
| `web_crawl()` | $0.05 | `start_url` | Mini crawler: fetches a start page and follows same-domain links breadth-first (max 10 pages), returning clean LLM-ready Markdown, title, word count and discovered links per page; honours robots.txt by default |
| `wikipedia_summary()` | $0.005 | `title` | Clean article summary from Wikipedia in any language: title, short description, extract (capped), canonical URL, thumbnail and coordinates; falls back to search when the title is fuzzy |
| `arxiv_search()` | $0.01 | `query` | Search arXiv preprints: returns id, title, authors, abstract, categories, published/updated dates and PDF links, sortable by relevance or date, optionally filtered by category (e.g |
| `npm_package()` | $0.005 | `name` | npm package intelligence: latest version, license, repository, maintainers, dependency count, publish dates and weekly downloads – ideal for dependency vetting by coding agents |
| `pypi_package()` | $0.005 | `name` | PyPI project intelligence: latest version, summary, license, author, project URLs, Python requirement, declared dependencies, release count and last release date |
| `geocode()` | $0.01 | `query` | Turn a place name or address into coordinates, bounding box, address parts and OSM type using OpenStreetMap Nominatim (ODbL); cached 24h |
| `domain_rdap()` | $0.01 | `domain` | Domain registration data via RDAP (the WHOIS successor): registered flag, registrar, status, registration/expiry events, nameservers and DNSSEC – for availability checks and due diligence |
| `dns_lookup()` | $0.005 | `name` | Resolve any DNS record type (A, AAAA, CNAME, MX, NS, TXT, SOA, SRV, CAA, PTR) over DNS-over-HTTPS with TTLs and DNSSEC validation flag |
| `contract_info()` | $0.02 | `address` | Smart-contract metadata from Blockscout for Base, Ethereum, Optimism or Arbitrum: verification status, name, compiler, proxy/implementation, creator, creation tx, token details and function/event names |

> `currency_convert()` uses `from_` as the parameter name (since `from` is a reserved word in Python);
> it is sent to the API as `from`.

---

## Links

- Website: https://agentmarginrouter.com
- API docs: https://agentmarginrouter.com/docs
- Live discovery catalog: https://agent-margin-router-production.up.railway.app/discovery/resources
- Source: https://github.com/AgentMarginRouter/agent-margin-router-python

## License

MIT © NovaNest
