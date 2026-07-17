# Channel contract

Authoritative status semantics for `agent-atlas doctor` / `smoke`. Prefer this over older notes.

## Status meanings

| Status | Meaning | Smoke |
|--------|---------|-------|
| `ok` | Probe passed — research ready | Runs |
| `warn` | Installed but login/config incomplete; fallback may work | Skip (exception: LinkedIn + Jina) |
| `off` | Missing or `disabled_channels` | Skip |
| `error` | Tool broken | Skip |

`active_backend` is the backend doctor selected. Agents must call that tool, not invent scrapers.

## Channels

| Channel | Tier | Backends (order) | Auth | Smoke |
|---------|------|------------------|------|-------|
| web | 0 | Jina Reader | None | curl Jina |
| exa | 0 | mcporter + Exa | None (free MCP) | mcporter call |
| youtube | 0 | yt-dlp | None | yt-dlp print |
| github | 0 | gh | Optional (`gh auth`) | `gh repo view` |
| rss | 0 | feedparser | None | parse feed via `sys.executable` |
| twitter | 1 | twitter-cli → OpenCLI | Tokens / bridge | search |
| reddit | 1 | rdt-cli → OpenCLI | Cookies / bridge | search |
| facebook | 1 | OpenCLI | Bridge (often disabled) | opencli search |
| instagram | 1 | OpenCLI | Bridge (often disabled) | opencli search |
| linkedin | 1 | linkedin-mcp → Jina | MCP login / public | MCP configured → pass; else Jina public company page |

## LinkedIn notes

- `ok` + `linkedin-mcp` = MCP configured (mcporter list entry `linkedin` **or** Cursor/Claude config with `linkedin-scraper-mcp`). Session is used when the agent calls MCP tools.
- `warn` + `Jina Reader` = public pages only.
- If mcporter is broken but Jina works → `warn` + Jina (MCP failure noted in message).

## Agent usage

```bash
agent-atlas doctor --json
# pick active_backend per channel, then run upstream CLI / MCP tools
agent-atlas smoke
```

See also: [platforms.md](platforms.md) · [tier1.md](tier1.md) · [troubleshooting.md](troubleshooting.md)
