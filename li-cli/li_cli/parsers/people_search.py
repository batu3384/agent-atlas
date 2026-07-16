"""Parse LinkedIn people-search HTML (SSR, no browser)."""

from __future__ import annotations

import re
from html import unescape
from typing import Any


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", unescape(s or "")).strip()


def parse_people_search_html(html: str, *, limit: int = 10) -> list[dict[str, str]]:
    if "search/results/people" not in html and "/in/" not in html:
        return []
    # anchor-based extraction (OpenCLI people-search strategy, simplified)
    seen: set[str] = set()
    rows: list[dict[str, str]] = []
    for m in re.finditer(r'href="(/in/[^"?#]+)/?"', html):
        handle = m.group(1).split("/in/")[-1].rstrip("/")
        if not handle or handle in seen:
            continue
        seen.add(handle)
        # try to find aria-hidden name near anchor
        start = max(0, m.start() - 400)
        chunk = html[start : m.end() + 400]
        name_m = re.search(
            r'aria-hidden="true"[^>]*>([^<]{2,80})</span>',
            chunk,
        )
        name = _clean(name_m.group(1)) if name_m else handle.replace("-", " ").title()
        rows.append(
            {
                "name": name,
                "headline": "",
                "location": "",
                "profile_url": f"https://www.linkedin.com/in/{handle}/",
            }
        )
        if len(rows) >= limit:
            break
    return rows
