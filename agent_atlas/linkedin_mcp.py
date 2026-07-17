# -*- coding: utf-8 -*-
"""LinkedIn MCP probe — Reach-style (mcporter live list + explicit scraper config)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

from agent_atlas.probe import probe_command, which

_MCP_HINT = (
    "uvx linkedin-scraper-mcp@latest --login  "
    "then add MCP (docs/tier1.md)"
)
_SCRAPER_MARKERS = ("linkedin-scraper-mcp", "mcp-server-linkedin")


def _mcp_config_paths() -> list[Path]:
    home = Path.home()
    return [
        home / ".cursor" / "mcp.json",
        home / ".config" / "cursor" / "mcp.json",
        home / ".claude.json",
        home / ".codeium" / "windsurf" / "mcp_config.json",
        home / ".mcporter" / "mcporter.json",
        Path.cwd() / ".mcp.json",
        Path.cwd() / "mcp.json",
        Path.cwd() / "config" / "mcporter.json",
    ]


def _server_is_linkedin_scraper(server_cfg: object) -> bool:
    """True only if command/args/url clearly reference linkedin-scraper-mcp."""
    blob = json.dumps(server_cfg).lower() if not isinstance(server_cfg, str) else server_cfg.lower()
    return any(m in blob for m in _SCRAPER_MARKERS)


def _cursor_has_scraper_mcp() -> bool:
    for path in _mcp_config_paths():
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        servers = data.get("mcpServers") or data.get("mcp") or {}
        if not isinstance(servers, dict):
            continue
        for key, cfg in servers.items():
            key_l = str(key).lower()
            if "linkedin" not in key_l and not _server_is_linkedin_scraper(cfg):
                continue
            # Name alone is not enough — require scraper package markers
            if _server_is_linkedin_scraper(cfg):
                return True
            # mcporter-style HTTP entry under key linkedin with /mcp URL
            if "linkedin" in key_l and isinstance(cfg, dict):
                url = str(cfg.get("baseUrl") or cfg.get("url") or "").lower()
                if "/mcp" in url and "linkedin" in url:
                    return True
    return False


def _mcporter_has_linkedin() -> Tuple[str, str]:
    """Return (status, detail) from live `mcporter config list`.

    status: ok | missing | broken | absent
    """
    probe = probe_command(
        "mcporter",
        ["config", "list"],
        timeout=10,
        package="mcporter",
    )
    if probe.status == "missing":
        return "missing", probe.hint or "mcporter not installed"
    if probe.status in ("broken", "timeout"):
        return "broken", probe.hint or probe.output or "mcporter failed"
    if not probe.ok:
        return "broken", probe.hint or probe.output or "mcporter error"
    # Reach: "linkedin" in list output
    if "linkedin" in (probe.output or "").lower():
        return "ok", probe.output
    return "absent", probe.output or ""


def linkedin_mcp_configured() -> bool:
    """True if mcporter lists linkedin OR Cursor/Claude has scraper MCP."""
    st, _ = _mcporter_has_linkedin()
    if st == "ok":
        return True
    return _cursor_has_scraper_mcp()


def linkedin_mcp_status() -> Tuple[str, str, Optional[dict]]:
    """Return (ok|warn|off|error, message, meta).

    Reach parity: configured LinkedIn MCP ⇒ ok (session verified by host on use).
    """
    mcp_st, mcp_detail = _mcporter_has_linkedin()
    if mcp_st == "ok":
        return (
            "ok",
            "linkedin-mcp via mcporter — Profile, jobs, people search",
            {"source": "mcporter", "configured": True},
        )
    if mcp_st == "broken":
        return (
            "error",
            f"mcporter broken — reinstall: npm i -g mcporter ({mcp_detail[:80]})",
            {"source": "mcporter", "configured": False},
        )

    if _cursor_has_scraper_mcp():
        return (
            "ok",
            "linkedin-mcp in agent MCP config — use MCP tools (search_people, …)",
            {"source": "cursor-mcp", "configured": True},
        )

    has_uvx = which("uvx") is not None
    if mcp_st == "missing" and not has_uvx:
        return (
            "off",
            f"LinkedIn MCP: install uv + mcporter, then {_MCP_HINT}",
            {"configured": False, "uvx": False},
        )
    return (
        "off",
        f"LinkedIn MCP not configured — {_MCP_HINT}",
        {"configured": False, "mcporter": mcp_st, "uvx": has_uvx},
    )
