# -*- coding: utf-8 -*-
"""Tests for li-cli parsers and chrome paths."""

from __future__ import annotations

from li_cli.chrome_paths import chrome_root, configured_profile
from li_cli.parsers.people_search import parse_people_search_html
from li_cli.parsers.profile import parse_profile_html


def test_parse_people_search_html() -> None:
    html = '''
    <a href="/in/johndoe/">John</a>
    <span aria-hidden="true">John Doe</span>
    <a href="/in/janedoe/">Jane</a>
    '''
    rows = parse_people_search_html(html, limit=5)
    assert len(rows) == 2
    assert rows[0]["profile_url"].endswith("/in/johndoe/")


def test_parse_profile_html_minimal() -> None:
    html = '<title>Jane Doe | LinkedIn</title><h1>Jane Doe</h1>'
    out = parse_profile_html(html, profile_url="https://www.linkedin.com/in/janedoe/")
    assert out["name"] == "Jane Doe"
    assert "janedoe" in out["profile_url"]


def test_chrome_paths() -> None:
    assert chrome_root().name == "Chrome" or "Chrome" in str(chrome_root())
