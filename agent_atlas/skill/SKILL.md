---
name: agent-atlas
description: >
  Use when the user wants to search, research, look up, or read content on the
  open web — e.g. research a topic, search the web, read a URL, YouTube
  transcript, GitHub repo/issues, RSS feed, Twitter/X, Reddit, Facebook,
  Instagram, or LinkedIn.

  10 Western platforms. Multi-backend routing. Zero-config for web, Exa search,
  YouTube, GitHub, RSS. Login for Twitter/Reddit/Facebook/Instagram/LinkedIn.

  Run `agent-atlas doctor --json` to see which backend is active per channel.

  NOT for: writing posts/comments; China-only platforms (Bilibili, Xiaohongshu…);
  content that already has a dedicated specialized skill.
metadata:
  homepage: https://github.com/batu3384/agent-atlas
---

# Agent Atlas — open-web research router

Installer + doctor + routing. **You call upstream tools directly** after checking `agent-atlas doctor --json`.

## Standing rules

1. Before multi-platform work, run `agent-atlas doctor --json` and use each channel's `active_backend`.
2. Optional: `agent-atlas smoke` to verify real research calls still work.
3. Say which channel/backend you are using.
4. Temp files → `/tmp/`. Config → `~/.agent-atlas/`. Do not pollute the project workspace.
5. Prefer Tier 0 tools first; ask before installing Tier 1 login tools.

## Zero-config commands

```bash
# Web page → clean markdown
curl -s "https://r.jina.ai/URL"

# Web search (Exa via mcporter)
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'

# GitHub
gh search repos "query" --sort stars --limit 10
gh repo view owner/repo

# YouTube subtitles
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# RSS (Python)
python -c "import feedparser; print(feedparser.parse('FEED_URL').entries[:5])"
```

## Login channels (Tier 1)

This install disables **Facebook** and **Instagram** (`disabled_channels`).
**Twitter** → twitter-cli (cookie/token). **Reddit** → rdt-cli (Chrome closed OK).
**LinkedIn** → OpenCLI (Chrome open + bridge + linkedin.com feed). Headless `li-cli` is experimental — LinkedIn rejects cookie replay.

`agent-atlas` reads `~/.agent-atlas/config.yaml` into env (`TWITTER_*`, `LI_*`, `OPENCLI_PROFILE`).
Reddit/LinkedIn cookie sync uses `twitter_chrome_profile` (or per-channel override) on doctor.

```bash
agent-atlas configure twitter_chrome_profile "Profile 3"
agent-atlas configure opencli_profile atlas
```

```bash
twitter search "query" -n 10
rdt search "query" -n 10 --compact --yaml
opencli linkedin people-search "query" -f yaml
```

Do **not** use Facebook/Instagram adapters unless the user re-enables them.

## Install / update

```
Install: docs/install.md · Tier 1: docs/tier1.md · Update: docs/update.md
```

## Platform details

See `docs/platforms.md` after skill sync.
