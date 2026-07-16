# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from agent_atlas.channels.base import Channel
from agent_atlas.probe import probe_command


class YouTubeChannel(Channel):
    name = "youtube"
    description = "YouTube transcripts"
    backends = ["yt-dlp"]
    tier = 0

    def can_handle(self, url: str) -> bool:
        d = urlparse(url).netloc.lower()
        return "youtube.com" in d or "youtu.be" in d

    def check(self, config=None):
        probe = probe_command("yt-dlp", ["--version"], timeout=15, package="yt-dlp")
        if probe.status == "missing":
            self.active_backend = None
            return "off", "yt-dlp not installed — pip install yt-dlp"
        if probe.ok:
            self.active_backend = "yt-dlp"
            return "ok", f"yt-dlp {probe.output.splitlines()[0] if probe.output else 'ok'}"
        self.active_backend = None
        return "error", probe.hint
