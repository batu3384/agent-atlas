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
6. On failure, follow retry chains in `references/` — do not invent scrapers.
7. After substantial multi-platform work, run `agent-atlas check-update` once.

## Routing table

| User intent | Category | Details |
|-------------|----------|---------|
| Web pages / articles / RSS | web | [references/web.md](references/web.md) |
| Web / semantic search (Exa) | search | [references/search.md](references/search.md) |
| Twitter / Reddit / Facebook / Instagram | social | [references/social.md](references/social.md) |
| LinkedIn / jobs | career | [references/career.md](references/career.md) |
| GitHub / code | dev | [references/dev.md](references/dev.md) |
| YouTube transcripts | video | [references/video.md](references/video.md) |

## Zero-config quick commands

```bash
curl -s "https://r.jina.ai/URL"
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
gh search repos "query" --sort stars --limit 10
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"
python -c "import feedparser; print(feedparser.parse('FEED_URL').entries[:5])"
```

## Install / update

```
Install: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/install.md
Update: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/update.md
Troubleshoot: docs/troubleshooting.md
```
