# Agent Atlas

> Search and research the open web for your AI agent.

Agent Atlas is a **capability layer**: it installs, health-checks, and routes free upstream tools so your AI agent can research the web. It is **not** a scraper wrapper — after install, the agent calls upstream CLIs/APIs directly.

**10 Western channels.** No China-only platforms.

> Not the same as other GitHub projects named “AgentAtlas” (e.g. browser schema registries). This repo is an **open-web research installer + router** for AI coding agents.

| Tier | Channels |
|------|----------|
| **0 — zero config** | Web (Jina), Search (Exa+mcporter), YouTube (yt-dlp), GitHub (gh), RSS (feedparser) |
| **1 — login** | Twitter/X, Reddit, Facebook, Instagram, LinkedIn |

## Quick start (for humans)

Tell your AI agent:

```
Install Agent Atlas using docs/install.md in this repo.
```

Or from PyPI:

```bash
pip install agent-atlas
agent-atlas install
agent-atlas doctor
```

Or from this repo:

```bash
cd ~/Documents/agent-atlas   # or clone path
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
agent-atlas install
agent-atlas doctor
```

## Commands

```bash
agent-atlas doctor          # human report
agent-atlas doctor --json   # for agents
agent-atlas smoke           # one real call per ready channel
agent-atlas smoke --json
agent-atlas install         # Tier 0 tools + SKILL.md
agent-atlas install --safe  # print needs only
agent-atlas skill --install
agent-atlas uninstall
```

## Design

- Config: `~/.agent-atlas/` (mode 600)
- Temp: `/tmp/`
- Skill: agentskills.io `SKILL.md` → `~/.agents/skills/agent-atlas/`
- Inspiration: Agent Reach’s installer/doctor model — different product, English-first, Western-only scope

## License

MIT — see [LICENSE](LICENSE). Upstream tools keep their own licenses.

## Credits (upstream)

[Jina Reader](https://github.com/jina-ai/reader) · [Exa](https://exa.ai) · [mcporter](https://github.com/nicobailon/mcporter) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [GitHub CLI](https://cli.github.com) · [feedparser](https://github.com/kurtmckee/feedparser) · [OpenCLI](https://github.com/jackwener/opencli) · [twitter-cli](https://github.com/public-clis/twitter-cli)
