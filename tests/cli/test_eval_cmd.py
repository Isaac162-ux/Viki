"""Tests for the ``viki eval`` CLI commands."""

from __future__ import annotations

from click.testing import CliRunner

from viki.cli import cli


class TestEvalCLI:
    """Tests for the eval command group."""

    def test_eval_group_exists(self):
        """``viki eval --help`` shows run/compare/report/list subcommands."""
        result = CliRunner().invoke(cli, ["eval", "--help"])
        assert result.exit_code == 0
        assert "run" in result.output
        assert "compare" in result.output
        assert "report" in result.output
        assert "list" in result.output

    def test_eval_list_benchmarks(self):
        """``viki eval list`` exits 0 and outputs benchmark names."""
        result = CliRunner().invoke(cli, ["eval", "list"])
        assert result.exit_code == 0
        assert "supergpqa" in result.output
        assert "gaia" in result.output
        assert "frames" in result.output
        assert "wildchat" in result.output
        # Should also show backends
        assert "viki-direct" in result.output
        assert "viki-agent" in result.output

    def test_eval_run_missing_args(self):
        """``viki eval run`` without required args fails gracefully."""
        result = CliRunner().invoke(cli, ["eval", "run"])
        # Should fail because neither --config nor --benchmark/--model given
        assert result.exit_code != 0
        assert "config" in result.output.lower() or "benchmark" in result.output.lower()
