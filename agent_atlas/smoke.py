# -*- coding: utf-8 -*-
"""End-to-end research smoke — one real call per ready channel."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable, List, Optional

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


def _smoke_twitter(backend: Optional[str] = None) -> SmokeResult:
    if backend == "OpenCLI":
        ok, detail = _run(
            ["opencli", "twitter", "search", "AI agents", "-f", "yaml"],
            timeout=45,
        )
        return SmokeResult("twitter", "pass" if ok else "fail", detail)
    ok, detail = _run(["twitter", "search", "AI agents", "-n", "3"], timeout=35)
    if ok:
        return SmokeResult("twitter", "pass", detail)
    ok2, detail2 = _run(
        ["opencli", "twitter", "search", "AI agents", "-f", "yaml"],
        timeout=45,
    )
    return SmokeResult("twitter", "pass" if ok2 else "fail", detail2 if not ok else detail)


def _smoke_reddit(backend: Optional[str] = None) -> SmokeResult:
    if backend != "OpenCLI":
        from agent_atlas.rdt_status import rdt_status

        ok_rdt, _, _ = rdt_status()
        if ok_rdt:
            ok, detail = _run(
                ["rdt", "search", "AI agents", "-n", "3", "--compact", "--yaml"],
                timeout=45,
            )
            if ok or "ok: true" in (detail or "").lower():
                return SmokeResult("reddit", "pass", detail)
            # fall through to OpenCLI
    ok, detail = _run(
        ["opencli", "reddit", "search", "AI agents", "-f", "yaml"],
        timeout=45,
    )
    return SmokeResult("reddit", "pass" if ok else "fail", detail)


def _smoke_linkedin(backend: Optional[str] = None) -> SmokeResult:
    """Reach-style: MCP is exercised by the agent host; Jina probed via HTTP."""
    from agent_atlas.linkedin_mcp import linkedin_mcp_configured
    from agent_atlas.probe import http_ok

    if backend == "linkedin-mcp" or linkedin_mcp_configured():
        return SmokeResult(
            "linkedin",
            "pass",
            "linkedin-mcp configured — use agent MCP tools (search_people, …)",
        )
    if http_ok("https://r.jina.ai/https://www.linkedin.com", timeout=15):
        return SmokeResult(
            "linkedin",
            "pass",
            "Jina public page OK — curl -s https://r.jina.ai/https://www.linkedin.com/…",
        )
    return SmokeResult("linkedin", "fail", "LinkedIn smoke: configure linkedin-mcp or check Jina")


_SMOKES: dict[str, Callable[..., SmokeResult]] = {
    "web": _smoke_web,
    "exa": _smoke_exa,
    "youtube": _smoke_youtube,
    "github": _smoke_github,
    "rss": _smoke_rss,
    "twitter": _smoke_twitter,
    "reddit": _smoke_reddit,
    "linkedin": _smoke_linkedin,
}


def run_smoke(config: Config | None = None) -> List[SmokeResult]:
    """One real research call per channel doctor marks ok — respects active_backend."""
    config = config or Config()
    apply_runtime_env(config)
    health = check_all(config)
    results: List[SmokeResult] = []

    for name, fn in _SMOKES.items():
        status = health.get(name, {}).get("status", "off")
        msg = (health.get(name, {}).get("message") or "")[:80]
        backend = health.get(name, {}).get("active_backend")

        if status == "off":
            results.append(SmokeResult(name, "skip", "disabled / not installed"))
            continue
        if status == "ok" or (status == "warn" and name == "linkedin"):
            # LinkedIn is warn when MCP/Jina ready (session lives in MCP host)
            if name in ("twitter", "reddit", "linkedin"):
                results.append(fn(backend))
            else:
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
