# Platforms

Agent Atlas routes to these upstream tools. Prefer `agent-atlas doctor --json` → `active_backend`.

## Tier 0

| Channel | Backend | Example |
|---------|---------|---------|
| **web** | Jina Reader | `curl -s "https://r.jina.ai/https://example.com"` |
| **exa** | mcporter + Exa | `mcporter call 'exa.web_search_exa(query: "…", numResults: 5)'` |
| **youtube** | yt-dlp | `yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"` |
| **github** | gh | `gh repo view owner/repo` · `gh search repos "q"` |
| **rss** | feedparser | `python -c "import feedparser; …"` |

## Tier 1

Full setup: [tier1.md](tier1.md)

| Channel | Backend order | Example |
|---------|---------------|---------|
| **twitter** | twitter-cli → OpenCLI | `twitter search "q" -n 10` · `opencli twitter search "q" -f yaml` |
| **reddit** | OpenCLI → rdt-cli | `opencli reddit search "q" -f yaml` |
| **facebook** | OpenCLI | `opencli facebook search "q" -f yaml` |
| **instagram** | OpenCLI | `opencli instagram search "q" -f yaml` |
| **linkedin** | OpenCLI → Jina | `curl -s "https://r.jina.ai/https://www.linkedin.com/…"` |

Doctor statuses: `ok` = session ready · `warn` = installed, login needed · `off` = not installed.

## Out of scope

Bilibili, Xiaohongshu, V2EX, Xueqiu, Xiaoyuzhou — not supported by design.
