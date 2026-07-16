"""People search command."""

from __future__ import annotations

import click

from . import _common as common


@common.structured_options
@click.command("people-search")
@click.argument("query")
@click.option("-n", "--limit", default=5, show_default=True, type=click.IntRange(1, 10))
def people_search(query: str, limit: int, as_json: bool, as_yaml: bool) -> None:
    """Search LinkedIn people by keyword (HTTP + cookies, no Chrome bridge)."""
    common.run_action(
        lambda c: c.people_search(query, limit=limit),
        as_json=as_json,
        as_yaml=as_yaml,
    )
