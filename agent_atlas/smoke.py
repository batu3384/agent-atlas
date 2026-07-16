# -*- coding: utf-8 -*-
"""End-to-end research smoke — one real call per ready channel."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable, List

from agent_atlas.config import Config, apply_runtime_env
from agent_atlas.doctor import check_all


@dataclass
class SmokeResult:
    channel: str
    status: str  # pass | fail | skip
    detail: str


def _run(cmd: list[str], *, timeout: float = 45) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError:
        return False, f"missing: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, f"timeout {timeout}s"
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if proc.returncode != 0:
        return False, (out[:200] or f"exit {proc.returncode}")
    if not out:
        return False, "empty output"
    return True, out[:120].replace("\n", " ")


def _smoke_web() -> SmokeResult:
    ok, detail = _run(
        ["curl", "-sL", "--max-time", "20", "https://r.jina.ai/https://example.com"],
        timeout=25,
    )
    return SmokeResult("web", "pass" if ok else "fail", detail)


def _smoke_exa() -> SmokeResult:
    ok, detail = _run(
        [
            "mcporter",
            "call",
            'exa.web_search_exa(query: "Model Context Protocol", numResults: 2)',
        ],
        timeout=40,
    )
    return SmokeResult("exa", "pass" if ok else "fail", detail)


def _smoke_youtube() -> SmokeResult:
    ok, detail = _run(
        [
            "yt-dlp",
            "--skip-download",
            "--print",
            "%(id)s %(title)s",
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        ],
        timeout=40,
    )
    return SmokeResult("youtube", "pass" if ok else "fail", detail)


def _smoke_github() -> SmokeResult:
    ok, detail = _run(
        ["gh", "repo", "view", "cli/cli", "--json", "name", "-q", ".name"],
        timeout=20,
    )
    return SmokeResult("github", "pass" if ok else "fail", detail)


def _smoke_rss() -> SmokeResult:
    code = (
        "import feedparser; d=feedparser.parse('https://hnrss.org/frontpage'); "
        "assert d.entries; print(d.entries[0].title)"
    )
    ok, detail = _run(["python3", "-c", code], timeout=25)
    return SmokeResult("rss", "pass" if ok else "fail", detail)


def _smoke_twitter() -> SmokeResult:
    ok, detail = _run(["twitter", "search", "AI agents", "-n", "3"], timeout=35)
    return SmokeResult("twitter", "pass" if ok else "fail", detail)


def _smoke_reddit() -> SmokeResult:
    ok, detail = _run(
        ["opencli", "reddit", "search", "AI agents", "-f", "yaml"],
        timeout=45,
    )
    return SmokeResult("reddit", "pass" if ok else "fail", detail)


def _smoke_linkedin() -> SmokeResult:
    # Public page via Jina — often blocked anonymously; treat soft errors as skip
    ok, detail = _run(
        [
            "curl",
            "-sL",
            "--max-time",
            "25",
            "https://r.jina.ai/https://www.linkedin.com/company/github",
        ],
        timeout=30,
    )
    low = detail.lower()
    if (not ok) or "abusealleviation" in low or '"code":403' in low or "40305" in low:
        return SmokeResult(
            "linkedin",
            "skip",
            "Jina anonymous LinkedIn blocked — use OpenCLI when bridge connected",
        )
    return SmokeResult("linkedin", "pass", detail)


_SMOKES: dict[str, Callable[[], SmokeResult]] = {
    "web": _smoke_web,
    "exa": _smoke_exa,
    "youtube": _smoke_youtube,
    "github": _smoke_github,
    "rss": _smoke_rss,
    "twitter": _smoke_twitter,
    "reddit": _smoke_reddit,
    "linkedin": _smoke_linkedin,
}

# Channels that can smoke even when doctor is warn (public / no login)
_WARN_OK = {"linkedin"}


def run_smoke(config: Config | None = None) -> List[SmokeResult]:
    """One real research call per channel doctor marks ok (linkedin: Jina if warn)."""
    config = config or Config()
    apply_runtime_env(config)
    health = check_all(config)
    results: List[SmokeResult] = []

    for name, fn in _SMOKES.items():
        status = health.get(name, {}).get("status", "off")
        msg = (health.get(name, {}).get("message") or "")[:80]

        if status == "off":
            results.append(SmokeResult(name, "skip", "disabled / not installed"))
            continue
        if status == "ok" or (status == "warn" and name in _WARN_OK):
            results.append(fn())
            continue
        results.append(SmokeResult(name, "skip", msg or f"doctor={status}"))

    return results


def format_smoke(results: List[SmokeResult]) -> str:
    lines = ["Agent Atlas research smoke", "=" * 40]
    for r in results:
        mark = {"pass": "OK", "fail": "FAIL", "skip": "--"}.get(r.status, "?")
        lines.append(f"  [{mark}] {r.channel:10} {r.detail}")
    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    skipped = sum(1 for r in results if r.status == "skip")
    lines.append("")
    lines.append(f"pass={passed} fail={failed} skip={skipped}")
    return "\n".join(lines)


def smoke_exit_code(results: List[SmokeResult]) -> int:
    return 1 if any(r.status == "fail" for r in results) else 0


def results_as_dict(results: List[SmokeResult]) -> dict:
    return {
        "results": [
            {"channel": r.channel, "status": r.status, "detail": r.detail} for r in results
        ],
        "pass": sum(1 for r in results if r.status == "pass"),
        "fail": sum(1 for r in results if r.status == "fail"),
        "skip": sum(1 for r in results if r.status == "skip"),
    }
