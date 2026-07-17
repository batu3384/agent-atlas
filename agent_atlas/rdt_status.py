# -*- coding: utf-8 -*-
"""rdt-cli probe + optional cookie sync from configured Chrome profile."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, Tuple

from agent_atlas.chrome_profile import chrome_cookie_file
from agent_atlas.config import Config
from agent_atlas.probe import which

_RDT_CRED = Path.home() / ".config" / "rdt-cli" / "credential.json"
_REQUIRED = {"reddit_session"}


def rdt_installed() -> bool:
    return which("rdt") is not None


def sync_reddit_cookies(config: Config) -> bool:
    """Extract Reddit cookies from Atlas Chrome profile into rdt-cli credential file."""
    cookie_file = chrome_cookie_file(config)
    if not cookie_file or not cookie_file.exists():
        return False

    script = f'''
import json, time, browser_cookie3
from pathlib import Path
cookies = {{}}
try:
    jar = browser_cookie3.chrome(
        domain_name=".reddit.com",
        cookie_file={str(cookie_file)!r},
    )
    for c in jar:
        cookies[c.name] = c.value
except Exception:
    pass
required = {sorted(_REQUIRED)!r}
if not any(k in cookies for k in required):
    raise SystemExit(1)
out = {{
    "cookies": cookies,
    "source": "agent-atlas:chrome-profile",
    "username": None,
    "modhash": None,
    "saved_at": time.time(),
    "last_verified_at": None,
}}
path = Path({str(_RDT_CRED)!r})
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2))
path.chmod(0o600)
print("ok")
'''
    try:
        if which("uv") is None:
            return False
        proc = subprocess.run(
            ["uv", "run", "--with", "browser-cookie3", "python3", "-c", script],
            capture_output=True,
            text=True,
            timeout=35,
            check=False,
        )
        return proc.returncode == 0 and "ok" in (proc.stdout or "")
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def rdt_status() -> Tuple[bool, str, Optional[dict]]:
    """Return (authenticated, detail_message, parsed_status_or_none)."""
    if not rdt_installed():
        return False, "rdt-cli not installed — uv tool install rdt-cli", None

    try:
        proc = subprocess.run(
            ["rdt", "status", "--yaml"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "rdt status timed out", None

    out = (proc.stdout or "").strip()
    if not out:
        return False, "rdt status empty output", None

    try:
        data = _parse_yaml_status(out)
    except Exception:
        data = None

    if data and data.get("authenticated"):
        user = data.get("username") or "?"
        return True, f'rdt-cli authenticated (@{user}) — rdt search "q" -n 10', data

    err = (data or {}).get("error") if data else None
    hint = err or (proc.stderr or proc.stdout or "not authenticated")[:80]
    return False, f"rdt-cli needs login — rdt login (docs/tier1.md) — {hint}", data


def _parse_yaml_status(text: str) -> dict:
    """Minimal parse for rdt status --yaml (top-level ok/data)."""
    try:
        import yaml  # noqa: PLC0415 — optional dep already in project

        parsed = yaml.safe_load(text)
        if isinstance(parsed, dict) and "data" in parsed:
            return parsed["data"] if isinstance(parsed["data"], dict) else parsed
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass
    if "authenticated: true" in text:
        user = ""
        for line in text.splitlines():
            if line.strip().startswith("username:"):
                user = line.split(":", 1)[1].strip()
        return {"authenticated": True, "username": user}
    return {}


def ensure_rdt_session(config: Config, *, sync: bool = True) -> Tuple[bool, str]:
    """Return (ok, message). Optionally sync cookies from configured Chrome profile."""
    ok, msg, _ = rdt_status()
    if ok:
        return True, msg
    if sync:
        if which("uv") is None:
            return False, (
                f"{msg} | cookie sync needs uv — install uv "
                "(https://docs.astral.sh/uv/) or: rdt login"
            )
        if sync_reddit_cookies(config):
            ok, msg, _ = rdt_status()
            if ok:
                return True, msg
    return False, msg
