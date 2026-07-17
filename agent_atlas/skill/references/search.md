# Search (Exa via mcporter)

## Capabilities
- Semantic web search (Exa MCP, free hosted endpoint)

## Prerequisites
- `mcporter` + Exa config (`agent-atlas install` adds it)

## Doctor
- `exa` → `ok` when mcporter + Exa registered

## Commands

```bash
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
mcporter call 'exa.web_search_exa(query: "site:x.com topic", numResults: 5)'
```

## Retry
1. `mcporter` missing → `npm i -g mcporter`
2. Exa absent → `mcporter config add exa https://mcp.exa.ai/mcp`

## Fallback
Site-scoped Exa when a login CLI is down (Twitter/Reddit/LinkedIn).

## Safety
No API key required for the default Exa MCP endpoint.
