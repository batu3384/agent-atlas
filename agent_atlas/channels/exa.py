# -*- coding: utf-8 -*-
from agent_atlas.channels.base import Channel
from agent_atlas.probe import probe_command, which


class ExaChannel(Channel):
    name = "exa"
    description = "Web search (Exa via mcporter)"
    backends = ["mcporter+Exa"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return False  # search-only

    def check(self, config=None):
        if not which("mcporter"):
            self.active_backend = None
            return "off", "mcporter not installed — run: npm i -g mcporter"
        # List servers; Exa may be named variously
        probe = probe_command("mcporter", ["list"], timeout=20, package="mcporter")
        if probe.status == "missing":
            self.active_backend = None
            return "off", probe.hint
        if probe.status != "ok":
            self.active_backend = None
            return "warn", f"mcporter present but list failed: {probe.hint}"
        out = probe.output.lower()
        if "exa" in out:
            self.active_backend = "mcporter+Exa"
            return "ok", "mcporter call 'exa.web_search_exa(query: \"…\", numResults: 5)'"
        self.active_backend = None
        return "warn", "mcporter OK but Exa not configured — see docs/install.md"
