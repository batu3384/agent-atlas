# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from agent_atlas.channels.base import Channel
from agent_atlas.probe import http_ok


class WebChannel(Channel):
    name = "web"
    description = "Web pages (Jina Reader)"
    backends = ["Jina Reader"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        try:
            return bool(urlparse(url).scheme in ("http", "https"))
        except Exception:
            return False

    def check(self, config=None):
        # Light probe: Jina root should respond
        if http_ok("https://r.jina.ai/", timeout=8):
            self.active_backend = "Jina Reader"
            return "ok", "curl -s https://r.jina.ai/URL"
        self.active_backend = None
        return "warn", "Jina Reader unreachable — check network"
