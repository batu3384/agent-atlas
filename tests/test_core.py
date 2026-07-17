# -*- coding: utf-8 -*-
"""Minimal unit tests — config env map, disabled channels, opencli parse, smoke exit."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agent_atlas.config import Config, apply_runtime_env
from agent_atlas.opencli_status import clear_opencli_cache, opencli_doctor
from agent_atlas.smoke import SmokeResult, smoke_exit_code


@pytest.fixture()
def tmp_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    cfg_path = tmp_path / "config.yaml"
    monkeypatch.delenv("TWITTER_CHROME_PROFILE", raising=False)
    monkeypatch.delenv("TWITTER_BROWSER", raising=False)
    monkeypatch.delenv("OPENCLI_PROFILE", raising=False)
    return Config(config_path=cfg_path)


def test_apply_runtime_env_from_yaml(tmp_config: Config, monkeypatch: pytest.MonkeyPatch) -> None:
    tmp_config.set("twitter_chrome_profile", "Profile 3")
    tmp_config.set("twitter_browser", "chrome")
    tmp_config.set("opencli_profile", "atlas")

    applied = apply_runtime_env(tmp_config, overwrite=True)
    assert applied["TWITTER_CHROME_PROFILE"] == "Profile 3"
    assert applied["TWITTER_BROWSER"] == "chrome"
    assert applied["OPENCLI_PROFILE"] == "atlas"
    assert os.environ["TWITTER_CHROME_PROFILE"] == "Profile 3"
    assert os.environ["OPENCLI_PROFILE"] == "atlas"


def test_apply_runtime_env_respects_existing_shell(
    tmp_config: Config, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TWITTER_CHROME_PROFILE", "Default")
    tmp_config.set("twitter_chrome_profile", "Profile 3")
    applied = apply_runtime_env(tmp_config, overwrite=False)
    assert "TWITTER_CHROME_PROFILE" not in applied
    assert os.environ["TWITTER_CHROME_PROFILE"] == "Default"


def test_disabled_channels_csv_and_list(tmp_config: Config) -> None:
    tmp_config.set("disabled_channels", "facebook,instagram")
    assert tmp_config.disabled_channels() == {"facebook", "instagram"}
    tmp_config.set("disabled_channels", ["facebook", "instagram"])
    assert tmp_config.disabled_channels() == {"facebook", "instagram"}


def test_opencli_doctor_parses_missing_extension(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_opencli_cache()

    class FakeProbe:
        status = "ok"
        ok = True
        output = (
            "[OK] Daemon: running\n"
            "[MISSING] Extension: not connected\n"
            "[FAIL] Connectivity: failed\n"
        )
        hint = ""

    monkeypatch.setattr(
        "agent_atlas.opencli_status.opencli_installed", lambda: True
    )
    monkeypatch.setattr(
        "agent_atlas.opencli_status.probe_command",
        lambda *a, **k: FakeProbe(),
    )
    status, msg, _ = opencli_doctor()
    assert status == "warn"
    assert "bridge" in msg.lower() or "extension" in msg.lower()
    # cache hit
    status2, _, _ = opencli_doctor()
    assert status2 == status


def test_smoke_exit_code() -> None:
    assert smoke_exit_code([SmokeResult("web", "pass", "ok")]) == 0
    assert smoke_exit_code([SmokeResult("web", "skip", "n/a")]) == 0
    assert smoke_exit_code([SmokeResult("web", "fail", "boom")]) == 1


def test_rdt_status_parses_authenticated() -> None:
    from agent_atlas.rdt_status import _parse_yaml_status

    text = "ok: true\nschema_version: '1'\ndata:\n  authenticated: true\n  username: testuser\n"
    data = _parse_yaml_status(text)
    assert data.get("authenticated") is True
    assert data.get("username") == "testuser"


def test_li_status_parses_authenticated() -> None:
    from agent_atlas.li_status import _parse_yaml_status

    text = "ok: true\nschema_version: '1'\ndata:\n  authenticated: true\n  username: johndoe\n"
    data = _parse_yaml_status(text)
    assert data.get("authenticated") is True
    assert data.get("username") == "johndoe"


def test_li_status_parses_error_payload() -> None:
    from agent_atlas.li_status import _parse_yaml_status

    text = "ok: false\nerror:\n  code: AUTH\n  message: session expired\n"
    data = _parse_yaml_status(text)
    assert data.get("authenticated") is False
    assert "expired" in data.get("error", "")


def test_chrome_cookie_file_from_config(tmp_config: Config) -> None:
    from agent_atlas.chrome_profile import chrome_cookie_file

    tmp_config.set("twitter_chrome_profile", "Profile 3")
    path = chrome_cookie_file(tmp_config)
    assert path is not None
    assert path.name == "Cookies"
    assert str(path).endswith("Profile 3/Cookies")


def test_apply_runtime_env_linkedin_profile(tmp_config: Config) -> None:
    tmp_config.set("linkedin_chrome_profile", "Profile 3")
    applied = apply_runtime_env(tmp_config, overwrite=True)
    assert applied["LI_CHROME_PROFILE"] == "Profile 3"


def test_apply_runtime_env_reddit_profile(tmp_config: Config) -> None:
    tmp_config.set("reddit_chrome_profile", "Profile 3")
    applied = apply_runtime_env(tmp_config, overwrite=True)
    assert applied["REDDIT_CHROME_PROFILE"] == "Profile 3"


def test_linkedin_uses_mcp_when_configured(monkeypatch) -> None:
    from agent_atlas.channels.social import LinkedInChannel

    ch = LinkedInChannel()
    monkeypatch.setattr(
        "agent_atlas.linkedin_mcp.linkedin_mcp_configured", lambda: True
    )
    monkeypatch.setattr(
        "agent_atlas.linkedin_mcp.linkedin_mcp_status",
        lambda: (
            "warn",
            "linkedin-mcp ready — use MCP tools",
            {"configured": True, "uvx": True},
        ),
    )
    status, msg = ch.check()
    assert status == "warn"
    assert ch.active_backend == "linkedin-mcp"
    assert "linkedin-mcp" in msg


def test_linkedin_falls_back_to_jina(monkeypatch) -> None:
    from agent_atlas.channels.social import LinkedInChannel

    ch = LinkedInChannel()
    monkeypatch.setattr(
        "agent_atlas.linkedin_mcp.linkedin_mcp_configured", lambda: False
    )
    monkeypatch.setattr(
        "agent_atlas.linkedin_mcp.linkedin_mcp_status",
        lambda: ("off", "LinkedIn MCP not configured", {"configured": False}),
    )
    monkeypatch.setattr(
        "agent_atlas.channels.social.http_ok", lambda *a, **k: True
    )
    status, msg = ch.check()
    assert status == "warn"
    assert ch.active_backend == "Jina Reader"
    assert "jina" in msg.lower()


def test_linkedin_mcp_config_detection(tmp_path, monkeypatch) -> None:
    from agent_atlas import linkedin_mcp as lm

    cfg = tmp_path / "mcp.json"
    cfg.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "linkedin": {
                        "command": "uvx",
                        "args": ["linkedin-scraper-mcp@latest"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(lm, "_mcp_config_paths", lambda: [cfg])
    assert lm.linkedin_mcp_configured() is True

    empty = tmp_path / "empty.json"
    empty.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(lm, "_mcp_config_paths", lambda: [empty])
    assert lm.linkedin_mcp_configured() is False


def test_linkedin_off_without_mcp_or_jina(monkeypatch) -> None:
    from agent_atlas.channels.social import LinkedInChannel

    ch = LinkedInChannel()
    monkeypatch.setattr(
        "agent_atlas.linkedin_mcp.linkedin_mcp_configured", lambda: False
    )
    monkeypatch.setattr(
        "agent_atlas.linkedin_mcp.linkedin_mcp_status",
        lambda: ("off", "LinkedIn MCP not configured — login hint", None),
    )
    monkeypatch.setattr(
        "agent_atlas.channels.social.http_ok", lambda *a, **k: False
    )
    status, msg = ch.check()
    assert status == "off"
    assert ch.active_backend is None
    assert "LinkedIn" in msg


def test_compare_versions() -> None:
    from agent_atlas.update_check import compare_versions

    assert compare_versions("0.1.0", "0.2.0") == "newer"
    assert compare_versions("0.1.0", "0.1.0") == "same"
    assert compare_versions("0.2.0", "0.1.0") == "older"


def test_twitter_falls_back_to_opencli_when_unauth(monkeypatch) -> None:
    from agent_atlas.channels.social import TwitterChannel
    from agent_atlas.probe import ProbeResult

    ch = TwitterChannel()

    def fake_probe(*a, **k):
        return ProbeResult(
            status="ok",
            output="ok: false\nerror: not_authenticated\n",
            hint="",
        )

    monkeypatch.setattr(
        "agent_atlas.channels.social.probe_command", fake_probe
    )
    monkeypatch.setattr(
        "agent_atlas.channels.social.opencli_installed", lambda: True
    )
    monkeypatch.setattr(
        "agent_atlas.channels.social.opencli_doctor",
        lambda: ("ok", "bridge ready", None),
    )
    status, msg = ch.check()
    assert status == "ok"
    assert ch.active_backend == "OpenCLI"
    assert "opencli twitter" in msg

