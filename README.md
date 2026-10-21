# wiki-mcp

Učebný MCP server pre Wikipédiu. Dáva Claudovi tri nástroje:

| Nástroj | Čo robí |
| --- | --- |
| `search_wiki(query, lang="sk", limit=5)` | vyhľadá články |
| `get_summary(title, lang="sk")` | krátke zhrnutie a odkaz |
| `get_page(title, lang="sk", max_chars=20000)` | celý text článku |

Pred spustením doplň do `HEADERS` v `server.py` svoj email (Wikipédia vyžaduje User-Agent s kontaktom).

## Lokálne spustenie

```bash
uv sync                 # nainštaluje závislosti
uv run server.py        # spustí server cez stdio
```

Test v MCP Inspectore (potrebuje Node.js):

```bash
npx @modelcontextprotocol/inspector uv run server.py
```

## Claude Desktop

Do `claude_desktop_config.json` (Settings → Developer → Edit Config) pridaj:

```json
{
  "mcpServers": {
    "wikipedia": {
      "command": "uv",
      "args": ["--directory", "C:\\cesta\\k\\wiki-mcp", "run", "server.py"]
    }
  }
}
```

Potom Claude Desktop úplne ukonči a spusti znova.

## Nasadenie na Render (pre claude.ai)

Ak je nastavená premenná `PORT`, server sa sám prepne na HTTP a počúva na `/mcp`.

1. render.com → New → Web Service → vyber tento repozitár
2. Build command: `pip install -r requirements.txt`
3. Start command: `python server.py`
4. Instance type: Free
5. V claude.ai: Settings → Connectors → Add custom connector → `https://<tvoja-adresa>.onrender.com/mcp`

Server nemá prihlásenie, takže ho môže volať ktokoľvek s adresou. Pri verejných dátach z Wikipédie to nevadí.
