from __future__ import annotations

from typing import Any
import asyncio
import re
import threading
from urllib.parse import urljoin


def _safe_imports():
    try:
        from duckduckgo_search import ddg
    except Exception:  # pragma: no cover - best-effort
        ddg = None
    try:
        import requests
        from bs4 import BeautifulSoup
    except Exception:  # pragma: no cover
        requests = None
        BeautifulSoup = None
    try:
        from crawl4ai import AsyncWebCrawler
    except Exception:  # pragma: no cover
        AsyncWebCrawler = None
    return ddg, requests, BeautifulSoup, AsyncWebCrawler


def _run_async(coro: Any, timeout_seconds: int = 12):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout_seconds))

    result: dict[str, Any] = {"value": None}

    def runner():
        try:
            result["value"] = asyncio.run(asyncio.wait_for(coro, timeout=timeout_seconds))
        except Exception:
            result["value"] = None

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join(timeout_seconds + 2)
    return result["value"]


async def _crawl4ai_fetch(url: str, AsyncWebCrawler):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        markdown = getattr(result, "markdown", "")
        if hasattr(markdown, "raw_markdown"):
            return markdown.raw_markdown
        if isinstance(markdown, str):
            return markdown
        return str(markdown)


def _extract_promotions_from_markdown(markdown: str) -> list[dict[str, Any]]:
    if not markdown:
        return []
    items: list[dict[str, Any]] = []
    seen = set()
    pattern = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
    for line in markdown.splitlines():
        if "/promotion" not in line:
            continue
        for match in pattern.finditer(line):
            title, url = match.groups()
            if "/promotion" not in url:
                continue
            if url in seen:
                continue
            seen.add(url)
            items.append({"title": title.strip(), "url": url, "summary": ""})
            if len(items) >= 6:
                return items
    return items


def scrape_promotions(query: str = "True promotion site:true.th/promotion") -> dict[str, Any]:
    """Best-effort scraper: use DuckDuckGo to find promotion pages, then fetch and parse HTML.

    Returns a dict with `items` list of promotions: {title, url, summary}
    If scraper dependencies are missing, returns an explanatory error.
    """
    ddg, requests, BeautifulSoup, AsyncWebCrawler = _safe_imports()
    if ddg is None and (requests is None or BeautifulSoup is None) and AsyncWebCrawler is None:
        return {"error": "scraper_dependencies_missing"}

    results = []

    # Try Crawl4AI first if available
    if AsyncWebCrawler is not None:
        markdown = _run_async(_crawl4ai_fetch("https://www.true.th/promotion", AsyncWebCrawler))
        results.extend(_extract_promotions_from_markdown(markdown or ""))

    # Try searching via DuckDuckGo first
    if ddg is not None:
        try:
            hits = ddg(query, max_results=5)
        except Exception:
            hits = []
        for hit in hits or []:
            url = hit.get("href") or hit.get("url") or hit.get("link")
            title = hit.get("title") or hit.get("title")
            summary = hit.get("body") or ""
            results.append({"title": title, "url": url, "summary": summary})

    # If we have requests/bs4 and no results yet, try direct fetch of the promotion page
    if (not results) and requests is not None and BeautifulSoup is not None:
        try:
            r = requests.get("https://www.true.th/promotion", timeout=8)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            # heuristic: find promotion cards
            cards = soup.select("a.promotion-card, .promotion-card, .card--promotion, article.promotion")
            if not cards:
                cards = soup.select("a[href*='/promotion']")[:8]
            for c in cards[:6]:
                a = c if c.name == "a" else c.find("a")
                url = a["href"] if a and a.has_attr("href") else None
                if url and url.startswith("/"):
                    url = urljoin("https://www.true.th", url)
                title_tag = c.find(["h2", "h3"]) if hasattr(c, "find") else None
                title = title_tag.get_text(strip=True) if title_tag else (a.get_text(strip=True) if a else "Promotion")
                p = c.find("p") if hasattr(c, "find") else None
                summary = p.get_text(strip=True) if p else ""
                results.append({"title": title, "url": url, "summary": summary})
        except Exception:
            pass

    return {"items": results}
