# -*- coding: utf-8 -*-
"""Shared OpenCLI probe helpers for Tier 1 channels.

opencli doctor / list are expensive — results are cached for one doctor run.
Call clear_opencli_cache() at the start of check_all().
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

from agent_atlas.probe import probe_command, which

_doctor_cache: Optional[Tuple[str, str, Optional[dict]]] = None
_list_cache: Optional[str] = None


def clear_opencli_cache() -> None:
    global _doctor_cache, _list_cache
    _doctor_cache = None
    _list_cache = None


def opencli_installed() -> bool:
    return which("opencli") is not None


def opencli_doctor() -> Tuple[str, str, Optional[dict]]:
    """Return (status, message, parsed_json_or_none). Cached per process until cleared."""
    global _doctor_cache
    if _doctor_cache is not None:
        return _doctor_cache

    if not opencli_installed():
        _doctor_cache = (
            "off",
            "OpenCLI not installed — npm i -g @jackwener/opencli + Chrome bridge (docs/tier1.md)",
            None,
        )
        return _doctor_cache

    # opencli has no --json doctor; one text call, shared via cache across channels
    probe = probe_command("opencli", ["doctor"], timeout=25, package="@jackwener/opencli")
    if probe.status == "missing":
        _doctor_cache = ("off", probe.hint, None)
        return _doctor_cache
    out = probe.output
    low = out.lower()
    # opencli often exits 0 even when extension is missing — parse text
    if "[fail]" in low or "[missing]" in low or "not connected" in low:
        _doctor_cache = (
            "warn",
            "OpenCLI installed — connect Chrome bridge extension (docs/tier1.md)",
            None,
        )
        return _doctor_cache
    if "extension" in low and ("not" in low or "missing" in low):
        _doctor_cache = (
            "warn",
            "OpenCLI installed — connect Chrome bridge extension (docs/tier1.md)",
            None,
        )
        return _doctor_cache
    if probe.ok and ("[ok]" in low or "ready" in low or "healthy" in low):
        if "connectivity: failed" in low:
            _doctor_cache = (
                "warn",
                "OpenCLI installed — Chrome bridge not connected (docs/tier1.md)",
                None,
            )
            return _doctor_cache
        _doctor_cache = ("ok", "OpenCLI doctor OK — Chrome bridge ready", None)
        return _doctor_cache
    if probe.ok:
        _doctor_cache = ("warn", "OpenCLI installed — run: opencli doctor", None)
        return _doctor_cache
    _doctor_cache = ("warn", f"OpenCLI present — {probe.hint or 'run opencli doctor'}", None)
    return _doctor_cache


def _opencli_list_output() -> str:
    global _list_cache
    if _list_cache is not None:
        return _list_cache
    if not opencli_installed():
        _list_cache = ""
        return _list_cache
    probe = probe_command("opencli", ["list"], timeout=20)
    _list_cache = probe.output if probe.ok else ""
    return _list_cache


def opencli_has_adapter(name: str) -> bool:
    """Best-effort: opencli list mentions adapter name (uses cached list)."""
    out = _opencli_list_output()
    if not out:
        # If list failed/empty but doctor is ok, assume common adapters exist
        st, _, _ = opencli_doctor()
        return st == "ok" and name.lower() in {
            "linkedin",
            "reddit",
            "twitter",
            "facebook",
            "instagram",
        }
    return bool(re.search(rf"\b{re.escape(name)}\b", out, re.I))
