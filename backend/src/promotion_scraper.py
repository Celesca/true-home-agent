from __future__ import annotations

from typing import Any


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
    return ddg, requests, BeautifulSoup


def scrape_promotions(query: str = "True promotion site:true.th/promotion") -> dict[str, Any]:
    """Best-effort scraper: use DuckDuckGo to find promotion pages, then fetch and parse HTML.

    Returns a dict with `items` list of promotions: {title, url, summary}
    If scraper dependencies are missing, returns an explanatory error.
    """
    ddg, requests, BeautifulSoup = _safe_imports()
    if ddg is None and (requests is None or BeautifulSoup is None):
        return {"error": "scraper_dependencies_missing"}

    results = []

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
            soup = BeautifulSoup(r.text, "lxml")
            # heuristic: find promotion cards
            cards = soup.select("a.promotion-card, .promotion-card, .card--promotion, article.promotion")
            if not cards:
                cards = soup.select("a[href*='/promotion']")[:8]
            for c in cards[:6]:
                a = c if c.name == "a" else c.find("a")
                url = a["href"] if a and a.has_attr("href") else None
                if url and url.startswith("/"):
                    url = "https://www.true.th" + url
                title_tag = c.find(["h2", "h3"]) if hasattr(c, "find") else None
                title = title_tag.get_text(strip=True) if title_tag else (a.get_text(strip=True) if a else "Promotion")
                p = c.find("p") if hasattr(c, "find") else None
                summary = p.get_text(strip=True) if p else ""
                results.append({"title": title, "url": url, "summary": summary})
        except Exception:
            pass

    return {"items": results}
