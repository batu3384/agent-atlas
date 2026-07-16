"""li CLI entry point."""

from __future__ import annotations

import click

from . import __version__
from .commands import auth, jobs, people_search, profile


@click.group()
@click.version_option(version=__version__, prog_name="li")
def cli() -> None:
    """li — LinkedIn in your terminal (cookie auth, no live Chrome)."""


cli.add_command(auth.login)
cli.add_command(auth.logout)
cli.add_command(auth.status)
cli.add_command(people_search.people_search)
cli.add_command(jobs.search_jobs)
cli.add_command(profile.profile_read)


if __name__ == "__main__":
    cli()
