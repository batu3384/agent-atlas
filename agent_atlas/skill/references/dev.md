# Dev — GitHub

## Search & view

```bash
gh search repos "query" --sort stars --limit 10
gh repo view owner/repo
gh issue list -R owner/repo --limit 20
gh api repos/owner/repo/readme -H "Accept: application/vnd.github.raw"
```

## Auth

Public repos work without login. Private repos:

```bash
gh auth login
gh auth status
```

## Retry

1. `gh` missing → `brew install gh` / https://cli.github.com
2. Rate limit / 401 → `gh auth login`
3. Fallback for public README: `curl -s "https://r.jina.ai/https://github.com/owner/repo"`
