# -*- coding: utf-8 -*-
"""Tier 1 social channels — login / browser session required."""

from urllib.parse import urlparse

from agent_atlas.channels.base import Channel
from agent_atlas.opencli_status import (
    opencli_doctor,
    opencli_installed,
)
from agent_atlas.probe import http_ok, probe_command


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
        twitter_warn: str | None = None
        if probe.status != "missing":
            if probe.ok and "ok: true" in probe.output:
                self.active_backend = "twitter-cli"
                return "ok", 'twitter-cli authenticated — twitter search "q" -n 10'
            twitter_warn = "twitter-cli installed — set TWITTER_AUTH_TOKEN + TWITTER_CT0 (docs/tier1.md)"

        # Fallback: OpenCLI (even when twitter-cli exists but is unauthenticated)
        if opencli_installed():
            st, msg, _ = opencli_doctor()
            if st == "ok":
                self.active_backend = "OpenCLI"
                return "ok", 'OpenCLI ready — opencli twitter search "q" -f yaml'
            if twitter_warn:
                self.active_backend = "twitter-cli"
                return "warn", f"{twitter_warn}; OpenCLI — {msg}"
            self.active_backend = "OpenCLI"
            return "warn", f"OpenCLI present — {msg}"

        if twitter_warn:
            self.active_backend = "twitter-cli"
            return "warn", twitter_warn

        self.active_backend = None
        return "off", "Install twitter-cli (pipx) or OpenCLI — docs/tier1.md"


class RedditChannel(Channel):
    name = "reddit"
    description = "Reddit"
    backends = ["rdt-cli", "OpenCLI"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        return "reddit.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        from agent_atlas.config import Config as Cfg
        from agent_atlas.rdt_status import ensure_rdt_session, rdt_installed

        config = config or Cfg()

        # Preferred: rdt-cli (cookie on disk — no live Chrome bridge)
        if rdt_installed():
            ok, msg = ensure_rdt_session(config)
            self.active_backend = "rdt-cli"
            if ok:
                return "ok", msg
            rdt_warn = msg

            # Fallback: OpenCLI when bridge is up
            if opencli_installed():
                st, omsg, _ = opencli_doctor()
                if st == "ok":
                    self.active_backend = "OpenCLI"
                    return "ok", 'OpenCLI ready — opencli reddit search "q" -f yaml'
                return "warn", f"{rdt_warn}; OpenCLI — {omsg}"

            return "warn", rdt_warn

        if opencli_installed():
            st, msg, _ = opencli_doctor()
            self.active_backend = "OpenCLI"
            if st == "ok":
                return "ok", 'OpenCLI ready — opencli reddit search "q" -f yaml'
            return "warn", f"OpenCLI present — {msg}"

        self.active_backend = None
        return "off", "Reddit: uv tool install rdt-cli + Atlas profile login — docs/tier1.md"


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
    backends = ["linkedin-mcp", "Jina Reader"]
    tier = 1

    def can_handle(self, url: str) -> bool:
        return "linkedin.com" in urlparse(url).netloc.lower()

    def check(self, config=None):
        from agent_atlas.linkedin_mcp import linkedin_mcp_status

        # Reach-style: linkedin-scraper-mcp for auth research; Jina for public pages
        mcp_st, mcp_msg, _ = linkedin_mcp_status()
        if mcp_st == "ok":
            self.active_backend = "linkedin-mcp"
            return "ok", mcp_msg

        # MCP missing/off/error → still offer public Jina when reachable
        if http_ok("https://r.jina.ai/", timeout=8):
            self.active_backend = "Jina Reader"
            prefix = "Public LinkedIn via Jina"
            if mcp_st == "error":
                return (
                    "warn",
                    f"{prefix} — curl -s https://r.jina.ai/https://www.linkedin.com/in/… "
                    f"| MCP probe failed: {mcp_msg}",
                )
            return (
                "warn",
                f"{prefix} — curl -s https://r.jina.ai/https://www.linkedin.com/in/… "
                f"| Full access: {mcp_msg}",
            )
        if mcp_st == "error":
            self.active_backend = None
            return "error", mcp_msg
        self.active_backend = None
        return "off", f"LinkedIn: {mcp_msg}"
