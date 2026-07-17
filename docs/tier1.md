# Tier 1 — login channels

Twitter, Reddit, Facebook, Instagram, and LinkedIn need a **browser session** or cookies.
Agent Atlas does not scrape these itself — it routes to **OpenCLI** and/or **twitter-cli**.

## Security (read first)

| Rule | Why |
|------|-----|
| Use a **secondary account** | Cookie/API automation can trigger bans |
| Never commit cookies/tokens | Store only in `~/.agent-atlas/` or env vars (mode 600) |
| Prefer OpenCLI + Chrome login | Reuses your real browser session; no manual cookie export for most flows |
| Do not use sudo | Not required |

---

## Recommended path: OpenCLI (desktop)

Covers: **Reddit, Facebook, Instagram, Twitter (fallback)**. Not used for LinkedIn (see LinkedIn section).

### 1. Install CLI

```bash
# Node.js >= 20
npm install -g @jackwener/opencli
opencli --version
```

Or install [OpenCLIApp](https://opencli.info/download) (macOS/Windows) which manages the `opencli` binary.

### 2. Chrome Browser Bridge

1. Install the **OpenCLI** extension from the [Chrome Web Store](https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk)  
   (or load unpacked from [GitHub Releases](https://github.com/jackwener/opencli/releases))
2. Open Chrome and stay logged into the sites you need (Reddit, X, etc.) — **secondary accounts recommended**
3. Verify:

```bash
opencli doctor
```

### 3. Agent Atlas install helper

```bash
agent-atlas install --channels opencli
# or individually:
agent-atlas install --channels twitter,reddit,facebook,instagram
```

### 4. Example commands

```bash
opencli reddit search "query" -f yaml
opencli facebook search "query" -f yaml
opencli instagram search "query" -f yaml
opencli twitter search "query" -f yaml
```

Check `opencli list` for the exact adapter names on your version.

---

## Twitter preferred path: twitter-cli

```bash
uv tool install twitter-cli
# or: pipx install twitter-cli
```

Auth (Cookie-Editor / env — **secondary account**):

```bash
export TWITTER_AUTH_TOKEN="…"
export TWITTER_CT0="…"
twitter status   # expect ok: true
twitter search "query" -n 10
```

Optional: persist via Agent Atlas config (mode 600). `agent-atlas` loads these into the process env automatically (twitter-cli / OpenCLI):

```bash
agent-atlas configure twitter_chrome_profile "Profile 3"
agent-atlas configure twitter_browser chrome
agent-atlas configure opencli_profile atlas
agent-atlas configure twitter_auth_token "…"   # optional
agent-atlas configure twitter_ct0 "…"          # optional
```

Direct `twitter` / `opencli` in a bare shell still need the same vars exported (or rely on defaults).

---

## Reddit — rdt-cli (preferred)

Cookie CLI (like twitter-cli). **No live Chrome bridge required** after cookies are saved.

```bash
uv tool install rdt-cli
```

1. Log into Reddit in your **Atlas Chrome profile** (`Profile 3`)
2. `agent-atlas doctor` syncs cookies automatically (uses `twitter_chrome_profile` from config)
3. Or manually: `rdt login`

```bash
rdt status
rdt search "query" -n 10 --compact --yaml
```

Optional config (defaults to Twitter profile keys):

```bash
agent-atlas configure reddit_chrome_profile "Profile 3"
```

### OpenCLI fallback

If rdt-cli is not authenticated but OpenCLI bridge is connected:

```bash
opencli reddit search "query" -f yaml
```

---

## LinkedIn — linkedin-mcp → Jina (Reach-style)

Same stack as [Agent Reach](https://github.com/Panniantong/Agent-Reach): authenticated research via [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server); public pages via Jina.

### 1. Login (once)

```bash
uvx linkedin-scraper-mcp@latest --login
```

A browser window opens — sign in with a **secondary** LinkedIn account. Session is stored under `~/.linkedin-mcp/`.

### 2. Register MCP

Cursor `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "uvx",
      "args": ["linkedin-scraper-mcp@latest"],
      "env": { "UV_HTTP_TIMEOUT": "300" }
    }
  }
}
```

Optional (Reach/mcporter HTTP):

```bash
uvx linkedin-scraper-mcp@latest --transport streamable-http --port 8001
mcporter config add linkedin http://localhost:8001/mcp
```

### 3. Use

From the agent: MCP tools (`search_people`, `get_person_profile`, `search_jobs`, …).

Public page (no login):

```bash
curl -s "https://r.jina.ai/https://www.linkedin.com/in/…"
```

`agent-atlas doctor` shows `linkedin-mcp` as **warn** when MCP config is present (session lives in the MCP host). Without MCP, doctor falls back to **Jina Reader** for public pages.

---

## Doctor status meanings (Tier 1)

| Status | Meaning |
|--------|---------|
| `ok` | Tool installed **and** session/bridge ready |
| `warn` | Tool installed, login/bridge still needed |
| `off` | Tool not installed |
| `error` | Tool broken |

```bash
agent-atlas doctor
agent-atlas doctor --json
```

---

## Uninstall Tier 1 tools

```bash
npm uninstall -g @jackwener/opencli
pipx uninstall twitter-cli
# Remove Chrome extension manually
```
