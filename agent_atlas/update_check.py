# -*- coding: utf-8 -*-
"""Version / update helpers."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional, Tuple

from agent_atlas import __version__


def current_version() -> str:
    return __version__


def fetch_latest_version(*, timeout: float = 8) -> Tuple[Optional[str], str]:
    """Return (version_or_none, detail). Uses GitHub tags API."""
    url = "https://api.github.com/repos/batu3384/agent-atlas/tags?per_page=5"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "agent-atlas"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as e:
        return None, f"could not check GitHub tags: {e}"
    if not isinstance(data, list) or not data:
        return None, "no tags on GitHub yet"
    name = str(data[0].get("name") or "").lstrip("v")
    if not name:
        return None, "empty latest tag"
    return name, f"latest GitHub tag: v{name}"


def compare_versions(current: str, latest: str) -> str:
    """Return newer | same | older | unknown."""
    try:
        def parts(v: str) -> tuple:
            return tuple(int(x) for x in v.split(".")[:3])

        c, l = parts(current), parts(latest)
        if l > c:
            return "newer"
        if l == c:
            return "same"
        return "older"
    except ValueError:
        return "unknown"


def check_update() -> Tuple[int, str]:
    """Return (exit_code, human message). 0 = up to date or unknown; 2 = update available."""
    cur = current_version()
    latest, detail = fetch_latest_version()
    if not latest:
        return 0, f"Agent Atlas v{cur} — {detail}"
    cmp = compare_versions(cur, latest)
    if cmp == "newer":
        return 2, (
            f"Update available: v{cur} → v{latest}. "
            f"See docs/update.md or: uv tool install --force git+https://github.com/batu3384/agent-atlas.git"
        )
    if cmp == "same":
        return 0, f"Agent Atlas v{cur} — up to date ({detail})"
    if cmp == "older":
        return 0, f"Agent Atlas v{cur} — newer than GitHub tag v{latest} (dev build?)"
    return 0, f"Agent Atlas v{cur} — {detail}"
