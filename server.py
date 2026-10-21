"""MCP server pre Wikipédiu – vyhľadávanie, zhrnutie a celý text článku."""

import os
from urllib.parse import quote

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Wikipedia")

# Wikipédia vyžaduje vlastný User-Agent s kontaktom. Doplň svoj email.
HEADERS = {"User-Agent": "wiki-mcp/0.1 (tvoj-email@example.com)"}
TIMEOUT = 15.0


def _base(lang: str) -> str:
    return f"https://{lang}.wikipedia.org"


@mcp.tool
async def search_wiki(query: str, lang: str = "sk", limit: int = 5) -> str:
    """Vyhľadá články na Wikipédii.

    Args:
        query: hľadaný výraz, napr. "Malé Karpaty"
        lang: jazyk Wikipédie (sk, en, cs, ...)
        limit: počet výsledkov (1 až 20)
    """
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": max(1, min(limit, 20)),
        "format": "json",
        "utf8": 1,
    }
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT) as client:
        r = await client.get(f"{_base(lang)}/w/api.php", params=params)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])

    if not results:
        return f"Nič som nenašiel pre „{query}“."
    return "\n".join(f"- {item['title']}" for item in results)


@mcp.tool
async def get_summary(title: str, lang: str = "sk") -> str:
    """Vráti krátke zhrnutie článku a odkaz naň.

    Args:
        title: presný názov článku (napr. z výsledku search_wiki)
        lang: jazyk Wikipédie
    """
    url = f"{_base(lang)}/api/rest_v1/page/summary/{quote(title.replace(' ', '_'))}"
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
        r = await client.get(url)
        if r.status_code == 404:
            return f"Článok „{title}“ neexistuje. Skús najprv search_wiki."
        r.raise_for_status()
        data = r.json()

    link = data.get("content_urls", {}).get("desktop", {}).get("page", "")
    return f"{data.get('title', title)}\n\n{data.get('extract', '')}\n\n{link}"


@mcp.tool
async def get_page(title: str, lang: str = "sk", max_chars: int = 20000) -> str:
    """Vráti celý text článku ako čistý text (bez HTML).

    Args:
        title: presný názov článku
        lang: jazyk Wikipédie
        max_chars: maximálna dĺžka vráteného textu
    """
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
        "titles": title,
        "format": "json",
        "utf8": 1,
    }
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT) as client:
        r = await client.get(f"{_base(lang)}/w/api.php", params=params)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})

    page = next(iter(pages.values()), {})
    if "missing" in page or not page.get("extract"):
        return f"Článok „{title}“ som nenašiel."
    text = page["extract"]
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... text skrátený ...]"
    return text


if __name__ == "__main__":
    # Na hostingu (Render a pod.) je nastavená premenná PORT -> server beží cez HTTP na /mcp.
    # Lokálne (Claude Desktop, Inspector) PORT nie je -> server beží cez stdio.
    port = os.environ.get("PORT")
    if port:
        mcp.run(transport="http", host="0.0.0.0", port=int(port))
    else:
        mcp.run()
