"""Headless Chromium transport — isolated profile + injected cookies.

LinkedIn often rejects cookie replay; validate must not false-positive.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from dataclasses import dataclass
from typing import Any

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright

from .chrome_paths import chrome_process_running
from .constants import BASE_URL, BROWSER_PROFILE_DIR, HEADERS
from .exceptions import ApiError, AuthError

logger = logging.getLogger(__name__)


def _pw_cookies(cookies: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, value in cookies.items():
        if not value or value == "delete me":
            continue
        rows.append(
            {
                "name": name,
                "value": value,
                "domain": ".linkedin.com",
                "path": "/",
                "secure": True,
                "sameSite": "Lax",
            }
        )
    return rows


def reset_isolated_profile() -> None:
    if BROWSER_PROFILE_DIR.exists():
        shutil.rmtree(BROWSER_PROFILE_DIR, ignore_errors=True)


@dataclass
class BrowserResponse:
    status: int
    text: str
    url: str


def _is_login_wall(url: str, html: str) -> bool:
    u = url.lower()
    if any(x in u for x in ("/login", "/uas/", "authwall", "checkpoint", "challenge")):
        return True
    low = html.lower()
    if "oturum açma" in low or "sign in" in low and "linkedin" in low:
        if 'href="/in/' not in html or html.count('href="/in/') < 2:
            return True
    return False


def _looks_logged_in(url: str, html: str) -> bool:
    """Strict: must be on search/feed AND have multiple profile links, not a login page."""
    if _is_login_wall(url, html):
        return False
    if "search/results/people" not in url and "/feed" not in url:
        return False
    # Real people-search SSR embeds several /in/ anchors
    return html.count('href="/in/') >= 3 or html.count("/in/") >= 8


class BrowserSession:
    """Headless Chromium in ~/.config/li-cli/browser-profile."""

    def __init__(self, cookies: dict[str, str]):
        self._cookies = {k: v for k, v in cookies.items() if v and v != "delete me"}
        self._pw: Playwright | None = None
        self._context: BrowserContext | None = None

    def _ensure(self) -> Page:
        if self._context is not None:
            return self._context.pages[0] if self._context.pages else self._context.new_page()

        if not self._cookies.get("li_at"):
            raise AuthError("No li_at cookie — run: li login --force")

        BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        self._pw = sync_playwright().start()
        try:
            self._context = self._pw.chromium.launch_persistent_context(
                str(BROWSER_PROFILE_DIR),
                channel="chrome",
                headless=True,
                locale="en-US",
                viewport={"width": 1280, "height": 800},
                user_agent=HEADERS.get("User-Agent", ""),
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
            )
        except Exception:
            self._context = self._pw.chromium.launch_persistent_context(
                str(BROWSER_PROFILE_DIR),
                headless=True,
                locale="en-US",
                viewport={"width": 1280, "height": 800},
                user_agent=HEADERS.get("User-Agent", ""),
            )
        try:
            self._context.add_cookies(_pw_cookies(self._cookies))
        except Exception as exc:
            logger.debug("add_cookies: %s", exc)
        return self._context.pages[0] if self._context.pages else self._context.new_page()

    def close(self) -> None:
        if self._context is not None:
            self._context.close()
            self._context = None
        if self._pw is not None:
            self._pw.stop()
            self._pw = None

    def __enter__(self) -> BrowserSession:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def export_cookies(self) -> dict[str, str]:
        ctx = self._context
        if ctx is None:
            return dict(self._cookies)
        merged = dict(self._cookies)
        for c in ctx.cookies():
            if c.get("domain", "").endswith("linkedin.com"):
                val = c.get("value", "")
                if val and val != "delete me":
                    merged[c["name"]] = val
        # Never wipe li_at if Playwright cleared it during a failed challenge
        if not merged.get("li_at") and self._cookies.get("li_at"):
            merged["li_at"] = self._cookies["li_at"]
        self._cookies = merged
        return merged

    def get(self, url: str, *, wait_ms: int = 2000) -> BrowserResponse:
        page = self._ensure()
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as exc:
            msg = str(exc)
            if "ERR_TOO_MANY_REDIRECTS" in msg or "ERR_HTTP_RESPONSE_CODE_FAILURE" in msg:
                raise AuthError(
                    "LinkedIn rejected this session (cookie present but invalid). "
                    "In Atlas Chrome open linkedin.com — you must see your FEED (not login). "
                    "Then Cmd+Q and: li login --force"
                ) from exc
            raise ApiError(msg) from exc
        if wait_ms:
            page.wait_for_timeout(wait_ms)
        status = resp.status if resp else 0
        return BrowserResponse(status=status, text=page.content(), url=page.url)

    def get_json(self, url: str, *, extra_headers: dict[str, str] | None = None) -> Any:
        page = self._ensure()
        headers = dict(extra_headers or {})
        payload = page.evaluate(
            """async ({ url, headers }) => {
                const r = await fetch(url, { headers, credentials: 'include' });
                const text = await r.text();
                return { status: r.status, text };
            }""",
            {"url": url, "headers": headers},
        )
        status = int(payload.get("status", 0))
        text = payload.get("text", "")
        if status in (401, 403):
            raise AuthError(f"LinkedIn API auth failed (HTTP {status})")
        if status == 429:
            raise ApiError("LinkedIn rate limited — wait and retry")
        if status >= 400:
            raise ApiError(f"LinkedIn API HTTP {status}: {text[:200]}")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ApiError("LinkedIn API returned non-JSON") from exc


def probe_authenticated(session: BrowserSession) -> dict[str, Any]:
    """Strict session check — cookie file alone is not enough."""
    url = f"{BASE_URL}/search/results/people/?keywords=github"
    resp = session.get(url, wait_ms=3000)
    if not _looks_logged_in(resp.url, resp.text):
        raise AuthError(
            "LinkedIn cookie exists but session is not logged in. "
            "Atlas Chrome → linkedin.com → confirm FEED is visible → Cmd+Q → li login --force"
        )
    if resp.status == 429:
        raise ApiError("LinkedIn rate limited — wait and retry")
    if resp.status >= 400:
        raise ApiError(f"session probe HTTP {resp.status}")
    username = None
    m = re.search(r'"publicIdentifier":"([^"]+)"', resp.text)
    if m:
        username = m.group(1)
    return {
        "authenticated": True,
        "username": username,
        "cookie_count": len(session.export_cookies()),
        "chrome_running": chrome_process_running(),
        "probe_url": resp.url,
    }
