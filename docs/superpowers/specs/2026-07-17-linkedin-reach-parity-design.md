# Design: LinkedIn Reach-parity simplification

**Date:** 2026-07-17  
**Status:** Approved (user chose option A)  
**Goal:** Remove LinkedIn complexity; match Agent Reach mental model.

## Decision

LinkedIn backends become **only**:

```
linkedin-scraper-mcp → Jina Reader
```

Drop from LinkedIn routing and docs:

- OpenCLI LinkedIn path
- li-cli as Atlas backend
- Chrome open / closed / Profile / bridge / feed language

## User flow

1. `uvx linkedin-scraper-mcp@latest --login` (visible browser login once)
2. Register MCP in Cursor `mcp.json` and/or mcporter HTTP (Reach-style)
3. Agent uses MCP tools for search/profile/jobs
4. Public URLs via Jina (`curl https://r.jina.ai/…`)

## Doctor

| Condition | Status | active_backend |
|-----------|--------|----------------|
| MCP configured (Cursor mcp.json and/or mcporter) | `warn` (session in MCP host) | `linkedin-mcp` |
| Else Jina reachable | `warn` (public only) | `Jina Reader` |
| Else | `off` | none |

No OpenCLI session probe. No li-cli ensure.

## Code impact

- `LinkedInChannel.check` — MCP then Jina only
- `smoke` LinkedIn — MCP configured → skip/pass note; else Jina public probe
- `install --channels linkedin` — print MCP login + config steps (not li-cli install)
- Docs/SKILL/README/PLAN/CHANGELOG — rewrite LinkedIn sections
- `li-cli/` remains in repo as orphaned experimental package (not wired)

## Non-goals

- Delete `li-cli/` directory
- Change Twitter/Reddit Chrome/cookie flows
- PyPI publish

## Trade-off

LinkedIn authenticated research requires an MCP host (Cursor/Claude/mcporter). No `opencli linkedin …` CLI path in Atlas docs.
