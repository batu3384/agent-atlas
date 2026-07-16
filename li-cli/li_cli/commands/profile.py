"""Profile read command."""

from __future__ import annotations

import click

from . import _common as common


@common.structured_options
@click.command("profile-read")
@click.argument("profile_url")
def profile_read(profile_url: str, as_json: bool, as_yaml: bool) -> None:
    """Read a public LinkedIn profile page."""
    common.run_action(
        lambda c: c.profile_read(profile_url),
        as_json=as_json,
        as_yaml=as_yaml,
    )
