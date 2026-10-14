"""Tests for the env-aware ViKi home-directory resolver.

Covers the single-root consolidation: ``$VIKI_HOME`` >
``$XDG_DATA_HOME/viki`` > ``~/.viki``, backward compatibility
(no env => exactly ``~/.viki``), and the source-tree rejection guard.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from viki.core import paths


def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every env var that influences home resolution."""
    for var in (
        "VIKI_HOME",
        "XDG_DATA_HOME",
        "XDG_CONFIG_HOME",
        "XDG_CACHE_HOME",
    ):
        monkeypatch.delenv(var, raising=False)


class TestGetConfigDir:
    """Precedence and backward compatibility of get_config_dir()."""

    def test_default_when_unset_is_legacy_dir(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Backward-compat: with nothing set, the resolved dir is exactly the
        # historical ~/.viki so existing installs are untouched.
        _clear_env(monkeypatch)
        assert paths.get_config_dir() == (Path.home() / ".viki").resolve()

    def test_respects_viki_home(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        custom = tmp_path / "viki"
        monkeypatch.setenv("VIKI_HOME", str(custom))
        assert paths.get_config_dir() == custom.resolve()

    def test_respects_xdg_data_home(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        # Single nested 'viki' dir under XDG_DATA_HOME.
        assert paths.get_config_dir() == (tmp_path / "viki").resolve()

    def test_viki_home_wins_over_xdg(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        viki = tmp_path / "viki_wins"
        monkeypatch.setenv("VIKI_HOME", str(viki))
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg_loses"))
        assert paths.get_config_dir() == viki.resolve()

    def test_expands_user_in_viki_home(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        monkeypatch.setenv("VIKI_HOME", "~/relocated-viki")
        assert paths.get_config_dir() == (Path.home() / "relocated-viki").resolve()

    def test_returns_absolute_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        monkeypatch.setenv("VIKI_HOME", str(tmp_path / "rel"))
        assert paths.get_config_dir().is_absolute()


class TestDerivedDirs:
    """config_path / data_dir / cache_dir all hang off the single root."""

    def test_config_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _clear_env(monkeypatch)
        monkeypatch.setenv("VIKI_HOME", str(tmp_path / "viki"))
        assert paths.get_config_path() == (tmp_path / "viki" / "config.toml").resolve()

    def test_data_dir_equals_config_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        monkeypatch.setenv("VIKI_HOME", str(tmp_path / "viki"))
        assert paths.get_data_dir() == paths.get_config_dir()

    def test_cache_dir_is_nested_cache(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        monkeypatch.setenv("VIKI_HOME", str(tmp_path / "viki"))
        assert paths.get_cache_dir() == (tmp_path / "viki" / "cache").resolve()

    def test_cache_dir_under_xdg(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        assert paths.get_cache_dir() == (tmp_path / "viki" / "cache").resolve()


class TestSourceTreeRejection:
    """A home pointing inside the repo must fail loudly (REVIEW.md)."""

    def test_rejects_path_inside_source_tree(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _clear_env(monkeypatch)
        source_root = paths._find_source_root()
        assert source_root is not None  # We must be running inside the repo.
        monkeypatch.setenv("VIKI_HOME", str(source_root / "junk_dir"))
        with pytest.raises(paths.ConfigurationError, match="inside the source tree"):
            paths.get_config_dir()


class TestLegacyConstantsHonorEnv:
    """The legacy DEFAULT_CONFIG_* names route through the env-aware resolver.

    This is the exact split-brain bug from #462: the constant used to ignore
    VIKI_HOME entirely. The constant is resolved once at import (the
    install-script model, where the env is set before the process starts), and
    every instance-level default goes through ``get_config_dir()`` so it honors
    the override. ``DEFAULT_CONFIG_DIR`` stays a real attribute so existing
    tests can ``monkeypatch.setattr`` it.
    """

    def test_constant_matches_resolver_at_import(self) -> None:
        from viki.core import config

        # The constant is the import-time resolution of the same function.
        assert config.DEFAULT_CONFIG_DIR == paths.get_config_dir()
        assert config.DEFAULT_CONFIG_PATH == paths.get_config_path()

    def test_constant_is_a_real_settable_attribute(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Install/CLI tests monkeypatch this attribute directly; it must be a
        # real module attribute (not __getattr__-only) for setattr/undo to work.
        from viki.core import config

        monkeypatch.setattr(config, "DEFAULT_CONFIG_DIR", tmp_path / "patched")
        assert config.DEFAULT_CONFIG_DIR == tmp_path / "patched"

    def test_dataclass_defaults_reflect_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Config dataclass field defaults must resolve under the override at
        # instantiation time, not freeze ~/.viki at import.
        _clear_env(monkeypatch)
        from viki.core.config import SessionConfig, StorageConfig

        monkeypatch.setenv("VIKI_HOME", str(tmp_path / "viki"))
        root = (tmp_path / "viki").resolve()
        assert StorageConfig().db_path == str(root / "memory.db")
        assert SessionConfig().db_path == str(root / "sessions.db")

    def test_downstream_consumer_honors_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # End-to-end: a non-config subsystem (credentials) resolves under the
        # custom root, proving the override is no longer split-brain.
        _clear_env(monkeypatch)
        from viki.core import credentials

        monkeypatch.setenv("VIKI_HOME", str(tmp_path / "viki"))
        assert (
            credentials._default_path()
            == (tmp_path / "viki" / "credentials.toml").resolve()
        )

    def test_constant_never_resolves_to_the_real_developer_home(self) -> None:
        """Regression for #787: DEFAULT_CONFIG_DIR is resolved once, at the
        first import of viki.core.config anywhere in the test
        session -- which happens via tests/conftest.py, before any test
        body runs. If conftest.py doesn't set VIKI_HOME before that
        import, this constant (and the ~45 modules that reference it)
        permanently binds to the developer's real ~/.viki for the
        rest of the run, so tests touching e.g. AgentConfigEvolver or
        LearningOrchestrator read/write real files there.

        This test verifies that the test environment correctly sets
        VIKI_HOME to a temporary directory before the first import,
        so the constant binds to a temp directory instead of the
        developer's real ~/.viki. It also ensures we don't accidentally
        resolve to the old OpenJarvis path (~/.openjarvis).
        """
        from viki.core.config import DEFAULT_CONFIG_DIR

        real_home = (Path.home() / ".viki").resolve()
        old_openjarvis_home = (Path.home() / ".openjarvis").resolve()
        test_home = Path(os.environ.get("VIKI_HOME", "")).resolve()
        
        # In test environment, DEFAULT_CONFIG_DIR should be the temp test directory
        # (set by conftest.py before first import), not the real home
        assert DEFAULT_CONFIG_DIR == test_home
        # Should NOT resolve to the old OpenJarvis path
        assert DEFAULT_CONFIG_DIR != old_openjarvis_home
        assert "VIKI_CONFIG" not in os.environ
