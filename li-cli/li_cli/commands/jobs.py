"""Job search command."""

from __future__ import annotations

import click

from . import _common as common


@common.structured_options
@click.command("search-jobs")
@click.argument("query")
@click.option("-n", "--limit", default=10, show_default=True, type=click.IntRange(1, 25))
def search_jobs(query: str, limit: int, as_json: bool, as_yaml: bool) -> None:
    """Search LinkedIn jobs via Voyager API."""
    common.run_action(
        lambda c: c.search_jobs(query, limit=limit),
        as_json=as_json,
        as_yaml=as_yaml,
    )
