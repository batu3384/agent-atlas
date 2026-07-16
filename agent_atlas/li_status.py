# -*- coding: utf-8 -*-
"""li-cli probe + optional cookie sync from configured Chrome profile."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

from agent_atlas.chrome_profile import chrome_cookie_file, chrome_profile_in_use
from agent_atlas.config import Config
from agent_atlas.probe import which

_LI_CRED = Path.home() / ".config" / "li-cli" / "credential.json"
_REQUIRED = {"li_at"}
_CACHE_TTL_SECONDS = 300
_status_cache: Optional[Tuple[float, Tuple[bool, str, Optional[dict]]]] = None


def clear_li_cache() -> None:
    global _status_cache
    _status_cache = None


def li_installed() -> bool:
    return which("li") is not None


def _credential_on_disk() -> Optional[dict]:
    if not _LI_CRED.exists():
        return None
    try:
        data = json.loads(_LI_CRED.read_text())
        cookies = data.get("cookies") or {}
        if not cookies.get("li_at"):
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def sync_linkedin_cookies(config: Config) -> bool:
    """Extract LinkedIn cookies from Atlas Chrome profile into li-cli credential file."""
    cookie_file = chrome_cookie_file(config)
    if not cookie_file or not cookie_file.exists():
        return False

    script = f'''
import json, time, browser_cookie3
from pathlib import Path
cookies = {{}}
try:
    jar = browser_cookie3.chrome(
        domain_name=".linkedin.com",
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
    "saved_at": time.time(),
}}
path = Path({str(_LI_CRED)!r})
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2))
path.chmod(0o600)
print("ok")
'''
    try:
        proc = subprocess.run(
            ["uv", "run", "--with", "browser-cookie3", "python3", "-c", script],
            capture_output=True,
            text=True,
            timeout=35,
            check=False,
        )
        if proc.returncode == 0 and "ok" in (proc.stdout or ""):
            clear_li_cache()
            return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def li_status(*, quick: bool = False, use_cache: bool = True) -> Tuple[bool, str, Optional[dict]]:
    """Return (authenticated, detail_message, parsed_status_or_none)."""
    global _status_cache

    if not li_installed():
        return False, "li-cli not installed — uv tool install -e ./li-cli", None

    if use_cache and _status_cache is not None:
        cached_at, cached = _status_cache
        if (time.time() - cached_at) < _CACHE_TTL_SECONDS:
            return cached

    cmd = ["li", "status", "--yaml"]
    if quick:
        cmd.append("--quick")
    timeout = 15 if quick else 90

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "li status timed out", None

    out = (proc.stdout or "").strip()
    if not out:
        return False, "li status empty output", None

    data = _parse_yaml_status(out)
    if data and data.get("authenticated"):
        user = data.get("username") or "?"
        result = (
            True,
            f'li-cli authenticated (@{user}) — li people-search "q" -n 5',
            data,
        )
        if use_cache and not quick:
            _status_cache = (time.time(), result)
        return result

    err = _extract_error(data, proc)
    if chrome_profile_in_use() and not quick:
        err = f"{err} (tip: close Google Chrome, then li login --force)"
    result = (False, f"li-cli needs login — li login (docs/tier1.md) — {err}", data)
    if use_cache and not quick:
        _status_cache = (time.time(), result)
    return result


def _extract_error(data: Optional[dict], proc: subprocess.CompletedProcess) -> str:
    if isinstance(data, dict):
        if isinstance(data.get("error"), str):
            return data["error"][:120]
        if isinstance(data.get("error"), dict):
            return str(data["error"].get("message", ""))[:120]
    return (proc.stderr or proc.stdout or "not authenticated")[:120]


def _parse_yaml_status(text: str) -> dict:
    """Parse li status --yaml (success or error payloads)."""
    try:
        import yaml  # noqa: PLC0415

        parsed = yaml.safe_load(text)
        if not isinstance(parsed, dict):
            return {}
        if parsed.get("ok") is False:
            err = parsed.get("error")
            if isinstance(err, dict):
                return {"authenticated": False, "error": err.get("message", str(err))}
            return {"authenticated": False, "error": str(err or "not authenticated")}
        if "data" in parsed:
            return parsed["data"] if isinstance(parsed["data"], dict) else parsed
        return parsed
    except Exception:
        pass
    if "authenticated: true" in text:
        user = ""
        for line in text.splitlines():
            if line.strip().startswith("username:"):
                user = line.split(":", 1)[1].strip()
        return {"authenticated": True, "username": user}
    return {}


def ensure_li_session(config: Config, *, sync: bool = True) -> Tuple[bool, str]:
    """Return (ok, message). Optionally sync cookies from configured Chrome profile."""
    ok, msg, _ = li_status(use_cache=True)
    if ok:
        return True, msg
    if sync and sync_linkedin_cookies(config):
        clear_li_cache()
        ok, msg, _ = li_status(use_cache=False)
        if ok:
            return True, msg
    return False, msg
