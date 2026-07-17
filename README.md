# Agent Atlas

> Search and research the open web for your AI agent.

Agent Atlas is a **capability layer**: it installs, health-checks, and routes free upstream tools so your AI coding agent can research the web. It is **not** a scraper framework — after setup, the agent calls upstream CLIs/APIs directly.

**10 Western channels.** No China-only platforms. English-first docs · [Türkçe](docs/README_tr.md).

> Not the same as other GitHub projects named “AgentAtlas” (e.g. browser schema registries). This repo is an **open-web research installer + router** for AI coding agents.

---

## What it does

| Capability | Description |
|------------|-------------|
| **Install** | Sets up Tier 0 tools (+ optional Tier 1 CLIs) and registers `SKILL.md` for Cursor / Claude Code / agents |
| **Doctor** | Per-channel health: `ok` / `warn` / `off` + `active_backend` (JSON for agents) |
| **Smoke** | One real research call per ready channel — proves end-to-end wiring |
| **Config** | `~/.agent-atlas/config.yaml` → runtime env (`TWITTER_*`, `LI_*`, `OPENCLI_PROFILE`, …) |
| **Routing** | Prefer Tier 0; Tier 1 uses cookie CLIs first, OpenCLI bridge when needed |

---

## Channels & tools

### Tier 0 — zero config (after install)

| Channel | Tool | What you get |
|---------|------|----------------|
| **web** | [Jina Reader](https://github.com/jina-ai/reader) | URL → clean markdown |
| **exa** | [Exa](https://exa.ai) via [mcporter](https://github.com/nicobailon/mcporter) | Web search for agents |
| **youtube** | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Transcripts / metadata (no download required) |
| **github** | [GitHub CLI](https://cli.github.com) (`gh`) | Repos, issues, search |
| **rss** | [feedparser](https://github.com/kurtmckee/feedparser) | RSS / Atom feeds |

### Tier 1 — login / session

| Channel | Backend order | Notes |
|---------|---------------|-------|
| **twitter** | [twitter-cli](https://github.com/public-clis/twitter-cli) → [OpenCLI](https://github.com/jackwener/opencli) | Tokens / cookies |
| **reddit** | [rdt-cli](https://pypi.org/project/rdt-cli/) → OpenCLI | Cookies from Atlas Chrome profile on doctor |
| **linkedin** | [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server) → Jina | Reach-style: `uvx … --login` + MCP / mcporter |
| **facebook** | OpenCLI | Often disabled via `disabled_channels` |
| **instagram** | OpenCLI | Often disabled via `disabled_channels` |

Full command examples: [docs/platforms.md](docs/platforms.md) · Tier 1 setup: [docs/tier1.md](docs/tier1.md)

---

## Quick start

Tell your AI agent:

```
Install Agent Atlas: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/install.md
```

Or manually:

```bash
uv tool install agent-atlas
# fallback: uv tool install git+https://github.com/batu3384/agent-atlas.git
# ensure ~/.local/bin is on PATH
agent-atlas install
agent-atlas doctor
agent-atlas smoke
```

From a clone:

```bash
git clone https://github.com/batu3384/agent-atlas.git
cd agent-atlas
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
agent-atlas install
agent-atlas doctor
```

Tier 1 (optional):

```bash
agent-atlas install --channels twitter,reddit,linkedin,opencli
agent-atlas configure twitter_chrome_profile "Profile 3"
agent-atlas configure opencli_profile atlas
```

Ensure `~/.local/bin` is on your `PATH` if you use `uv tool install` for `agent-atlas`, `rdt`, or `li`.

---

## CLI

```bash
agent-atlas doctor          # human report
agent-atlas doctor --json   # for agents — use active_backend per channel
agent-atlas smoke           # one real call per ready channel
agent-atlas smoke --json
agent-atlas watch           # quick health + update hint
agent-atlas check-update
agent-atlas install         # Tier 0 + SKILL.md
agent-atlas install --channels twitter,reddit,linkedin,opencli,all
agent-atlas install --safe  # print needs only
agent-atlas configure KEY VALUE
agent-atlas skill --install
agent-atlas uninstall
```

---

## Example research (after doctor is green)

```bash
# Tier 0
curl -s "https://r.jina.ai/https://example.com"
mcporter call 'exa.web_search_exa(query: "AI agents 2026", numResults: 5)'
gh search repos "AI agent" --sort stars --limit 5
yt-dlp --flat-playlist --print "%(title)s" "ytsearch3:AI agents"
python3 -c "import feedparser; print([e.title for e in feedparser.parse('https://hnrss.org/frontpage').entries[:5]])"

# Tier 1
twitter search "AI agents" -n 10
rdt search "AI agents" -n 10 --compact --yaml
# LinkedIn: agent MCP tools after `uvx linkedin-scraper-mcp@latest --login`
curl -s "https://r.jina.ai/https://www.linkedin.com/in/…"
```

---

## Design

- **Config:** `~/.agent-atlas/config.yaml` (mode 600)
- **Temp:** `/tmp/` — do not pollute the project tree
- **Skill:** agentskills.io `SKILL.md` → `~/.agents/skills/agent-atlas/`
- **Doctor statuses:** `ok` = ready · `warn` = installed, login needed · `off` = missing/disabled
- Inspiration: Agent Reach’s installer/doctor model — different product, English-first, Western-only scope

---

## Docs

| Doc | Contents |
|-----|----------|
| [docs/install.md](docs/install.md) | Install for agents & humans |
| [docs/tier1.md](docs/tier1.md) | Twitter / Reddit / LinkedIn / OpenCLI / MCP |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Common failures & fixes |
| [docs/platforms.md](docs/platforms.md) | Backend order + examples |
| [docs/update.md](docs/update.md) | Update path |
| [docs/README_tr.md](docs/README_tr.md) | Türkçe özet |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |
| [SECURITY.md](SECURITY.md) | Credentials & reporting |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Dev setup / PR guide |
| [SKILL.md](SKILL.md) | Agent skill (routing rules) |
| [PLAN.md](PLAN.md) | Project plan / status |

---

## License

MIT — see [LICENSE](LICENSE). Upstream tools keep their own licenses.

## Credits (upstream)

[Jina Reader](https://github.com/jina-ai/reader) · [Exa](https://exa.ai) · [mcporter](https://github.com/nicobailon/mcporter) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [GitHub CLI](https://cli.github.com) · [feedparser](https://github.com/kurtmckee/feedparser) · [OpenCLI](https://github.com/jackwener/opencli) · [twitter-cli](https://github.com/public-clis/twitter-cli) · [rdt-cli](https://pypi.org/project/rdt-cli/) · [linkedin-scraper-mcp](https://github.com/stickerdaniel/linkedin-mcp-server)
