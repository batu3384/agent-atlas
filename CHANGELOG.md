# Changelog

All notable changes to Agent Atlas are documented here.

## [0.1.5] — 2026-07-17

### Added
- `docs/channels.md` — authoritative doctor/smoke status contract
- Facebook/Instagram smoke paths; RSS smoke uses `sys.executable`
- CI: `pytest tests/`, stale-term guard, wheel clean-install gate
- Publish workflow: tag/version check + dist artifacts
- Config `ConfigError` for malformed YAML; probe OSError handling
- `install --safe` is probe-only (no config dir / skill install)

### Changed
- LinkedIn: mcporter line-token detection; Jina fallback when mcporter broken
- Removed obsolete `LI_*` / LinkedIn Chrome profile keys and dead OpenCLI helpers
- Skill references share Capabilities / Prerequisites / Doctor / Commands / Retry / Fallback / Safety
- Docs: PyPI `agent-atlas-cli` live; PATH checklist; LinkedIn setup checklist

### Removed
- Unused `requests` dependency; dead `ordered_backends` / Chrome process helpers

## [0.1.4] — 2026-07-17

### Added
- PyPI packaging as **`agent-atlas-cli`** (name `agent-atlas` blocked — too similar to existing `agentatlas`) + Trusted Publishing workflow
- Modular skill `references/` (web, search, social, career, video, dev)
- `docs/troubleshooting.md`
- Turkish summary: `docs/README_tr.md`

### Changed
- Install/update docs use `uv tool install agent-atlas-cli` (CLI remains `agent-atlas`) with git fallback
- Skill install already copies `references/` into agent skill dirs

## [0.1.3] — 2026-07-17

### Fixed
- LinkedIn doctor returns **ok** when mcporter lists LinkedIn or Cursor MCP has `linkedin-scraper-mcp` (Reach parity)
- Reject false-positive MCP configs (server name alone is not enough)

### Removed
- `li_status.py` and the orphaned `li-cli/` package (no longer routed)
- Uninstall no longer targets `~/.config/li-cli/`

### Added
- GitHub Actions CI (`pytest` matrix 3.10–3.13 + wheel gate)

## [0.1.2] — 2026-07-17

### Changed
- LinkedIn simplified to Reach model: **linkedin-mcp → Jina** only
- Removed OpenCLI / li-cli from LinkedIn doctor, smoke, install, and docs
- Dropped Chrome open/closed / feed / bridge language for LinkedIn

### Notes
- `li-cli/` was later removed in 0.1.3

## [0.1.1] — 2026-07-16

### Added
- Reach-style install/update URLs (`docs/install.md`, `docs/update.md`)
- `agent-atlas watch` and `agent-atlas check-update`
- LinkedIn OpenCLI **session** probe (bridge OK ≠ logged-in feed)
- Twitter OpenCLI fallback when twitter-cli is installed but unauthenticated
- `rdt-cli` / experimental `li-cli` integration + Chrome profile helpers
- Smoke respects `active_backend` from doctor
- `linkedin-mcp` (linkedin-scraper-mcp) documented as optional backend
- `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`

### Changed
- LinkedIn preferred path: OpenCLI (live Chrome) → li-cli (experimental) → linkedin-mcp → Jina
- Docs/SKILL honest about LinkedIn bot protection (no Chrome-closed guarantee)
- Uninstall also removes `~/.config/li-cli/`

### Removed
- PyPI publish workflow (publishing deferred; install via git/`uv tool`)

## [0.1.0] — 2026-07-16

### Added
- Initial release: installer, doctor, smoke, Tier 0–1 Western channels
- Config → runtime env (`TWITTER_*`, `OPENCLI_PROFILE`, …)
- SKILL.md for Cursor / Claude Code / agentskills.io
