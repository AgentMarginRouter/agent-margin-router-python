# This file is auto-generated from the live /discovery/resources catalog.
# Do not edit by hand; regenerate with _gen_client.py.
# ruff: noqa: E501
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._base import BaseClient


class Client(BaseClient):
    """Synchronous client for the Agent Margin Router API.

    One typed method per endpoint. Each returns the parsed JSON response as a dict.
    See https://agentmarginrouter.com/docs for the full API reference.
    """

    def extract_clean(self,
        url: str,
        schema_: Optional[Dict[str, Any]] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Clean page extraction from any public URL: title, meta description, main text,
        JSON-LD, language. Optional `schema` keeps only the listed top-level keys. Apify
        (JS-rendered) with direct-fetch fallback. Pay per call with USDC or USDT on Base
        via x402 – no API key, no signup. 3 free calls per wallet.

        Endpoint: POST /extract-clean  —  price: $0.02 per call (3 free per wallet).

        Args:
            url: Public URL to extract.
            schema_: Optional JSON schema for the output.
            instructions: Optional natural-language hints.
        """
        body: Dict[str, Any] = {}
        body['url'] = url
        if schema_ is not None:
            body['schema'] = schema_
        if instructions is not None:
            body['instructions'] = instructions
        return self._request('extract-clean', body)

    def market_spread(self,
        asset: str,
        buy_venue: str,
        sell_venue: str,
        size_usd: Optional[float] = None,
        quote: Optional[str] = None,
        max_age_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Cross-exchange crypto spread from live tickers: gross spread, fees, modelled
        slippage, transfer cost and net edge in bps for a given trade size.
        Ticker/volume based (no full order book). Pay per call with USDC or USDT on Base
        via x402 – no API key, no signup. 3 free calls per wallet.

        Endpoint: POST /market-spread  —  price: $0.05 per call (3 free per wallet).

        Args:
            asset: Ticker, e.g. ETH.
            buy_venue: Venue to buy on, e.g. binance.
            sell_venue: Venue to sell on, e.g. coinbase.
            size_usd: Notional size in USD (default 1000).
            quote: Quote currency (default USDT).
            max_age_seconds: Max quote age (default 30).
        """
        body: Dict[str, Any] = {}
        body['asset'] = asset
        body['buy_venue'] = buy_venue
        body['sell_venue'] = sell_venue
        if size_usd is not None:
            body['size_usd'] = size_usd
        if quote is not None:
            body['quote'] = quote
        if max_age_seconds is not None:
            body['max_age_seconds'] = max_age_seconds
        return self._request('market-spread', body)

    def gas_fees(self,
        chain: Optional[str] = None,
        max_age_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Live EIP-1559 gas fees (slow/standard/fast tiers) plus USD cost per transaction
        type (transfer, ERC-20 transfer, swap, NFT mint) for Base, Ethereum, Arbitrum,
        Optimism and Polygon. Aggregated from public RPC nodes – no API key. Pay per
        call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /gas-fees  —  price: $0.005 per call (3 free per wallet).

        Args:
            chain: base | ethereum | arbitrum | optimism | polygon (default base).
            max_age_seconds: Max cache age (default 10).
        """
        body: Dict[str, Any] = {}
        if chain is not None:
            body['chain'] = chain
        if max_age_seconds is not None:
            body['max_age_seconds'] = max_age_seconds
        return self._request('gas-fees', body)

    def best_price(self,
        chain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Best-price router: queries several independent gas-price sources in parallel,
        returns the cheapest quote and charges a configurable share of the savings
        (average - best) as commission. Response includes the full breakdown
        (best_price, average_price, savings_gross, provision, user_pays) for Base,
        Ethereum, Arbitrum, Optimism and Polygon. No API key. Pay per call with USDC or
        USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /best-price  —  price: $0.005 per call (3 free per wallet).

        Args:
            chain: base | ethereum | arbitrum | optimism | polygon (default base).
        """
        body: Dict[str, Any] = {}
        if chain is not None:
            body['chain'] = chain
        return self._request('best-price', body)

    def token_price(self,
        asset: str,
        quote: Optional[str] = None,
        venues: Optional[List[Any]] = None,
        max_age_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Multi-venue median spot price for any major crypto asset (Binance, Coinbase,
        Kraken, CoinGecko) with min/max, deviation and confidence score – one call
        instead of four. No API key. Pay per call with USDC or USDT on Base via x402. 3
        free calls per wallet.

        Endpoint: POST /token-price  —  price: $0.01 per call (3 free per wallet).

        Args:
            asset: Ticker, e.g. ETH.
            quote: Quote currency (default USD).
            venues: Subset of binance, coinbase, kraken, coingecko.
            max_age_seconds: Max cache age (default 5).
        """
        body: Dict[str, Any] = {}
        body['asset'] = asset
        if quote is not None:
            body['quote'] = quote
        if venues is not None:
            body['venues'] = venues
        if max_age_seconds is not None:
            body['max_age_seconds'] = max_age_seconds
        return self._request('token-price', body)

    def wallet_balance(self,
        address: str,
        chain: Optional[str] = None,
        tokens: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Native + stablecoin balances (ETH, USDC, USDT, DAI, WETH) of any EVM wallet with
        USD valuation, read directly from public RPC nodes on Base, Ethereum, Arbitrum,
        Optimism or Polygon. No API key. Pay per call with USDC or USDT on Base via
        x402. 3 free calls per wallet.

        Endpoint: POST /wallet-balance  —  price: $0.01 per call (3 free per wallet).

        Args:
            address: EVM address (0x + 40 hex chars).
            chain: base | ethereum | arbitrum | optimism | polygon (default base).
            tokens: Token symbols, default all known (USDC, USDT, DAI, WETH).
        """
        body: Dict[str, Any] = {}
        body['address'] = address
        if chain is not None:
            body['chain'] = chain
        if tokens is not None:
            body['tokens'] = tokens
        return self._request('wallet-balance', body)

    def web_search(self,
        query: str,
        max_results: Optional[int] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Live web search results (title, URL, domain, snippet) for any query, key-less,
        region-aware. Pay per call with USDC or USDT on Base via x402. 3 free calls per
        wallet.

        Endpoint: POST /web-search  —  price: $0.02 per call (3 free per wallet).

        Args:
            query: Search query (1-400 chars).
            max_results: 1-20, default 10.
            region: Region code, e.g. wt-wt, de-de, us-en.
        """
        body: Dict[str, Any] = {}
        body['query'] = query
        if max_results is not None:
            body['max_results'] = max_results
        if region is not None:
            body['region'] = region
        return self._request('web-search', body)

    def email_validate(self,
        email: str,
        check_mx: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Validate an email address: RFC syntax, MX/A records via DNS-over-HTTPS,
        disposable and free-provider detection, role-account flag, deliverability score
        and verdict. Pay per call with USDC or USDT on Base via x402. 3 free calls per
        wallet.

        Endpoint: POST /email-validate  —  price: $0.01 per call (3 free per wallet).

        Args:
            email: Email address.
            check_mx: Resolve MX records (default true).
        """
        body: Dict[str, Any] = {}
        body['email'] = email
        if check_mx is not None:
            body['check_mx'] = check_mx
        return self._request('email-validate', body)

    def dns_whois(self,
        domain: str,
        record_types: Optional[List[Any]] = None,
        include_whois: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """DNS records (A, AAAA, MX, NS, TXT, CNAME, SOA, CAA) via DNS-over-HTTPS plus
        RDAP/WHOIS registration data (registrar, created/expires, status, nameservers,
        DNSSEC). Pay per call with USDC or USDT on Base via x402. 3 free calls per
        wallet.

        Endpoint: POST /dns-whois  —  price: $0.005 per call (3 free per wallet).

        Args:
            domain: Domain name, e.g. example.com.
            record_types: Default A AAAA MX NS TXT CNAME.
            include_whois: Include RDAP data (default true).
        """
        body: Dict[str, Any] = {}
        body['domain'] = domain
        if record_types is not None:
            body['record_types'] = record_types
        if include_whois is not None:
            body['include_whois'] = include_whois
        return self._request('dns-whois', body)

    def pdf_text(self,
        url: str,
        max_pages: Optional[int] = None,
        pages: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Extract clean text (per page + full) and metadata from any public PDF URL up to
        25 MB / 200 pages. Pay per call with USDC or USDT on Base via x402. 3 free calls
        per wallet.

        Endpoint: POST /pdf-text  —  price: $0.02 per call (3 free per wallet).

        Args:
            url: Public PDF URL.
            max_pages: 1-200, default 50.
            pages: 1-based page numbers to extract.
        """
        body: Dict[str, Any] = {}
        body['url'] = url
        if max_pages is not None:
            body['max_pages'] = max_pages
        if pages is not None:
            body['pages'] = pages
        return self._request('pdf-text', body)

    def seo_check(self,
        url: str,
        check_robots: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """On-page SEO audit of any URL: title, meta description, canonical, headings,
        images without alt, links, Open Graph, structured data, robots.txt/sitemap,
        prioritized issues and a 0-100 score with grade. Pay per call with USDC or USDT
        on Base via x402. 3 free calls per wallet.

        Endpoint: POST /seo-check  —  price: $0.01 per call (3 free per wallet).

        Args:
            url: Page URL to audit.
            check_robots: Probe robots.txt + sitemap (default true).
        """
        body: Dict[str, Any] = {}
        body['url'] = url
        if check_robots is not None:
            body['check_robots'] = check_robots
        return self._request('seo-check', body)

    def defi_yields(self,
        chain: Optional[str] = None,
        asset: Optional[str] = None,
        project: Optional[str] = None,
        min_tvl_usd: Optional[float] = None,
        stablecoins_only: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Live DeFi pool yields (APY, TVL, stablecoin flag) across 100+ chains and
        protocols from DefiLlama. Filter by chain, asset, project, minimum TVL; sorted
        by APY. Pay per call with USDC or USDT on Base via x402. 3 free calls per
        wallet.

        Endpoint: POST /defi-yields  —  price: $0.02 per call (3 free per wallet).

        Args:
            chain: Chain filter, e.g. Base, Ethereum.
            asset: Asset symbol in pool, e.g. USDC.
            project: Protocol slug, e.g. aave-v3.
            min_tvl_usd: Minimum TVL in USD (default 100000).
            stablecoins_only: Only stablecoin pools.
            limit: Max pools (1-50, default 10).
        """
        body: Dict[str, Any] = {}
        if chain is not None:
            body['chain'] = chain
        if asset is not None:
            body['asset'] = asset
        if project is not None:
            body['project'] = project
        if min_tvl_usd is not None:
            body['min_tvl_usd'] = min_tvl_usd
        if stablecoins_only is not None:
            body['stablecoins_only'] = stablecoins_only
        if limit is not None:
            body['limit'] = limit
        return self._request('defi-yields', body)

    def currency_convert(self,
        from_: str,
        to: List[Any],
        amount: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Fiat currency conversion with ECB reference rates (30+ currencies): amount,
        source currency, one or many targets. Returns rates, converted amounts and rate
        date. Pay per call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /currency-convert  —  price: $0.005 per call (3 free per wallet).

        Args:
            from_: ISO-4217 source currency, e.g. EUR.
            to: Target currencies, e.g. ["USD", "GBP"].
            amount: Amount in source currency (default 1).
        """
        body: Dict[str, Any] = {}
        body['from'] = from_
        body['to'] = to
        if amount is not None:
            body['amount'] = amount
        return self._request('currency-convert', body)

    def geo_ip(self,
        ip: str,
    ) -> Dict[str, Any]:
        """IP geolocation for IPv4/IPv6: country, region, city, coordinates, timezone, ASN,
        ISP/org, EU flag, private-range detection. Pay per call with USDC or USDT on
        Base via x402. 3 free calls per wallet.

        Endpoint: POST /geo-ip  —  price: $0.005 per call (3 free per wallet).

        Args:
            ip: IPv4 or IPv6 address.
        """
        body: Dict[str, Any] = {}
        body['ip'] = ip
        return self._request('geo-ip', body)

    def rss_feed(self,
        url: str,
        max_items: Optional[int] = None,
        include_content: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Fetch and parse any RSS 2.0 or Atom feed into clean JSON: title, link, published
        date, author, summary, optional full text content and categories per item. Pay
        per call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /rss-feed  —  price: $0.01 per call (3 free per wallet).

        Args:
            url: Feed URL.
            max_items: Max items (1-100, default 20).
            include_content: Include full text content.
        """
        body: Dict[str, Any] = {}
        body['url'] = url
        if max_items is not None:
            body['max_items'] = max_items
        if include_content is not None:
            body['include_content'] = include_content
        return self._request('rss-feed', body)

    def crypto_ohlcv(self,
        symbol: str,
        quote: Optional[str] = None,
        interval: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Historical OHLCV candles for any major crypto pair (Binance, Coinbase fallback):
        intervals 1m-1w, up to 500 candles, with period summary (high, low, volume,
        change %). Pay per call with USDC or USDT on Base via x402. 3 free calls per
        wallet.

        Endpoint: POST /crypto-ohlcv  —  price: $0.005 per call (3 free per wallet).

        Args:
            symbol: Base asset, e.g. BTC.
            quote: Quote asset (default USDT).
            interval: 1m 5m 15m 30m 1h 4h 1d 1w (default 1h).
            limit: Candles (1-500, default 100).
        """
        body: Dict[str, Any] = {}
        body['symbol'] = symbol
        if quote is not None:
            body['quote'] = quote
        if interval is not None:
            body['interval'] = interval
        if limit is not None:
            body['limit'] = limit
        return self._request('crypto-ohlcv', body)

    def ens_resolve(self,
        name: str,
        text_keys: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """Resolve an ENS name to its Ethereum address plus text records (url, com.twitter,
        avatar, ...) via on-chain calls. Pay per call with USDC or USDT on Base via
        x402. 3 free calls per wallet.

        Endpoint: POST /ens-resolve  —  price: $0.01 per call (3 free per wallet).

        Args:
            name: ENS name, e.g. vitalik.eth.
            text_keys: Text records to read (default url, com.twitter, avatar).
        """
        body: Dict[str, Any] = {}
        body['name'] = name
        if text_keys is not None:
            body['text_keys'] = text_keys
        return self._request('ens-resolve', body)

    def html_to_markdown(self,
        url: str,
        include_links: Optional[bool] = None,
        include_images: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Convert any public web page into clean, LLM-ready Markdown: main content only
        (boilerplate, nav and ads removed), headings, lists, tables and optional
        links/images preserved. Trafilatura extraction with markdownify fallback, SSRF-
        guarded fetch, up to 3 MB HTML. Pay per call with USDC or USDT on Base via x402.
        3 free calls per wallet.

        Endpoint: POST /html-to-markdown  —  price: $0.01 per call (3 free per wallet).

        Args:
            url: Public page URL.
            include_links: Keep hyperlinks (default true).
            include_images: Keep images (default false).
        """
        body: Dict[str, Any] = {}
        body['url'] = url
        if include_links is not None:
            body['include_links'] = include_links
        if include_images is not None:
            body['include_images'] = include_images
        return self._request('html-to-markdown', body)

    def youtube_transcript(self,
        video_id: str,
        language: Optional[str] = None,
        include_segments: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Fetch the transcript of a YouTube video (manual or auto-generated captions) as
        timestamped segments plus full text, with language preference and English
        fallback. Accepts a video id or any YouTube URL. No API key, no download. Pay
        per call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /youtube-transcript  —  price: $0.02 per call (3 free per wallet).

        Args:
            video_id: 11-char video id or YouTube URL.
            language: Preferred caption language (default en).
            include_segments: Return timestamped segments (default true).
        """
        body: Dict[str, Any] = {}
        body['video_id'] = video_id
        if language is not None:
            body['language'] = language
        if include_segments is not None:
            body['include_segments'] = include_segments
        return self._request('youtube-transcript', body)

    def github_repo_summary(self,
        repo: str,
        include_readme: Optional[bool] = None,
        include_commits: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """One-call overview of any public GitHub repository: description, stars, forks,
        open issues, primary language and language split (%), topics, license, default
        branch, README excerpt and the 5 most recent commits. Pay per call with USDC or
        USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /github-repo-summary  —  price: $0.01 per call (3 free per wallet).

        Args:
            repo: owner/name or github.com URL.
            include_readme: Include README excerpt (default true).
            include_commits: Include recent commits (default true).
        """
        body: Dict[str, Any] = {}
        body['repo'] = repo
        if include_readme is not None:
            body['include_readme'] = include_readme
        if include_commits is not None:
            body['include_commits'] = include_commits
        return self._request('github-repo-summary', body)

    def dex_price(self,
        token_address: Optional[str] = None,
        symbol: Optional[str] = None,
        chain: Optional[str] = None,
        max_pairs: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Live DEX price, 24h change, volume and liquidity for any on-chain token (long-
        tail tokens not listed on CEXs) by contract address or symbol on Base, Ethereum,
        Arbitrum, Optimism, Polygon, BSC, Avalanche or Solana, with the top liquidity
        pairs per DEX (DexScreener). Pay per call with USDC or USDT on Base via x402. 3
        free calls per wallet.

        Endpoint: POST /dex-price  —  price: $0.01 per call (3 free per wallet).

        Args:
            token_address: Token contract address (preferred).
            symbol: Token symbol, e.g. AERO (if no address).
            chain: base (default), ethereum, arbitrum, optimism, polygon, bsc, avalanche, solana.
            max_pairs: Pairs to return (1-20, default 5).
        """
        body: Dict[str, Any] = {}
        if token_address is not None:
            body['token_address'] = token_address
        if symbol is not None:
            body['symbol'] = symbol
        if chain is not None:
            body['chain'] = chain
        if max_pairs is not None:
            body['max_pairs'] = max_pairs
        return self._request('dex-price', body)

    def tx_status(self,
        tx_hash: str,
        chain: Optional[str] = None,
        max_age_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Status of any EVM transaction on Base, Ethereum, BSC, Polygon, Arbitrum or
        Optimism: success/failed/pending, block number, confirmations, gas used,
        effective gas price, fee, from/to/value and all ERC-20 Transfer events decoded
        from the receipt logs (contract, symbol, decimals, amount). Public JSON-RPC
        nodes with fallback. Pay per call with USDC or USDT on Base via x402. 3 free
        calls per wallet.

        Endpoint: POST /tx-status  —  price: $0.01 per call (3 free per wallet).

        Args:
            tx_hash: Transaction hash (0x + 64 hex).
            chain: base (default), ethereum, bsc, polygon, arbitrum, optimism.
            max_age_seconds: Accept cached result up to N seconds old (default 0).
        """
        body: Dict[str, Any] = {}
        body['tx_hash'] = tx_hash
        if chain is not None:
            body['chain'] = chain
        if max_age_seconds is not None:
            body['max_age_seconds'] = max_age_seconds
        return self._request('tx-status', body)

    def erc20_balance(self,
        wallet_address: str,
        contract_addresses: List[Any],
        chain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Balances of up to 20 arbitrary ERC-20 tokens for one wallet in a single
        Multicall3 round-trip: raw and decimal-formatted balance, decimals and symbol
        per token, on Base, Ethereum, BSC, Polygon, Arbitrum or Optimism. Pay per call
        with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /erc20-balance  —  price: $0.01 per call (3 free per wallet).

        Args:
            wallet_address: EVM wallet address.
            contract_addresses: 1-20 ERC-20 contract addresses.
            chain: base (default), ethereum, bsc, polygon, arbitrum, optimism.
        """
        body: Dict[str, Any] = {}
        body['wallet_address'] = wallet_address
        body['contract_addresses'] = contract_addresses
        if chain is not None:
            body['chain'] = chain
        return self._request('erc20-balance', body)

    def news_search(self,
        query: str,
        max_results: Optional[int] = None,
        language: Optional[str] = None,
        timespan: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Global news article search across 65+ languages via the GDELT DOC 2.0 API:
        title, URL, source domain, publication time, language and country per article,
        with look-back window (e.g. 24h, 7d) and language filter. Pay per call with USDC
        or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /news-search  —  price: $0.02 per call (3 free per wallet).

        Args:
            query: Search phrase (GDELT query syntax allowed).
            max_results: 1-50 (default 10).
            language: ISO-639-1 article language (default en).
            timespan: Look-back window, e.g. 24h, 7d (default), 4w.
        """
        body: Dict[str, Any] = {}
        body['query'] = query
        if max_results is not None:
            body['max_results'] = max_results
        if language is not None:
            body['language'] = language
        if timespan is not None:
            body['timespan'] = timespan
        return self._request('news-search', body)

    def hn_search(self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search Hacker News stories and comments via the Algolia HN API: title, URL,
        author, points, comment count, timestamp and HN discussion link; sort by
        relevance or date, optional tag filter (story, comment, ask_hn, show_hn). Pay
        per call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /hn-search  —  price: $0.01 per call (3 free per wallet).

        Args:
            query: Search phrase.
            max_results: 1-50 (default 10).
            sort_by: relevance (default) or date.
            tags: Algolia tags, e.g. story, ask_hn, show_hn, comment.
        """
        body: Dict[str, Any] = {}
        body['query'] = query
        if max_results is not None:
            body['max_results'] = max_results
        if sort_by is not None:
            body['sort_by'] = sort_by
        if tags is not None:
            body['tags'] = tags
        return self._request('hn-search', body)

    def reddit_search(self,
        query: str,
        subreddit: Optional[str] = None,
        max_results: Optional[int] = None,
        sort: Optional[str] = None,
        time_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search Reddit posts site-wide or within one subreddit: title, URL, subreddit,
        author, score, upvote ratio, comment count, timestamp and the first 500
        characters of the post text; sort by relevance, hot, new, top or comments with a
        time filter. Pay per call with USDC or USDT on Base via x402. 3 free calls per
        wallet.

        Endpoint: POST /reddit-search  —  price: $0.01 per call (3 free per wallet).

        Args:
            query: Search phrase.
            subreddit: Restrict to one subreddit, e.g. ethereum.
            max_results: 1-50 (default 10).
            sort: relevance (default), hot, new, top, comments.
            time_filter: hour, day, week, month, year, all (default).
        """
        body: Dict[str, Any] = {}
        body['query'] = query
        if subreddit is not None:
            body['subreddit'] = subreddit
        if max_results is not None:
            body['max_results'] = max_results
        if sort is not None:
            body['sort'] = sort
        if time_filter is not None:
            body['time_filter'] = time_filter
        return self._request('reddit-search', body)

    def defi_tvl(self,
        protocol: Optional[str] = None,
        chain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Total value locked of a DeFi protocol (by DefiLlama slug: TVL, 1d/7d change,
        market cap, mcap/TVL ratio, TVL per chain, category) or of a whole chain (TVL,
        native token, protocol count, top-10 protocols). Pay per call with USDC or USDT
        on Base via x402. 3 free calls per wallet.

        Endpoint: POST /defi-tvl  —  price: $0.005 per call (3 free per wallet).

        Args:
            protocol: DefiLlama protocol slug, e.g. aave, uniswap, aerodrome (either protocol or chain).
            chain: Chain name, e.g. base, ethereum, arbitrum.
        """
        body: Dict[str, Any] = {}
        if protocol is not None:
            body['protocol'] = protocol
        if chain is not None:
            body['chain'] = chain
        return self._request('defi-tvl', body)

    def fear_greed(self,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Crypto market sentiment: the daily Fear & Greed index (0-100) with
        classification, 1d/7d change and up to 90 days of history from alternative.me.
        Pay per call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /fear-greed  —  price: $0.005 per call (3 free per wallet).

        Args:
            limit: Daily data points to return, 1-90 (default 1).
        """
        body: Dict[str, Any] = {}
        if limit is not None:
            body['limit'] = limit
        return self._request('fear-greed', body)

    def agent_wallet_snapshot(self,
        wallet_address: str,
        chain: Optional[str] = None,
        token_contracts: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """One-call wallet overview for autonomous agents: native balance, ERC-20 balances
        (default stablecoins + WETH, or any contracts you pass), current gas price, tx
        count, contract check and USD values incl. total – bundles what would otherwise
        be 5+ RPC calls. Base, Ethereum, BSC, Polygon, Arbitrum, Optimism. Pay per call
        with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /agent-wallet-snapshot  —  price: $0.02 per call (3 free per wallet).

        Args:
            wallet_address: EVM wallet address.
            chain: base (default), ethereum, bsc, polygon, arbitrum, optimism.
            token_contracts: ERC-20 contracts to include (max 20); default: USDC, USDT, DAI, WETH.
        """
        body: Dict[str, Any] = {}
        body['wallet_address'] = wallet_address
        if chain is not None:
            body['chain'] = chain
        if token_contracts is not None:
            body['token_contracts'] = token_contracts
        return self._request('agent-wallet-snapshot', body)

    def url_status(self,
        url: str,
    ) -> Dict[str, Any]:
        """Health check for any public URL: HTTP status, full redirect chain, response
        time, content type, SSL certificate validity/expiry/issuer and a security-header
        audit (HSTS, CSP, X-Frame-Options, …) with score. SSRF-guarded (private/internal
        targets are rejected). Pay per call with USDC or USDT on Base via x402. 3 free
        calls per wallet.

        Endpoint: POST /url-status  —  price: $0.005 per call (3 free per wallet).

        Args:
            url: Public http(s) URL to probe.
        """
        body: Dict[str, Any] = {}
        body['url'] = url
        return self._request('url-status', body)

    def web_crawl(self,
        start_url: str,
        max_pages: Optional[int] = None,
        follow_links: Optional[bool] = None,
        include_links: Optional[bool] = None,
        respect_robots: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Mini crawler: fetches a start page and follows same-domain links breadth-first
        (max 10 pages), returning clean LLM-ready Markdown, title, word count and
        discovered links per page; honours robots.txt by default. SSRF-guarded. Pay per
        call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /web-crawl  —  price: $0.05 per call (3 free per wallet).

        Args:
            start_url: Public page to start from.
            max_pages: 1-10 (default 5).
            follow_links: Follow same-domain links (default true).
            include_links: Keep hyperlinks in Markdown (default true).
            respect_robots: Honour robots.txt Disallow for '*' (default true).
        """
        body: Dict[str, Any] = {}
        body['start_url'] = start_url
        if max_pages is not None:
            body['max_pages'] = max_pages
        if follow_links is not None:
            body['follow_links'] = follow_links
        if include_links is not None:
            body['include_links'] = include_links
        if respect_robots is not None:
            body['respect_robots'] = respect_robots
        return self._request('web-crawl', body)

    def wikipedia_summary(self,
        title: str,
        language: Optional[str] = None,
        max_chars: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Clean article summary from Wikipedia in any language: title, short description,
        extract (capped), canonical URL, thumbnail and coordinates; falls back to search
        when the title is fuzzy. Content CC BY-SA 4.0. Pay per call with USDC or USDT on
        Base via x402. 3 free calls per wallet.

        Endpoint: POST /wikipedia-summary  —  price: $0.005 per call (3 free per wallet).

        Args:
            title: Article title or search phrase.
            language: Wikipedia language code (default en).
            max_chars: 100-5000 characters of extract (default 1200).
        """
        body: Dict[str, Any] = {}
        body['title'] = title
        if language is not None:
            body['language'] = language
        if max_chars is not None:
            body['max_chars'] = max_chars
        return self._request('wikipedia-summary', body)

    def arxiv_search(self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search arXiv preprints: returns id, title, authors, abstract, categories,
        published/updated dates and PDF links, sortable by relevance or date, optionally
        filtered by category (e.g. cs.AI). Pay per call with USDC or USDT on Base via
        x402. 3 free calls per wallet.

        Endpoint: POST /arxiv-search  —  price: $0.01 per call (3 free per wallet).

        Args:
            query: Free-text search query.
            max_results: 1-50 (default 10).
            sort_by: Sort order (default relevance).
            category: Optional arXiv category, e.g. cs.AI.
        """
        body: Dict[str, Any] = {}
        body['query'] = query
        if max_results is not None:
            body['max_results'] = max_results
        if sort_by is not None:
            body['sort_by'] = sort_by
        if category is not None:
            body['category'] = category
        return self._request('arxiv-search', body)

    def npm_package(self,
        name: str,
    ) -> Dict[str, Any]:
        """npm package intelligence: latest version, license, repository, maintainers,
        dependency count, publish dates and weekly downloads – ideal for dependency
        vetting by coding agents. Pay per call with USDC or USDT on Base via x402. 3
        free calls per wallet.

        Endpoint: POST /npm-package  —  price: $0.005 per call (3 free per wallet).

        Args:
            name: npm package name (scoped allowed, e.g. @scope/pkg).
        """
        body: Dict[str, Any] = {}
        body['name'] = name
        return self._request('npm-package', body)

    def pypi_package(self,
        name: str,
    ) -> Dict[str, Any]:
        """PyPI project intelligence: latest version, summary, license, author, project
        URLs, Python requirement, declared dependencies, release count and last release
        date. Pay per call with USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /pypi-package  —  price: $0.005 per call (3 free per wallet).

        Args:
            name: PyPI project name.
        """
        body: Dict[str, Any] = {}
        body['name'] = name
        return self._request('pypi-package', body)

    def geocode(self,
        query: str,
        max_results: Optional[int] = None,
        country_codes: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Turn a place name or address into coordinates, bounding box, address parts and
        OSM type using OpenStreetMap Nominatim (ODbL); cached 24h. Pay per call with
        USDC or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /geocode  —  price: $0.01 per call (3 free per wallet).

        Args:
            query: Place name or address.
            max_results: 1-10 (default 5).
            country_codes: Comma-separated ISO codes, e.g. de,at.
            language: Result language (default en).
        """
        body: Dict[str, Any] = {}
        body['query'] = query
        if max_results is not None:
            body['max_results'] = max_results
        if country_codes is not None:
            body['country_codes'] = country_codes
        if language is not None:
            body['language'] = language
        return self._request('geocode', body)

    def domain_rdap(self,
        domain: str,
    ) -> Dict[str, Any]:
        """Domain registration data via RDAP (the WHOIS successor): registered flag,
        registrar, status, registration/expiry events, nameservers and DNSSEC – for
        availability checks and due diligence. Pay per call with USDC or USDT on Base
        via x402. 3 free calls per wallet.

        Endpoint: POST /domain-rdap  —  price: $0.01 per call (3 free per wallet).

        Args:
            domain: Registrable domain, e.g. example.com.
        """
        body: Dict[str, Any] = {}
        body['domain'] = domain
        return self._request('domain-rdap', body)

    def dns_lookup(self,
        name: str,
        record_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolve any DNS record type (A, AAAA, CNAME, MX, NS, TXT, SOA, SRV, CAA, PTR)
        over DNS-over-HTTPS with TTLs and DNSSEC validation flag. Pay per call with USDC
        or USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /dns-lookup  —  price: $0.005 per call (3 free per wallet).

        Args:
            name: Host name to resolve.
            record_type: Record type (default A).
        """
        body: Dict[str, Any] = {}
        body['name'] = name
        if record_type is not None:
            body['record_type'] = record_type
        return self._request('dns-lookup', body)

    def contract_info(self,
        address: str,
        chain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Smart-contract metadata from Blockscout for Base, Ethereum, Optimism or
        Arbitrum: verification status, name, compiler, proxy/implementation, creator,
        creation tx, token details and function/event names. Pay per call with USDC or
        USDT on Base via x402. 3 free calls per wallet.

        Endpoint: POST /contract-info  —  price: $0.02 per call (3 free per wallet).

        Args:
            address: EVM contract or wallet address (0x...).
            chain: Chain (default base).
        """
        body: Dict[str, Any] = {}
        body['address'] = address
        if chain is not None:
            body['chain'] = chain
        return self._request('contract-info', body)

