# -*- coding: utf-8 -*-
"""LinkedIn MCP (linkedin-scraper-mcp) presence probe — Reach-style."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

from agent_atlas.probe import which

_MCP_HINT = (
    "uvx linkedin-scraper-mcp@latest --login  "
    "then add MCP server (docs/tier1.md)"
)


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
    ]


def _blob_mentions_linkedin_mcp(blob: str) -> bool:
    low = blob.lower()
    if "linkedin-scraper-mcp" in low or "mcp-server-linkedin" in low:
        return True
    # mcporter HTTP registration or Cursor server named linkedin
    if "linkedin" in low and (
        "uvx" in low or "8001" in low or "/mcp" in low or "scraper" in low
    ):
        return True
    return False


def linkedin_mcp_configured() -> bool:
    """True if Cursor/Claude/mcporter config references LinkedIn MCP."""
    for path in _mcp_config_paths():
        if not path.is_file():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if _blob_mentions_linkedin_mcp(raw):
            return True
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        servers = data.get("mcpServers") or data.get("mcp") or {}
        if isinstance(servers, dict):
            if _blob_mentions_linkedin_mcp(json.dumps(servers)):
                return True
            # Named server "linkedin" with any transport
            for key in servers:
                if "linkedin" in str(key).lower():
                    return True
    return False


def linkedin_mcp_status() -> Tuple[str, str, Optional[dict]]:
    """Return (ok|warn|off, message, meta).

    Session lives in the MCP host — configured ⇒ warn (ready for agent tools).
    """
    has_uvx = which("uvx") is not None
    configured = linkedin_mcp_configured()

    if configured and has_uvx:
        return (
            "warn",
            "linkedin-mcp ready — use MCP tools (search_people, get_person_profile, …)",
            {"configured": True, "uvx": True},
        )
    if configured and not has_uvx:
        return (
            "warn",
            "linkedin-mcp in config but uvx missing — install uv (docs/tier1.md)",
            {"configured": True, "uvx": False},
        )
    if has_uvx:
        return (
            "off",
            f"LinkedIn MCP not configured — {_MCP_HINT}",
            {"configured": False, "uvx": True},
        )
    return (
        "off",
        "LinkedIn MCP: install uv, then " + _MCP_HINT,
        {"configured": False, "uvx": False},
    )
