"""Operators — persistent, scheduled autonomous agents."""

from viki.operators.loader import load_operator
from viki.operators.manager import OperatorManager
from viki.operators.types import OperatorManifest

__all__ = ["OperatorManifest", "OperatorManager", "load_operator"]
