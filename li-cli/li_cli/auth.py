"""Cookie authentication for li-cli — always targets configured Atlas profile."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from .chrome_paths import (
    configured_profile_name,
    cookie_file as chrome_cookie_file,
    list_profiles_with_linkedin,
)
from .constants import CONFIG_DIR, CREDENTIAL_FILE, CREDENTIAL_TTL_DAYS, REQUIRED_COOKIES

logger = logging.getLogger(__name__)
_CREDENTIAL_TTL_SECONDS = CREDENTIAL_TTL_DAYS * 86400


class Credential:
    def __init__(
        self,
        cookies: dict[str, str],
        *,
        source: str = "unknown",
        username: str | None = None,
        saved_at: float | None = None,
        profile: str | None = None,
    ):
        self.cookies = cookies
        self.source = source
        self.username = username
        self.saved_at = saved_at
        self.profile = profile

    @property
    def is_valid(self) -> bool:
        return bool(self.cookies.get("li_at"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "cookies": self.cookies,
            "source": self.source,
            "username": self.username,
            "saved_at": self.saved_at or time.time(),
            "profile": self.profile,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Credential:
        return cls(
            cookies=data.get("cookies", {}),
            source=data.get("source", "saved"),
            username=data.get("username"),
            saved_at=data.get("saved_at"),
            profile=data.get("profile"),
        )


def save_credential(credential: Credential) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(CONFIG_DIR, 0o700)
    if credential.saved_at is None:
        credential.saved_at = time.time()
    CREDENTIAL_FILE.write_text(json.dumps(credential.to_dict(), indent=2, ensure_ascii=False))
    CREDENTIAL_FILE.chmod(0o600)


def load_credential() -> Credential | None:
    if not CREDENTIAL_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIAL_FILE.read_text())
        cred = Credential.from_dict(data)
        if not cred.is_valid:
            return None
        saved_at = data.get("saved_at", 0)
        if saved_at and (time.time() - saved_at) > _CREDENTIAL_TTL_SECONDS:
            logger.info("Credential stale; refreshing from browser")
            fresh = extract_browser_credential()
            return fresh or cred
        return cred
    except (json.JSONDecodeError, KeyError):
        return None


def clear_credential() -> None:
    if CREDENTIAL_FILE.exists():
        CREDENTIAL_FILE.unlink()


def diagnose_missing_cookies(profile: str | None) -> str:
    """Human-readable hint when configured profile has no LinkedIn session."""
    lines = []
    if profile:
        lines.append(f"Configured profile '{profile}' has no LinkedIn cookie (li_at).")
    else:
        lines.append("No Chrome profile configured (set LI_CHROME_PROFILE or agent-atlas config).")
    found = [name for name, has in list_profiles_with_linkedin() if has]
    if found:
        lines.append(f"LinkedIn login found in: {', '.join(found)}")
        lines.append(
            "You logged into LinkedIn in a DIFFERENT Chrome profile than Atlas. "
            "Switch to the Atlas profile (Profile 3), open linkedin.com, sign in, then retry."
        )
    else:
        lines.append("No Chrome profile on this Mac has a LinkedIn session.")
        lines.append("Open Atlas Chrome profile → linkedin.com → sign in → Cmd+Q → li login --force")
    return "\n".join(lines)


def extract_browser_credential() -> Credential | None:
    """Extract LinkedIn cookies from the CONFIGURED profile only — never silent Default fallback."""
    profile = configured_profile_name()
    cookie_path = chrome_cookie_file()
    if not profile or not cookie_path:
        return None
    if not cookie_path.exists():
        return None

    cookies = _read_cookies(cookie_path)
    if not cookies or not any(k in cookies for k in REQUIRED_COOKIES):
        return None
    cred = Credential(
        cookies=cookies,
        source=f"browser:{profile}",
        profile=profile,
    )
    save_credential(cred)
    return cred


def _read_cookies(cookie_path: Path) -> dict[str, str]:
    if shutil.which("uv"):
        script = f'''
import json, browser_cookie3
cookies = {{}}
jar = browser_cookie3.chrome(domain_name=".linkedin.com", cookie_file={str(cookie_path)!r})
for c in jar:
    cookies[c.name] = c.value
print(json.dumps(cookies))
'''
        try:
            proc = subprocess.run(
                ["uv", "run", "--with", "browser-cookie3", "python3", "-c", script],
                capture_output=True,
                text=True,
                timeout=35,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return json.loads(proc.stdout.strip())
        except Exception as e:
            logger.debug("subprocess extract failed: %s", e)
    try:
        import browser_cookie3

        jar = browser_cookie3.chrome(domain_name=".linkedin.com", cookie_file=str(cookie_path))
        return {c.name: c.value for c in jar}
    except Exception:
        return {}


def get_credential() -> Credential | None:
    cred = load_credential()
    if cred:
        return cred
    return extract_browser_credential()
