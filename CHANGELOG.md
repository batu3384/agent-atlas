# Changelog

All notable changes to Agent Atlas are documented here.

## [0.1.2] — 2026-07-17

### Changed
- LinkedIn simplified to Reach model: **linkedin-mcp → Jina** only
- Removed OpenCLI / li-cli from LinkedIn doctor, smoke, install, and docs
- Dropped Chrome open/closed / feed / bridge language for LinkedIn

### Notes
- `li-cli/` remains in-repo but is **not** wired into Atlas routing

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
