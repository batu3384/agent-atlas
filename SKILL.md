---
name: agent-atlas
description: >
  Use when the user wants to search, research, look up, or read content on the
  open web — research a topic, search the web, read a URL, YouTube transcript,
  GitHub, RSS, Twitter/X, Reddit, or LinkedIn.

  10 Western platforms. Run `agent-atlas doctor --json` for active backends.

  NOT for: writing posts; China-only platforms (Bilibili, Xiaohongshu…);
  topics that already have a dedicated specialized skill.
metadata:
  homepage: https://github.com/batu3384/agent-atlas
---

# Agent Atlas — open-web research router

Installer + doctor + route. **Call upstream tools directly** after `agent-atlas doctor --json`.

## Standing rules

1. Multi-platform → `agent-atlas doctor --json` → use each channel's `active_backend`.
2. Optional sanity: `agent-atlas smoke`.
3. Say which channel/backend you use.
4. Temp → `/tmp/`. Config → `~/.agent-atlas/`. Don't pollute the project tree.
5. Prefer Tier 0 first; ask before installing Tier 1 login tools.

## Routing order (default)

When the user asks to **research a topic**, try in this order (skip warn/off):

1. **Exa** — broad web search  
2. **Twitter** — recent public chatter  
3. **Reddit** — discussion threads (needs OpenCLI bridge)  
4. **GitHub** — code/repos if relevant  
5. **YouTube / RSS / web(Jina)** — deepen specific URLs  

Stop early when you have enough signal. Don't fan out to every channel by default.

## Tier 0 commands

```bash
curl -s "https://r.jina.ai/URL"
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
gh search repos "query" --sort stars --limit 10
gh repo view owner/repo
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"
python -c "import feedparser; print(feedparser.parse('FEED_URL').entries[:5])"
```

## Tier 1 (login)

FB/IG often disabled via `disabled_channels`. Twitter → twitter-cli. Reddit/LinkedIn → OpenCLI.

`agent-atlas` loads `~/.agent-atlas/config.yaml` into env automatically. Bare shell:

```bash
agent-atlas configure twitter_chrome_profile "Profile 3"
agent-atlas configure opencli_profile atlas
twitter search "query" -n 10
opencli reddit search "query" -f yaml
opencli linkedin search "query" -f yaml
```

## Docs

`docs/install.md` · `docs/tier1.md` · `docs/platforms.md` · `docs/update.md`
