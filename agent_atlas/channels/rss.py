# -*- coding: utf-8 -*-
from agent_atlas.channels.base import Channel


class RssChannel(Channel):
    name = "rss"
    description = "RSS / Atom feeds"
    backends = ["feedparser"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        u = url.lower()
        return any(x in u for x in (".xml", "/feed", "/rss", "atom"))

    def check(self, config=None):
        try:
            import feedparser  # noqa: F401

            self.active_backend = "feedparser"
            return "ok", "feedparser available (Python)"
        except ImportError:
            self.active_backend = None
            return "off", "feedparser missing — pip install feedparser"
