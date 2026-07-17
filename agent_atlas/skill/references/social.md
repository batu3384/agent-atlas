# Social — Twitter / Reddit / Facebook / Instagram

## Capabilities
- Search / read posts on Twitter, Reddit; OpenCLI for Meta (often disabled)

## Prerequisites
- Run `agent-atlas doctor --json` first; use `active_backend`
- Secondary accounts; Facebook/Instagram often in `disabled_channels`

## Doctor
- `ok` → use that backend’s commands
- `warn` → login / bridge needed (`docs/tier1.md`)

## Commands

### Twitter

```bash
twitter status
twitter search "query" -n 10
opencli twitter search "query" -f yaml
```

### Reddit

```bash
rdt search "query" -n 10 --compact --yaml
opencli reddit search "query" -f yaml
```

### Facebook / Instagram (if enabled)

```bash
opencli facebook search "query" -f yaml
opencli instagram search "query" -f yaml
```

## Retry
1. twitter-cli unauthenticated → OpenCLI or set `TWITTER_*` tokens
2. OpenCLI `BROWSER_CONNECT` → Chrome + extension → `opencli doctor`
3. Both fail → Exa `site:…` ([search.md](search.md))

## Fallback
Exa site search; tell user when login is required.

## Safety
Secondary accounts only. Never commit cookies/tokens.
