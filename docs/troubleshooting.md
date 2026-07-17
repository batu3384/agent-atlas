# Troubleshooting

Western channels only. Always start with:

```bash
agent-atlas doctor --json
agent-atlas smoke
```

Use each channel's `active_backend` from doctor.

---

## LinkedIn: doctor `off` or MCP tools fail

**Symptoms:** LinkedIn not `ok`; agent MCP tools missing / auth errors.

**Fix:**

```bash
uvx linkedin-scraper-mcp@latest --login
# Add linkedin-scraper-mcp to ~/.cursor/mcp.json  (docs/tier1.md)
# Or: mcporter config add linkedin http://localhost:8001/mcp
agent-atlas doctor --json   # expect active_backend=linkedin-mcp, status=ok
```

Public pages without login:

```bash
curl -s "https://r.jina.ai/https://www.linkedin.com/in/…"
```

---

## Twitter: `not_authenticated` / empty search

**Symptoms:** `twitter status` shows unauthenticated; doctor `warn`.

**Fix:**

1. Set `TWITTER_AUTH_TOKEN` + `TWITTER_CT0` (secondary account) — `docs/tier1.md`
2. Or use OpenCLI: Chrome + extension → `opencli doctor` → `opencli twitter search "q" -f yaml`
3. Fallback: Exa `site:x.com …` via mcporter

---

## Reddit: rdt needs login

**Symptoms:** doctor warns; `rdt search` fails.

**Fix:**

1. Log into Reddit in the Atlas Chrome profile (`twitter_chrome_profile`, often Profile 3)
2. Re-run `agent-atlas doctor` (cookie sync)
3. Fallback: `opencli reddit search "q" -f yaml` or Exa `site:reddit.com`

---

## OpenCLI: `BROWSER_CONNECT` / bridge down

**Symptoms:** Facebook/Instagram/Twitter OpenCLI path fails.

**Fix:**

1. Start Google Chrome
2. Enable OpenCLI extension; pin it
3. `opencli doctor` until connected
4. `agent-atlas configure opencli_profile atlas` if using a named profile

---

## Exa / mcporter broken

**Symptoms:** Exa channel `off` or `mcporter call` fails.

**Fix:**

```bash
npm i -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp
mcporter config list
agent-atlas install   # re-runs Exa config
```

---

## GitHub: `gh` missing or 401

```bash
brew install gh   # or https://cli.github.com
gh auth login
gh auth status
```

---

## YouTube: no subtitles

Some videos have no captions. Retry with `--write-auto-sub`. If still empty, tell the user — do not invent transcripts.

---

## Install / PATH

`agent-atlas: command not found`:

```bash
# ensure ~/.local/bin on PATH (uv tool / pipx)
uv tool install agent-atlas
# or until PyPI mirrors: uv tool install git+https://github.com/batu3384/agent-atlas.git
```

---

## Still stuck?

1. `agent-atlas doctor --json` → paste status to the agent
2. `docs/tier1.md` for login channels
3. Open a GitHub issue: https://github.com/batu3384/agent-atlas/issues
