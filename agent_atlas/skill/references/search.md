# Search (Exa via mcporter)

## Primary

```bash
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
```

Free Exa MCP endpoint — configured by `agent-atlas install`.

## Site-scoped fallback

When a login CLI is down, search the open web with a site filter:

```bash
mcporter call 'exa.web_search_exa(query: "site:x.com topic", numResults: 5)'
mcporter call 'exa.web_search_exa(query: "site:reddit.com topic", numResults: 5)'
mcporter call 'exa.web_search_exa(query: "site:linkedin.com topic", numResults: 5)'
```

## Retry

1. `mcporter` missing → `npm i -g mcporter` then `agent-atlas install`
2. Exa not in config → `mcporter config add exa https://mcp.exa.ai/mcp`
3. Call fails → check `mcporter config list`; see `docs/troubleshooting.md`
