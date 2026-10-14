"""Benchmarking framework for Viki inference engines."""

from __future__ import annotations

from viki.bench._stubs import BaseBenchmark, BenchmarkResult, BenchmarkSuite
from viki.core.registry import BenchmarkRegistry


def ensure_registered() -> None:
    """Ensure all benchmark implementations are registered."""
    from viki.bench.energy import ensure_registered as _reg_energy
    from viki.bench.latency import ensure_registered as _reg_latency
    from viki.bench.throughput import ensure_registered as _reg_throughput

    _reg_latency()
    _reg_throughput()
    _reg_energy()


# Trigger registration on import
ensure_registered()

__all__ = [
    "BaseBenchmark",
    "BenchmarkRegistry",
    "BenchmarkResult",
    "BenchmarkSuite",
    "ensure_registered",
]
