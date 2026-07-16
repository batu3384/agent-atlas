"""Parse LinkedIn profile HTML."""

from __future__ import annotations

import re
from html import unescape


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", unescape(s or "")).strip()


def parse_profile_html(html: str, *, profile_url: str) -> dict[str, str]:
    name_m = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.I)
    name = _clean(name_m.group(1)) if name_m else ""
    headline_m = re.search(r'<div[^>]*class="[^"]*text-body-medium[^"]*"[^>]*>([^<]+)</div>', html)
    headline = _clean(headline_m.group(1)) if headline_m else ""
    return {
        "profile_url": profile_url,
        "name": name,
        "headline": headline,
        "location": "",
        "about": "",
    }
