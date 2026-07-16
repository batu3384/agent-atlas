# -*- coding: utf-8 -*-
from agent_atlas.channels.exa import ExaChannel
from agent_atlas.channels.github import GitHubChannel
from agent_atlas.channels.rss import RssChannel
from agent_atlas.channels.social import (
    FacebookChannel,
    InstagramChannel,
    LinkedInChannel,
    RedditChannel,
    TwitterChannel,
)
from agent_atlas.channels.web import WebChannel
from agent_atlas.channels.youtube import YouTubeChannel

_CHANNELS = [
    WebChannel(),
    ExaChannel(),
    YouTubeChannel(),
    GitHubChannel(),
    RssChannel(),
    TwitterChannel(),
    RedditChannel(),
    FacebookChannel(),
    InstagramChannel(),
    LinkedInChannel(),
]


def get_all_channels():
    return list(_CHANNELS)
