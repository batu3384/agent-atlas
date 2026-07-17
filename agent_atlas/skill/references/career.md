# Career — LinkedIn

Reach-style stack: **linkedin-scraper-mcp → Jina**.

Check `agent-atlas doctor --json` → `linkedin.active_backend`.

## Backend A: linkedin-mcp (`ok` when configured)

One-time login:

```bash
uvx linkedin-scraper-mcp@latest --login
```

Cursor `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "uvx",
      "args": ["linkedin-scraper-mcp@latest"],
      "env": { "UV_HTTP_TIMEOUT": "300" }
    }
  }
}
```

Or mcporter HTTP (Reach-style):

```bash
uvx linkedin-scraper-mcp@latest --transport streamable-http --port 8001
mcporter config add linkedin http://localhost:8001/mcp
```

Then use **agent MCP tools**: `search_people`, `get_person_profile`, `search_jobs`, …

## Backend B: Jina (public pages)

```bash
curl -s "https://r.jina.ai/https://www.linkedin.com/in/…"
```

Doctor shows `warn` + `Jina Reader` when MCP is not configured.

## Retry

1. Doctor `off` / MCP missing → run `--login` + add MCP config (`docs/tier1.md`)
2. MCP tools fail → confirm login profile under `~/.linkedin-mcp/`; re-login
3. Public URL only → Jina
4. See `docs/troubleshooting.md`
