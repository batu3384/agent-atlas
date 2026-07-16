"""LinkedIn client — headless browser transport + cookie auth."""

from __future__ import annotations

import json
import logging
import re
from typing import Any
from urllib.parse import quote, urlencode

from .auth import Credential, save_credential
from .browser import BrowserSession, probe_authenticated
from .constants import BASE_URL, PEOPLE_SEARCH_URL
from .exceptions import ApiError, AuthError
from .parsers.people_search import parse_people_search_html
from .parsers.profile import parse_profile_html

logger = logging.getLogger(__name__)


def _csrf(cookies: dict[str, str]) -> str:
    js = cookies.get("JSESSIONID", "")
    return js.strip('"')


class LinkedInClient:
    def __init__(self, credential: Credential):
        self.credential = credential
        self._session = BrowserSession(credential.cookies)

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> LinkedInClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _persist_cookies(self) -> None:
        self.credential.cookies = self._session.export_cookies()
        save_credential(self.credential)

    def warmup(self) -> None:
        """No-op — session bootstraps on first real navigation."""
        return

    def _api_headers(self) -> dict[str, str]:
        csrf = _csrf(self.credential.cookies)
        if not csrf:
            self.warmup()
            csrf = _csrf(self.credential.cookies)
        h = {
            "x-restli-protocol-version": "2.0.0",
            "Accept": "application/vnd.linkedin.normalized+json+2.1",
        }
        if csrf:
            h["csrf-token"] = csrf
        return h

    def validate_session(self) -> dict[str, Any]:
        info = probe_authenticated(self._session)
        if info.get("username"):
            self.credential.username = info["username"]
        # Persist only after a STRICT successful probe — keep original li_at
        self._persist_cookies()
        save_credential(self.credential)
        return info

    def people_search(self, query: str, *, limit: int = 5) -> list[dict[str, str]]:
        self.warmup()
        limit = max(1, min(10, limit))
        url = PEOPLE_SEARCH_URL + "?" + urlencode({"keywords": query})
        resp = self._session.get(url, wait_ms=3000)
        from .browser import _looks_logged_in

        if not _looks_logged_in(resp.url, resp.text):
            raise AuthError(
                "LinkedIn people-search not logged in — Atlas Chrome → linkedin.com (see FEED) "
                "→ Cmd+Q → li login --force"
            )
        if resp.status == 429:
            raise ApiError("LinkedIn rate limited on people-search")
        if resp.status >= 400:
            raise ApiError(f"people-search HTTP {resp.status}")
        rows = parse_people_search_html(resp.text, limit=limit)
        if not rows:
            raise ApiError("No people results parsed — HTML layout may have changed")
        self._persist_cookies()
        return [{"rank": i + 1, **row} for i, row in enumerate(rows[:limit])]

    def search_jobs(self, query: str, *, limit: int = 10) -> list[dict[str, str]]:
        self.warmup()
        limit = max(1, min(25, limit))
        q = f"(origin:JOB_SEARCH_PAGE_JOB_FILTER,keywords:{quote(query)},locationUnion:(geoId:92000000))"
        params = {
            "decorationId": "com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-220",
            "count": str(limit),
            "q": "jobSearch",
            "query": q,
            "start": "0",
        }
        path = "/voyager/api/voyagerJobsDashJobCards?" + urlencode(params)
        data = self._session.get_json(f"{BASE_URL}{path}", extra_headers=self._api_headers())
        jobs: list[dict[str, str]] = []
        for element in data.get("elements") or []:
            card = (element or {}).get("jobCardUnion", {}).get("jobPostingCard") or {}
            title = card.get("jobPostingTitle") or (card.get("title") or {}).get("text") or ""
            company = (card.get("primaryDescription") or {}).get("text") or ""
            location = (card.get("secondaryDescription") or {}).get("text") or ""
            urn = card.get("jobPostingUrn") or card.get("entityUrn") or ""
            m = re.search(r"(\d+)", str(urn))
            job_id = m.group(1) if m else ""
            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": f"{BASE_URL}/jobs/view/{job_id}" if job_id else "",
                }
            )
        self._persist_cookies()
        return [{"rank": i + 1, **j} for i, j in enumerate(jobs[:limit])]

    def profile_read(self, profile_url: str) -> dict[str, str]:
        self.warmup()
        if not profile_url.startswith("http"):
            profile_url = f"{BASE_URL}/in/{profile_url.strip('/')}/"
        resp = self._session.get(profile_url, wait_ms=2000)
        if "authwall" in resp.url:
            raise AuthError("profile-read requires login")
        if resp.status >= 400:
            raise ApiError(f"profile-read HTTP {resp.status}")
        self._persist_cookies()
        return parse_profile_html(resp.text, profile_url=str(resp.url))
