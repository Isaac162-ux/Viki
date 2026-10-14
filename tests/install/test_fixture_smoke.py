"""Smoke test that the tmp_viki_home fixture works."""

from __future__ import annotations

from pathlib import Path

from viki.core import config as config_mod


def test_fixture_redirects_default_config_dir(tmp_viki_home: Path) -> None:
    assert config_mod.DEFAULT_CONFIG_DIR == tmp_viki_home
    assert tmp_viki_home.exists()
    assert (tmp_viki_home / ".state").exists()
    assert (tmp_viki_home / ".state" / "models").exists()


def test_fixture_redirects_config_path(tmp_viki_home: Path) -> None:
    assert config_mod.DEFAULT_CONFIG_PATH == tmp_viki_home / "config.toml"
