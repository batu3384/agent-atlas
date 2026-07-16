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

Covers: **Reddit, Facebook, Instagram, Twitter (fallback), LinkedIn (if adapter present)**.

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
agent-atlas install --channels twitter,reddit,facebook,instagram,linkedin
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

## Reddit alternative: rdt-cli

If not using OpenCLI:

```bash
# see https://github.com/public-clis/rdt-cli
rdt search "query" --limit 10
```

Requires Reddit cookies; OpenCLI is preferred on desktop.

---

## LinkedIn

| Mode | How |
|------|-----|
| Public page read | `curl -s "https://r.jina.ai/https://www.linkedin.com/in/…"` |
| Richer / logged-in | OpenCLI adapter if listed in `opencli list`, or linkedin-mcp |

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
