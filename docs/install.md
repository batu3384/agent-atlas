# Agent Atlas — Installation Guide

## For humans

Copy this to your AI agent:

```
Install Agent Atlas from this repo: read docs/install.md and run the steps.
```

Safe mode:

```
Install Agent Atlas in safe mode (agent-atlas install --safe).
```

---

## For AI agents

### Goal

Install Agent Atlas and Tier 0 upstream tools so the user can search and research the open web. After install, **call upstream tools directly** (do not invent scrapers).

### Boundaries

- Do **not** use `sudo` unless the user approved
- Do **not** write into the project workspace — use `~/.agent-atlas/` and `/tmp/`
- Do **not** install packages not listed here without asking
- Prefer `pipx` or a venv for Python tools

### Step 1 — Install the package

Preferred (PyPI):

```bash
pip install agent-atlas
```

Or from a clone:

```bash
cd /path/to/agent-atlas
python3 -m venv ~/.agent-atlas-venv
source ~/.agent-atlas-venv/bin/activate
pip install -e .
```

Or from the repo directory with an existing venv:

```bash
pip install -e .
```

### Step 2 — Run installer

```bash
agent-atlas install
# or preview:
agent-atlas install --dry-run
agent-atlas install --safe
```

This will:

1. Ensure `yt-dlp` is available
2. Check `gh` and Node/npm
3. Install `mcporter` if npm is available
4. Register `SKILL.md` under `~/.agents/skills/agent-atlas/` (and common agent dirs)

### Step 3 — Exa search (mcporter)

`agent-atlas install` runs:

```bash
mcporter config add exa https://mcp.exa.ai/mcp --scope home
mcporter config add exa https://mcp.exa.ai/mcp --scope project
```

Hosted Exa MCP — no API key required for the free MCP path.

Verify:

```bash
mcporter list exa
mcporter call 'exa.web_search_exa(query: "test", numResults: 2)'
agent-atlas doctor --json
```

### Step 4 — Optional Tier 1

**Ask the user first.** Use secondary accounts. Details: [tier1.md](tier1.md).

```bash
# OpenCLI covers Reddit / Facebook / Instagram / Twitter fallback / LinkedIn adapter
agent-atlas install --channels opencli

# Twitter preferred CLI
agent-atlas install --channels twitter

# Everything Tier 1 helpers
agent-atlas install --channels all
```

Then:

1. Install OpenCLI Chrome bridge extension
2. Log into sites in Chrome (secondary accounts)
3. `opencli doctor`
4. `agent-atlas doctor --json`

| Channel | Tool |
|---------|------|
| Twitter | `twitter-cli` and/or OpenCLI |
| Reddit / Facebook / Instagram | OpenCLI + Chrome |
| LinkedIn | Jina public pages and/or OpenCLI |

**Warning:** Cookie/login automation can risk account bans — use secondary accounts.

### Step 5 — Verify

```bash
agent-atlas doctor
agent-atlas doctor --json
agent-atlas smoke
agent-atlas smoke --json
```

### Uninstall

```bash
agent-atlas uninstall
pip uninstall agent-atlas
```
