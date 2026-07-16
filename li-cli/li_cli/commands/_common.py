"""Shared command helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import click
import yaml
from rich.console import Console

from ..auth import Credential, get_credential
from ..client import LinkedInClient
from ..exceptions import AuthError, LiCliError

console = Console(stderr=True)
_SCHEMA_VERSION = "1"


def resolve_output_format(*, as_json: bool, as_yaml: bool) -> str | None:
    if as_json and as_yaml:
        raise click.UsageError("Use only one of --json or --yaml.")
    if as_json:
        return "json"
    if as_yaml:
        return "yaml"
    mode = os.getenv("OUTPUT", "auto").strip().lower()
    if mode in ("json", "yaml"):
        return mode
    if not sys.stdout.isatty():
        return "yaml"
    return None


def success_payload(data: Any) -> dict[str, Any]:
    return {"ok": True, "schema_version": _SCHEMA_VERSION, "data": data}


def error_payload(code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "schema_version": _SCHEMA_VERSION,
        "error": {"code": code, "message": message},
    }


def emit_structured(payload: dict[str, Any], fmt: str) -> None:
    if fmt == "json":
        click.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        click.echo(yaml.dump(payload, allow_unicode=True, default_flow_style=False, sort_keys=False))


def structured_options(cmd):
    cmd = click.option("--yaml", "as_yaml", is_flag=True)(cmd)
    cmd = click.option("--json", "as_json", is_flag=True)(cmd)
    return cmd


def require_cred() -> Credential:
    cred = get_credential()
    if not cred:
        console.print("[yellow]Not logged in[/yellow] — run [bold]li login[/bold]")
        sys.exit(1)
    return cred


def run_action(action, *, as_json: bool = False, as_yaml: bool = False):
    fmt = resolve_output_format(as_json=as_json, as_yaml=as_yaml)
    try:
        cred = require_cred()
        with LinkedInClient(cred) as client:
            data = action(client)
        if fmt:
            emit_structured(success_payload(data), fmt)
        else:
            click.echo(yaml.dump(data, allow_unicode=True, default_flow_style=False))
        return data
    except AuthError as e:
        if fmt:
            emit_structured(error_payload("AUTH", str(e)), fmt)
        else:
            console.print(f"[red]AUTH:[/red] {e}")
        sys.exit(1)
    except LiCliError as e:
        if fmt:
            emit_structured(error_payload("API", str(e)), fmt)
        else:
            console.print(f"[red]ERROR:[/red] {e}")
        sys.exit(1)
