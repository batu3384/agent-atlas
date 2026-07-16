# -*- coding: utf-8 -*-
"""Minimal unit tests — config env map, disabled channels, opencli parse, smoke exit."""

from __future__ import annotations

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
