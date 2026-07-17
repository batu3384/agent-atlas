# Web pages & RSS

## Capabilities
- Read any public URL as clean markdown
- Parse RSS / Atom feeds

## Prerequisites
- Network access; `curl` for Jina; Python + `feedparser` (bundled with agent-atlas)

## Doctor
- `web` → usually `ok` (Jina)
- `rss` → `ok` when feedparser import works

## Commands

```bash
curl -s "https://r.jina.ai/https://example.com"
python -c "import feedparser; [print(e.title, e.link) for e in feedparser.parse('FEED_URL').entries[:10]]"
```

## Retry
1. Jina timeout → retry once
2. Paywalled page → matching Tier 1 channel if any

## Fallback
Open URL in browser / ask user — do not invent HTML scrapers.

## Safety
Temp files → `/tmp/`. Do not write into the project workspace.
