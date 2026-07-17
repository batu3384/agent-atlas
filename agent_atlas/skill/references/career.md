# Career — LinkedIn

## Capabilities
- Authenticated people/jobs/profile via linkedin-scraper-mcp
- Public pages via Jina

## Prerequisites
```bash
uvx linkedin-scraper-mcp@latest --login
# Add linkedin-scraper-mcp to ~/.cursor/mcp.json (docs/tier1.md)
# Restart MCP host; confirm tools appear
```

## Doctor
- `ok` + `linkedin-mcp` → configured (call MCP tools from agent)
- `warn` + `Jina Reader` → public pages only
- See `docs/channels.md` in the agent-atlas repository

## Commands

```bash
# MCP tools from the agent host: search_people, get_person_profile, search_jobs, …
curl -s "https://r.jina.ai/https://www.linkedin.com/in/…"
```

## Retry
1. Doctor `off` → `--login` + MCP config + host restart
2. MCP tools fail → re-login (`~/.linkedin-mcp/`)
3. Public URL → Jina

## Fallback
Jina for public pages; Exa `site:linkedin.com`

## Safety
Secondary LinkedIn account. No OpenCLI / li-cli path.
