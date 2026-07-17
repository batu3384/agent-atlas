# Social — Twitter / Reddit / Facebook / Instagram

Run `agent-atlas doctor --json` first. Use `active_backend` for each channel.

Facebook and Instagram are often in `disabled_channels` — do not use unless the user re-enabled them.

## Twitter / X

### Backend A: twitter-cli (preferred when authenticated)

```bash
twitter status
twitter search "query" -n 10
twitter tweet URL_OR_ID
```

Auth: `TWITTER_AUTH_TOKEN` + `TWITTER_CT0` (secondary account).  
Config: `agent-atlas configure` → env via `apply_runtime_env`.

### Backend B: OpenCLI

```bash
opencli twitter search "query" -f yaml
```

Requires Chrome + OpenCLI bridge extension (`opencli doctor`).

### Retry

1. twitter-cli `not_authenticated` → OpenCLI or set tokens (`docs/tier1.md`)
2. OpenCLI `BROWSER_CONNECT` → start Chrome + extension
3. Both fail → Exa `site:x.com` ([search.md](search.md))

## Reddit

### Backend A: rdt-cli

```bash
rdt search "query" -n 10 --compact --yaml
```

Cookie sync uses `twitter_chrome_profile` (Atlas Chrome profile) on doctor.

### Backend B: OpenCLI

```bash
opencli reddit search "query" -f yaml
```

### Retry

1. rdt needs login → log into Reddit in Atlas Chrome profile, re-run doctor
2. Fall back to OpenCLI, then Exa `site:reddit.com`

## Facebook / Instagram (OpenCLI only)

```bash
opencli facebook search "query" -f yaml
opencli instagram search "query" -f yaml
```

Only if removed from `disabled_channels`.
