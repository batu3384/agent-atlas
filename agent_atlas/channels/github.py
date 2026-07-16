# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from agent_atlas.channels.base import Channel
from agent_atlas.probe import probe_command


class GitHubChannel(Channel):
    name = "github"
    description = "GitHub (gh CLI)"
    backends = ["gh"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        return "github.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        probe = probe_command("gh", ["--version"], timeout=10, package="gh")
        if probe.status == "missing":
            self.active_backend = None
            return "off", "gh not installed — brew install gh"
        if not probe.ok:
            self.active_backend = None
            return "error", probe.hint
        auth = probe_command("gh", ["auth", "status"], timeout=10)
        self.active_backend = "gh"
        if auth.ok or "Logged in" in auth.output:
            return "ok", "gh CLI ready (authenticated)"
        return "warn", "gh installed but not logged in — run: gh auth login"
