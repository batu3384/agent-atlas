# -*- coding: utf-8 -*-
"""Agent Atlas CLI — install, doctor, skill, uninstall."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from agent_atlas import __version__
from agent_atlas.config import Config


def _run(
    cmd: list[str],
    check: bool = False,
    *,
    timeout: float = 120,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(
            cmd,
            124,
            stdout=e.stdout or "",
            stderr=(e.stderr or "") + f"\ntimeout after {timeout}s",
        )
    except OSError as e:
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr=str(e))


def _which(name: str) -> str | None:
    return shutil.which(name)


def cmd_doctor(as_json: bool = False) -> int:
    from agent_atlas.doctor import check_all, format_report

    results = check_all(Config())
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        try:
            from rich.console import Console

            Console().print(format_report(results))
        except ImportError:
            print(format_report(results))
    return 0


def cmd_install(*, safe: bool = False, dry_run: bool = False, channels: str = "") -> int:
    """Install Tier 0 upstream tools + optional Tier 1."""
    steps = []

    def note(msg: str) -> None:
        print(msg)
        steps.append(msg)

    note(f"Agent Atlas v{__version__} install (safe={safe} dry_run={dry_run})")

    # Config dir: only create on real install (safe/dry-run = probe-only)
    if safe or dry_run:
        note(f"SAFE/DRY: would use config dir {Config.CONFIG_DIR} (not creating)")
    else:
        cfg = Config()
        note(f"Config dir: {cfg.config_dir}")

    # Python deps already from pip install; ensure yt-dlp on PATH
    if not _which("yt-dlp"):
        if dry_run or safe:
            note("NEED: yt-dlp (pip install yt-dlp)")
        else:
            note("Installing yt-dlp via pip…")
            r = _run([sys.executable, "-m", "pip", "install", "yt-dlp"], timeout=180)
            if r.returncode == 0:
                note("OK: yt-dlp")
            else:
                note(f"WARN: yt-dlp install failed: {(r.stderr or r.stdout or '').strip()}")
    else:
        note("OK: yt-dlp")

    if not _which("gh"):
        note("NEED: gh CLI — brew install gh  (or https://cli.github.com)")
    else:
        note("OK: gh")

    if not _which("node") and not _which("npm"):
        note("NEED: Node.js — for mcporter (brew install node)")
    else:
        note("OK: node/npm")

    if not _which("mcporter"):
        if dry_run or safe:
            note("NEED: mcporter — npm i -g mcporter")
        else:
            if _which("npm"):
                note("Installing mcporter…")
                r = _run(["npm", "i", "-g", "mcporter"])
                if r.returncode != 0:
                    note(f"WARN: mcporter install failed: {r.stderr.strip()}")
                else:
                    note("OK: mcporter installed")
            else:
                note("NEED: npm to install mcporter")
    else:
        note("OK: mcporter")

    # Exa MCP via mcporter (free hosted endpoint, no API key)
    if _which("mcporter"):
        if dry_run or safe:
            note("NEED: mcporter config add exa https://mcp.exa.ai/mcp")
        else:
            note("Configuring Exa MCP in mcporter (home + project)…")
            for scope in ("home", "project"):
                r = _run(
                    [
                        "mcporter",
                        "config",
                        "add",
                        "exa",
                        "https://mcp.exa.ai/mcp",
                        "--scope",
                        scope,
                    ]
                )
                # idempotent-ish: already-added still ok for doctor
                if r.returncode == 0:
                    note(f"OK: exa ({scope})")
                else:
                    err = (r.stderr or r.stdout or "").strip()
                    if "already" in err.lower() or "exists" in err.lower():
                        note(f"OK: exa already configured ({scope})")
                    else:
                        note(f"WARN: exa {scope}: {err or 'failed'}")
    note("Web read needs no install: curl -s https://r.jina.ai/URL")

    # Skill registration (not in --safe / --dry-run)
    if safe:
        note("SAFE: skip skill install (probe-only)")
    elif dry_run:
        note("DRY-RUN: would install SKILL.md to agent skill dirs")
    else:
        cmd_skill_install()

    wanted = {c.strip().lower() for c in channels.split(",") if c.strip()}
    want_all = "all" in wanted
    want_opencli = want_all or bool(
        wanted & {"opencli", "reddit", "facebook", "instagram", "twitter"}
    )
    want_twitter = want_all or "twitter" in wanted
    want_reddit = want_all or "reddit" in wanted
    want_linkedin = want_all or "linkedin" in wanted

    if want_opencli or want_twitter or want_reddit or want_linkedin:
        note("Tier 1 — see docs/tier1.md (use secondary accounts)")

    if want_opencli:
        if dry_run or safe:
            note("NEED: npm i -g @jackwener/opencli + Chrome bridge extension")
        elif _which("opencli"):
            note("OK: opencli")
        elif _which("npm"):
            note("Installing @jackwener/opencli…")
            r = _run(["npm", "i", "-g", "@jackwener/opencli"])
            if r.returncode == 0:
                note("OK: opencli installed — next: Chrome extension + opencli doctor")
            else:
                note(f"WARN: opencli install failed: {(r.stderr or r.stdout or '').strip()}")
        else:
            note("NEED: npm to install OpenCLI")

    if want_twitter:
        if dry_run or safe:
            note("NEED: uv tool install twitter-cli  (or pipx) — auth: docs/tier1.md")
        elif _which("twitter"):
            note("OK: twitter-cli")
        elif _which("uv"):
            note("Installing twitter-cli via uv tool…")
            r = _run(["uv", "tool", "install", "twitter-cli"])
            if r.returncode == 0:
                note("OK: twitter-cli — set TWITTER_AUTH_TOKEN + TWITTER_CT0")
            else:
                note(f"WARN: twitter-cli: {(r.stderr or r.stdout or '').strip()}")
        elif _which("pipx"):
            note("Installing twitter-cli via pipx…")
            r = _run(["pipx", "install", "twitter-cli"])
            if r.returncode == 0:
                note("OK: twitter-cli — set TWITTER_AUTH_TOKEN + TWITTER_CT0")
            else:
                note(f"WARN: twitter-cli: {(r.stderr or r.stdout or '').strip()}")
        else:
            note("NEED: uv tool install twitter-cli")

    if want_reddit:
        if dry_run or safe:
            note("NEED: uv tool install rdt-cli — login in Atlas Chrome, then agent-atlas doctor")
        elif _which("rdt"):
            note("OK: rdt-cli")
        elif _which("uv"):
            note("Installing rdt-cli via uv tool…")
            r = _run(["uv", "tool", "install", "rdt-cli"])
            if r.returncode == 0:
                note("OK: rdt-cli — Reddit login in Atlas Chrome profile (docs/tier1.md)")
            else:
                note(f"WARN: rdt-cli: {(r.stderr or r.stdout or '').strip()}")
        elif _which("pipx"):
            note("Installing rdt-cli via pipx…")
            r = _run(["pipx", "install", "rdt-cli"])
            if r.returncode == 0:
                note("OK: rdt-cli — Reddit login in Atlas Chrome profile (docs/tier1.md)")
            else:
                note(f"WARN: rdt-cli: {(r.stderr or r.stdout or '').strip()}")
        else:
            note("NEED: uv tool install rdt-cli")

    if want_linkedin:
        if dry_run or safe:
            note(
                "NEED: uvx linkedin-scraper-mcp@latest --login  "
                "+ add MCP server to Cursor mcp.json (docs/tier1.md)"
            )
        else:
            note("LinkedIn (Reach-style):")
            note("  1. uvx linkedin-scraper-mcp@latest --login")
            note("  2. Add to ~/.cursor/mcp.json:")
            note('     "linkedin": {"command":"uvx","args":["linkedin-scraper-mcp@latest"]}')
            note("  3. Public pages: curl -s https://r.jina.ai/https://www.linkedin.com/…")
            note("  See docs/tier1.md")
            if _which("uvx"):
                note("OK: uvx present — run login when ready")
            else:
                note("NEED: install uv (https://docs.astral.sh/uv/) for uvx")

    if want_opencli or want_twitter:
        note("Manual step: Chrome login (secondary accounts) + opencli doctor")

    note("Done. Run: agent-atlas doctor")
    return 0


def _skill_source() -> Path:
    # Packaged skill next to this file's parent / skill/SKILL.md or repo root
    here = Path(__file__).resolve().parent
    candidates = [
        here / "skill" / "SKILL.md",
        here.parent / "SKILL.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError("SKILL.md not found")


def _skill_targets() -> list[Path]:
    """Prefer agents SSOT only; skip dirs that are the same inode (symlinks)."""
    home = Path.home()
    agents = home / ".agents" / "skills" / "agent-atlas"
    candidates = [
        agents,
        home / ".claude" / "skills" / "agent-atlas",
        home / ".cursor" / "skills" / "agent-atlas",
    ]
    seen: set[int] = set()
    out: list[Path] = []
    for p in candidates:
        parent = p.parent
        try:
            key = parent.resolve().stat().st_ino
        except OSError:
            key = hash(str(parent))
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out or [agents]


def cmd_skill_install() -> int:
    src = _skill_source()
    written = 0
    for target_dir in _skill_targets():
        # If parent is a symlink to agents, only write once to agents
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            dest = target_dir / "SKILL.md"
            shutil.copy2(src, dest)
            # Copy references if present
            ref_src = src.parent / "references"
            if ref_src.is_dir():
                ref_dst = target_dir / "references"
                if ref_dst.exists():
                    shutil.rmtree(ref_dst)
                shutil.copytree(ref_src, ref_dst)
            print(f"Skill installed: {dest}")
            written += 1
        except OSError as e:
            print(f"Skip {target_dir}: {e}")
    # Prefer single agents SSOT — if .cursor/skills is symlink, duplicate is ok
    return 0 if written else 1


def cmd_skill_uninstall() -> int:
    for target_dir in _skill_targets():
        if target_dir.exists():
            shutil.rmtree(target_dir)
            print(f"Removed {target_dir}")
    return 0


def cmd_uninstall(*, dry_run: bool = False, keep_config: bool = False) -> int:
    paths = [
        Path.home() / ".agents" / "skills" / "agent-atlas",
        Path.home() / ".claude" / "skills" / "agent-atlas",
        Path.home() / ".cursor" / "skills" / "agent-atlas",
    ]
    if not keep_config:
        paths.append(Path.home() / ".agent-atlas")
    for p in paths:
        if not p.exists():
            continue
        if dry_run:
            print(f"Would remove: {p}")
        else:
            shutil.rmtree(p)
            print(f"Removed: {p}")
    print("Python package: pip uninstall agent-atlas-cli  (or: uv tool uninstall agent-atlas-cli)")
    print("Note: rdt-cli credentials stay in ~/.config/rdt-cli/ (owned by rdt-cli)")
    return 0


def cmd_configure(key: str, value: str) -> int:
    cfg = Config()
    cfg.set(key.replace("-", "_"), value)
    cfg.apply_runtime_env(overwrite=True)
    print(f"Set {key} in {cfg.config_path}")
    return 0


def cmd_smoke(as_json: bool = False) -> int:
    from agent_atlas.smoke import format_smoke, results_as_dict, run_smoke, smoke_exit_code

    results = run_smoke(Config())
    if as_json:
        print(json.dumps(results_as_dict(results), indent=2, ensure_ascii=False))
    else:
        print(format_smoke(results))
    return smoke_exit_code(results)


def cmd_check_update(*, as_json: bool = False) -> int:
    from agent_atlas.update_check import check_update, current_version, fetch_latest_version

    code, msg = check_update()
    if as_json:
        latest, detail = fetch_latest_version()
        print(
            json.dumps(
                {
                    "current": current_version(),
                    "latest": latest,
                    "detail": detail,
                    "message": msg,
                    "update_available": code == 2,
                },
                indent=2,
            )
        )
    else:
        print(msg)
    return 0 if code != 2 else 2


def cmd_watch(*, as_json: bool = False) -> int:
    """Quick doctor summary + update hint (for scheduled tasks)."""
    from agent_atlas.doctor import check_all
    from agent_atlas.update_check import check_update

    results = check_all(Config())
    ok = sum(1 for r in results.values() if r["status"] == "ok")
    warn = sum(1 for r in results.values() if r["status"] == "warn")
    off = sum(1 for r in results.values() if r["status"] in ("off", "error"))
    upd_code, upd_msg = check_update()

    if as_json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "warn": warn,
                    "off": off,
                    "channels": {
                        k: {"status": v["status"], "active_backend": v.get("active_backend")}
                        for k, v in results.items()
                    },
                    "update": {"code": upd_code, "message": upd_msg},
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(f"Agent Atlas watch — ready={ok} warn={warn} off={off}")
        for name, r in results.items():
            if r["status"] == "ok":
                continue
            mark = {"warn": "!", "off": "X", "error": "E"}.get(r["status"], "?")
            print(f"  [{mark}] {name}: {r['message'][:90]}")
        print(upd_msg)
    return 1 if warn or (upd_code == 2) else 0


def main(argv: list[str] | None = None) -> None:
    from agent_atlas.config import ConfigError, apply_runtime_env

    try:
        apply_runtime_env()
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(2)

    parser = argparse.ArgumentParser(
        prog="agent-atlas",
        description="Search and research the open web for your AI agent",
    )
    parser.add_argument("--version", action="version", version=f"Agent Atlas v{__version__}")
    sub = parser.add_subparsers(dest="command")

    p_doc = sub.add_parser("doctor", help="Check channel availability")
    p_doc.add_argument("--json", action="store_true")

    p_smoke = sub.add_parser("smoke", help="One real research call per ready channel")
    p_smoke.add_argument("--json", action="store_true")

    p_watch = sub.add_parser("watch", help="Quick health + update check")
    p_watch.add_argument("--json", action="store_true")

    p_upd = sub.add_parser("check-update", help="Check GitHub for newer version")
    p_upd.add_argument("--json", action="store_true")

    p_inst = sub.add_parser("install", help="Install upstream tools + skill")
    p_inst.add_argument("--safe", action="store_true")
    p_inst.add_argument("--dry-run", action="store_true")
    p_inst.add_argument(
        "--channels",
        default="",
        help="Optional: twitter,reddit,linkedin,opencli,all",
    )

    p_conf = sub.add_parser("configure", help="Set a config value")
    p_conf.add_argument("key")
    p_conf.add_argument("value")

    p_skill = sub.add_parser("skill", help="Manage SKILL.md registration")
    g = p_skill.add_mutually_exclusive_group(required=True)
    g.add_argument("--install", action="store_true")
    g.add_argument("--uninstall", action="store_true")

    p_un = sub.add_parser("uninstall", help="Remove config and skills")
    p_un.add_argument("--dry-run", action="store_true")
    p_un.add_argument("--keep-config", action="store_true")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "doctor":
        code = cmd_doctor(as_json=args.json)
    elif args.command == "smoke":
        code = cmd_smoke(as_json=args.json)
    elif args.command == "watch":
        code = cmd_watch(as_json=args.json)
    elif args.command == "check-update":
        code = cmd_check_update(as_json=args.json)
    elif args.command == "install":
        code = cmd_install(safe=args.safe, dry_run=args.dry_run, channels=args.channels)
    elif args.command == "configure":
        code = cmd_configure(args.key, args.value)
    elif args.command == "skill":
        code = cmd_skill_install() if args.install else cmd_skill_uninstall()
    elif args.command == "uninstall":
        code = cmd_uninstall(dry_run=args.dry_run, keep_config=args.keep_config)
    else:
        parser.print_help()
        code = 1
    sys.exit(code)


if __name__ == "__main__":
    main()
