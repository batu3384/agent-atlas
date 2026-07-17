# Web pages & RSS

## Jina Reader (any public URL)

```bash
curl -s "https://r.jina.ai/https://example.com"
```

Returns clean markdown. Prefer this for article/page reads.

## RSS / Atom

```bash
python -c "import feedparser; [print(e.title, e.link) for e in feedparser.parse('FEED_URL').entries[:10]]"
```

## Retry

1. Jina timeout → retry once; then open URL in browser / ask user
2. Paywalled / login-gated page → Tier 1 channel if platform matches (LinkedIn → career.md)
3. Never scrape HTML yourself when Jina works
