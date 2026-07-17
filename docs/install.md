# Agent Atlas — Installation Guide

## For humans

Copy this to your AI agent:

```
Install Agent Atlas: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/install.md
```

Safe mode:

```
Install Agent Atlas (safe mode): https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/install.md
Use: agent-atlas install --safe
```

Update:

```
Update Agent Atlas: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/update.md
```

---

## For AI agents

### Goal

Install Agent Atlas and Tier 0 upstream tools so the user can search and research the **Western** open web. After install, **call upstream tools directly** (do not invent scrapers). Agent Atlas is installer + doctor + router — never a content proxy.

### Boundaries

- Do **not** use `sudo` unless the user approved
- Do **not** write into the project workspace — use `~/.agent-atlas/` and `/tmp/`
- Do **not** install packages not listed here without asking
- Prefer `pipx` or `uv tool` for the CLI; venv is fine too

### Directory rules

| Purpose | Path |
|---------|------|
| Config | `~/.agent-atlas/config.yaml` (mode 600) |
| Temp | `/tmp/` |
| Skills | `~/.agents/skills/agent-atlas/` (and common agent dirs) |
| LinkedIn MCP session | `~/.linkedin-mcp/` (linkedin-scraper-mcp) |
| rdt-cli creds | `~/.config/rdt-cli/` |

### Step 1 — Install the package

PyPI package **`agent-atlas-cli`** is published (CLI binary: `agent-atlas`). Git install remains a fallback.

```bash
# Recommended (PyPI)
uv tool install agent-atlas-cli
# or
pipx install agent-atlas-cli
# or
pip install agent-atlas-cli

# Fallback (git)
uv tool install git+https://github.com/batu3384/agent-atlas.git
# or
pipx install git+https://github.com/batu3384/agent-atlas.git

# Or venv from a clone
git clone https://github.com/batu3384/agent-atlas.git
cd agent-atlas
python3 -m venv ~/.agent-atlas-venv
source ~/.agent-atlas-venv/bin/activate
pip install -e .
```

Ensure `~/.local/bin` is on `PATH` when using `uv tool` / `pipx`. Verify:

```bash
command -v agent-atlas
agent-atlas --version
```

**Maintainers — publish a release:** create a GitHub Release; `.github/workflows/publish.yml` uploads to PyPI as **`agent-atlas-cli`** via Trusted Publishing.

### Step 2 — Run installer

```bash
agent-atlas install
# preview only (no config dir, no skill install, no package installs):
agent-atlas install --safe
agent-atlas install --dry-run
```

`--safe` / `--dry-run` print what is needed without mutating the system (except reading PATH).

This will:

1. Ensure `yt-dlp` is available
2. Check `gh` and Node/npm
3. Install `mcporter` if npm is available
4. Configure Exa MCP (free hosted path)
5. Register `SKILL.md` under agent skill dirs

### Step 3 — Verify Tier 0

```bash
mcporter call 'exa.web_search_exa(query: "test", numResults: 2)'
agent-atlas doctor --json
agent-atlas smoke
```

### Step 4 — Optional Tier 1

**Ask the user first.** Use **secondary accounts**. Details: [tier1.md](tier1.md).

Present roughly:

> Tier 0 is ready (web, Exa, YouTube, GitHub, RSS). Optional login channels:
> - **Twitter** — twitter-cli (tokens/cookies)
> - **Reddit** — rdt-cli (cookie sync from Chrome profile)
> - **LinkedIn** — linkedin-scraper-mcp (Reach-style) + Jina for public pages
> - **OpenCLI** — Chrome bridge (FB/IG + Twitter/Reddit fallback)
>
> Which ones do you want? (e.g. `twitter,reddit,linkedin,opencli` or `all`)

```bash
agent-atlas install --channels opencli,twitter,reddit,linkedin
# or
agent-atlas install --channels all
```

Then:

1. Twitter/Reddit: secondary accounts + `docs/tier1.md`
2. LinkedIn: `uvx linkedin-scraper-mcp@latest --login` + MCP config (`docs/tier1.md`)
3. OpenCLI (if needed): extension + `opencli doctor`
4. `agent-atlas configure twitter_chrome_profile "Profile 3"` (Reddit cookie sync)
5. `agent-atlas doctor` / `agent-atlas smoke`

**Warning:** Cookie/login automation can risk bans — use secondary accounts.

### Step 5 — Ongoing health

```bash
agent-atlas doctor
agent-atlas smoke
agent-atlas watch          # quick doctor + update hint
agent-atlas check-update
```

### Uninstall

```bash
agent-atlas uninstall              # skills + config
agent-atlas uninstall --keep-config
agent-atlas uninstall --dry-run
pipx uninstall agent-atlas-cli         # or: uv tool uninstall agent-atlas-cli
```
