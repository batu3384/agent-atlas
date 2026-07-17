# Dev — GitHub

## Capabilities
- Repo search, view, issues via `gh`

## Prerequisites
- `gh` CLI; `gh auth login` for private repos / higher limits

## Doctor
- `github` → `ok` when `gh` works

## Commands

```bash
gh search repos "query" --sort stars --limit 10
gh repo view owner/repo
gh issue list -R owner/repo --limit 20
```

## Retry
1. Missing `gh` → install from https://cli.github.com
2. 401 / rate limit → `gh auth login`

## Fallback
`curl -s "https://r.jina.ai/https://github.com/owner/repo"` for public README

## Safety
Do not force-push or mutate remotes unless the user asks.
