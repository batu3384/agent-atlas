# LinkedIn Reach-parity Implementation Plan

> **For agentic workers:** Implement task-by-task. Steps use checkbox syntax.

**Goal:** LinkedIn = `linkedin-mcp → Jina` only; remove OpenCLI/li-cli/Chrome open-closed from LinkedIn path.

**Architecture:** Doctor/smoke/docs follow Agent Reach: authenticate via `linkedin-scraper-mcp`, public pages via Jina. `li-cli/` stays unwired.

**Tech Stack:** Python agent-atlas, linkedin-scraper-mcp (uvx), Jina Reader, optional mcporter.

## Global Constraints

- No Chrome open/closed language for LinkedIn in user-facing docs
- Do not delete `li-cli/` package directory
- Keep Twitter/Reddit Chrome/cookie behavior unchanged
- Docs English; product messages English

---

## File map

| File | Change |
|------|--------|
| `agent_atlas/channels/social.py` | LinkedInChannel → MCP → Jina |
| `agent_atlas/linkedin_mcp.py` | Also detect mcporter LinkedIn; clearer hints |
| `agent_atlas/smoke.py` | LinkedIn smoke for MCP/Jina |
| `agent_atlas/cli.py` | install linkedin → MCP instructions |
| `agent_atlas/opencli_status.py` | Remove unused `opencli_linkedin_session` if dead |
| `tests/test_core.py` | Replace OpenCLI LinkedIn tests |
| `docs/tier1.md`, `platforms.md`, `install.md` | Simplify LinkedIn |
| `README.md`, `SKILL.md`, `agent_atlas/skill/SKILL.md`, `PLAN.md`, `llms.txt`, `CHANGELOG.md` | Sync |
| `li-cli/README.md` | Note: not used by Atlas routing |

---

### Task 1: Channel + MCP probe

- [ ] Rewrite `LinkedInChannel` backends/check
- [ ] Extend `linkedin_mcp_configured` for mcporter configs
- [ ] Tests: MCP → warn; no MCP + Jina → warn; neither → off

### Task 2: Smoke + install

- [ ] `_smoke_linkedin`: MCP configured → pass with “use MCP tools”; else Jina curl
- [ ] `install --channels linkedin`: print uvx login + mcp.json snippet (no li-cli)

### Task 3: Docs + skill

- [ ] Rewrite LinkedIn sections; strip Chrome open/closed for LinkedIn
- [ ] Bump CHANGELOG 0.1.2 note

### Task 4: Verify

- [ ] `uv run pytest tests/test_core.py -q`
