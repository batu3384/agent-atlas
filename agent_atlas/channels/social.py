# -*- coding: utf-8 -*-
"""Tier 1 social channels — login / browser session required."""

from urllib.parse import urlparse

from agent_atlas.channels.base import Channel
from agent_atlas.opencli_status import opencli_doctor, opencli_has_adapter, opencli_installed
from agent_atlas.probe import http_ok, probe_command, which


class TwitterChannel(Channel):
    name = "twitter"
    description = "Twitter / X"
    backends = ["twitter-cli", "OpenCLI"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        d = urlparse(url).netloc.lower()
        return "x.com" in d or "twitter.com" in d

    def check(self, config=None):
        # Preferred: twitter-cli authenticated
        probe = probe_command("twitter", ["status"], timeout=12, package="twitter-cli")
        if probe.status != "missing":
            if probe.ok and "ok: true" in probe.output:
                self.active_backend = "twitter-cli"
                return "ok", "twitter-cli authenticated — twitter search \"q\" -n 10"
            if "not_authenticated" in probe.output or probe.status in ("broken", "ok", "timeout"):
                self.active_backend = "twitter-cli"
                return (
                    "warn",
                    "twitter-cli installed — set TWITTER_AUTH_TOKEN + TWITTER_CT0 (docs/tier1.md)",
                )

        # Fallback: OpenCLI
        if opencli_installed():
            st, msg, _ = opencli_doctor()
            self.active_backend = "OpenCLI"
            if st == "ok":
                return "ok", 'OpenCLI ready — opencli twitter search "q" -f yaml'
            return "warn", f"OpenCLI present — {msg}"

        self.active_backend = None
        return "off", "Install twitter-cli (pipx) or OpenCLI — docs/tier1.md"


class RedditChannel(Channel):
    name = "reddit"
    description = "Reddit"
    backends = ["OpenCLI", "rdt-cli"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        return "reddit.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        if opencli_installed():
            st, msg, _ = opencli_doctor()
            self.active_backend = "OpenCLI"
            if st == "ok":
                return "ok", 'OpenCLI ready — opencli reddit search "q" -f yaml'
            return "warn", f"OpenCLI present — {msg}"
        if which("rdt"):
            self.active_backend = "rdt-cli"
            return "warn", "rdt-cli found — needs Reddit cookies (docs/tier1.md)"
        self.active_backend = None
        return "off", "Reddit: install OpenCLI + Chrome login — docs/tier1.md"


class FacebookChannel(Channel):
    name = "facebook"
    description = "Facebook"
    backends = ["OpenCLI"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        return "facebook.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        if not opencli_installed():
            self.active_backend = None
            return "off", "Facebook: install OpenCLI — docs/tier1.md"
        st, msg, _ = opencli_doctor()
        self.active_backend = "OpenCLI"
        if st == "ok":
            return "ok", 'OpenCLI ready — opencli facebook search "q" -f yaml'
        return "warn", f"OpenCLI present — {msg}"


class InstagramChannel(Channel):
    name = "instagram"
    description = "Instagram"
    backends = ["OpenCLI"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        return "instagram.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        if not opencli_installed():
            self.active_backend = None
            return "off", "Instagram: install OpenCLI — docs/tier1.md"
        st, msg, _ = opencli_doctor()
        self.active_backend = "OpenCLI"
        if st == "ok":
            return "ok", 'OpenCLI ready — opencli instagram search "q" -f yaml'
        return "warn", f"OpenCLI present — {msg}"


class LinkedInChannel(Channel):
    name = "linkedin"
    description = "LinkedIn"
    backends = ["OpenCLI", "Jina Reader", "linkedin-mcp"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        return "linkedin.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        if opencli_installed() and opencli_has_adapter("linkedin"):
            st, msg, _ = opencli_doctor()
            self.active_backend = "OpenCLI"
            if st == "ok":
                return "ok", "OpenCLI LinkedIn adapter ready"
            return "warn", f"OpenCLI LinkedIn — {msg}"

        if http_ok("https://r.jina.ai/", timeout=8):
            self.active_backend = "Jina Reader"
            return (
                "warn",
                "Public pages via Jina — curl -s https://r.jina.ai/https://www.linkedin.com/…",
            )
        self.active_backend = None
        return "off", "LinkedIn: OpenCLI, Jina, or linkedin-mcp — docs/tier1.md"
