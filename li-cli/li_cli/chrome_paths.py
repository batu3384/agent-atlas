"""Chrome profile paths for li-cli."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def chrome_root() -> Path:
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA", "")
        return Path(local) / "Google" / "Chrome" / "User Data"
    return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"


def _profile_from_agent_atlas_config() -> str | None:
    """Read twitter/linkedin chrome profile from ~/.agent-atlas/config.yaml."""
    cfg = Path.home() / ".agent-atlas" / "config.yaml"
    if not cfg.exists():
        return None
    try:
        import yaml

        data = yaml.safe_load(cfg.read_text()) or {}
        for key in ("linkedin_chrome_profile", "twitter_chrome_profile", "reddit_chrome_profile"):
            val = data.get(key)
            if val:
                return str(val)
    except Exception:
        pass
    return None


def configured_profile_name() -> str | None:
    """Resolve which Chrome profile directory to use (e.g. 'Profile 3')."""
    return (
        os.environ.get("LI_CHROME_PROFILE")
        or os.environ.get("TWITTER_CHROME_PROFILE")
        or _profile_from_agent_atlas_config()
    )


def configured_profile() -> tuple[Path, str] | None:
    profile = configured_profile_name()
    browser = (os.environ.get("LI_BROWSER") or os.environ.get("TWITTER_BROWSER") or "chrome").lower()
    if not profile or browser != "chrome":
        return None
    return chrome_root(), profile


def cookie_file() -> Path | None:
    cfg = configured_profile()
    if not cfg:
        return None
    root, profile = cfg
    return root / profile / "Cookies"


def chrome_process_running() -> bool:
    """True only if a live Google Chrome process exists (not a stale SingletonLock)."""
    try:
        if os.name == "nt":
            out = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return "chrome.exe" in (out.stdout or "").lower()
        out = subprocess.run(
            ["pgrep", "-x", "Google Chrome"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        return out.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def chrome_profile_in_use() -> bool:
    """Prefer live process check; SingletonLock alone is often stale after Cmd+Q."""
    return chrome_process_running()


def list_profiles_with_linkedin() -> list[tuple[str, bool]]:
    """Return [(profile_dir, has_li_at), ...] for diagnosis."""
    root = chrome_root()
    rows: list[tuple[str, bool]] = []
    try:
        import browser_cookie3
    except ImportError:
        return rows
    for child in sorted(root.iterdir()):
        cookies = child / "Cookies"
        if not cookies.exists():
            continue
        try:
            jar = browser_cookie3.chrome(domain_name=".linkedin.com", cookie_file=str(cookies))
            has = any(c.name == "li_at" for c in jar)
            rows.append((child.name, has))
        except Exception:
            continue
    return rows
