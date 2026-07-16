"""Auth commands — clear progress, no silent Default-profile trap."""

from __future__ import annotations

import click
from rich.console import Console

from ..auth import (
    CREDENTIAL_FILE,
    clear_credential,
    diagnose_missing_cookies,
    extract_browser_credential,
    get_credential,
)
from ..browser import reset_isolated_profile
from ..chrome_paths import chrome_process_running, configured_profile_name
from ..client import LinkedInClient
from . import _common as common

console = Console(stderr=True)


@click.command()
@click.option("--force", is_flag=True, help="Re-sync cookies and reset isolated browser profile.")
@click.option("--skip-validate", is_flag=True, help="Only sync cookies; skip headless probe.")
def login(force: bool, skip_validate: bool) -> None:
    """Sync LinkedIn cookies from Atlas Chrome profile and validate session."""
    profile = configured_profile_name()
    console.print(f"[dim]Profile:[/dim] {profile or '(none — check ~/.agent-atlas/config.yaml)'}")

    if chrome_process_running():
        console.print("[yellow]Google Chrome is still running[/yellow] — quit with Cmd+Q, then retry.")
        raise SystemExit(1)

    if force:
        console.print("[dim]Clearing old credentials…[/dim]")
        clear_credential()
        reset_isolated_profile()

    console.print("[dim]Reading LinkedIn cookies from Chrome…[/dim]")
    cred = extract_browser_credential()
    if not cred:
        console.print("[red]No LinkedIn cookies in configured profile[/red]")
        console.print(diagnose_missing_cookies(profile))
        raise SystemExit(1)

    console.print(f"[green]Cookies found[/green] — {len(cred.cookies)} from {cred.source}")

    if skip_validate:
        console.print("[green]Saved[/green] (validation skipped)")
        return

    console.print("[dim]Validating with headless browser (30–90s, please wait)…[/dim]")
    with LinkedInClient(cred) as client:
        try:
            info = client.validate_session()
        except Exception as e:
            console.print(f"[yellow]Cookies found but LinkedIn rejected them:[/yellow] {e}")
            console.print(diagnose_missing_cookies(profile))
            raise SystemExit(1) from e
    console.print(
        f"[green]Login OK[/green] — {info.get('cookie_count', '?')} cookies"
        + (f" (@{info['username']})" if info.get("username") else "")
    )


@click.command()
def logout() -> None:
    """Clear saved cookies and isolated browser profile."""
    clear_credential()
    reset_isolated_profile()
    console.print("[green]Credentials cleared[/green]")


@common.structured_options
@click.command()
@click.option("--quick", is_flag=True, help="Check credential file only (no browser launch).")
def status(as_json: bool, as_yaml: bool, quick: bool) -> None:
    """Check authentication status."""
    fmt = common.resolve_output_format(as_json=as_json, as_yaml=as_yaml)
    cred = get_credential()
    if not cred:
        err = diagnose_missing_cookies(configured_profile_name())
        if fmt:
            common.emit_structured(common.error_payload("AUTH", err.splitlines()[0]), fmt)
        else:
            console.print("[yellow]Not authenticated[/yellow]")
            console.print(err)
        raise SystemExit(1)

    if quick:
        data = {
            "authenticated": True,
            "username": cred.username,
            "cookie_count": len(cred.cookies),
            "credential_file": str(CREDENTIAL_FILE),
            "source": cred.source,
            "profile": cred.profile or configured_profile_name(),
            "mode": "quick",
        }
        if fmt:
            common.emit_structured(common.success_payload(data), fmt)
        else:
            console.print(
                f"[green]OK[/green] @{cred.username or '?'} "
                f"({len(cred.cookies)} cookies, profile={data['profile']}, quick)"
            )
        return

    try:
        with LinkedInClient(cred) as client:
            me = client.validate_session()
        data = {
            "authenticated": True,
            "username": cred.username or me.get("username"),
            "cookie_count": len(cred.cookies),
            "credential_file": str(CREDENTIAL_FILE),
            "source": cred.source,
            "profile": cred.profile or configured_profile_name(),
            **me,
        }
        if fmt:
            common.emit_structured(common.success_payload(data), fmt)
        else:
            user = cred.username or me.get("username") or "?"
            console.print(f"[green]OK[/green] @{user} ({len(cred.cookies)} cookies)")
    except Exception as e:
        if fmt:
            common.emit_structured(common.error_payload("AUTH", str(e)[:200]), fmt)
        else:
            console.print(f"[red]AUTH:[/red] {e}")
        raise SystemExit(1) from e
