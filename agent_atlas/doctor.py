# -*- coding: utf-8 -*-
"""Environment health check across all channels."""

from __future__ import annotations

from typing import Dict

from agent_atlas.channels import get_all_channels
from agent_atlas.config import Config


def check_all(config: Config | None = None) -> Dict[str, dict]:
    from agent_atlas.config import apply_runtime_env
    from agent_atlas.opencli_status import clear_opencli_cache

    config = config or Config()
    apply_runtime_env(config)
    clear_opencli_cache()

    disabled = config.disabled_channels()
    results = {}
    for ch in get_all_channels():
        if ch.name in disabled:
            results[ch.name] = {
                "status": "off",
                "name": ch.description,
                "message": "disabled by user config (disabled_channels)",
                "tier": ch.tier,
                "backends": ch.backends,
                "active_backend": None,
            }
            continue
        try:
            status, message = ch.check(config)
            active = getattr(ch, "active_backend", None)
        except Exception as e:  # noqa: BLE001
            status, message, active = "error", f"check failed: {e}", None
        results[ch.name] = {
            "status": status,
            "name": ch.description,
            "message": message,
            "tier": ch.tier,
            "backends": ch.backends,
            "active_backend": active,
        }
    return results


def format_report(results: Dict[str, dict]) -> str:
    lines = [
        "Agent Atlas status",
        "=" * 40,
        "Legend: ok | warn (needs login/config) | off | error",
        "",
        "Tier 0 — ready after install:",
    ]
    for key, r in results.items():
        if r["tier"] != 0:
            continue
        mark = {"ok": "OK", "warn": "!", "off": "X", "error": "E"}.get(r["status"], "?")
        backend = f" [{r['active_backend']}]" if r.get("active_backend") else ""
        lines.append(f"  [{mark}] {r['name']}{backend} — {r['message']}")

    lines.append("")
    lines.append("Tier 1 — needs login:")
    for key, r in results.items():
        if r["tier"] != 1:
            continue
        mark = {"ok": "OK", "warn": "!", "off": "X", "error": "E"}.get(r["status"], "?")
        backend = f" [{r['active_backend']}]" if r.get("active_backend") else ""
        lines.append(f"  [{mark}] {r['name']}{backend} — {r['message']}")

    ok = sum(1 for r in results.values() if r["status"] == "ok")
    lines.append("")
    lines.append(f"Ready: {ok}/{len(results)} channels fully ok")
    return "\n".join(lines)
