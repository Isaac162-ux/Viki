"""External-framework subprocess backends (Hermes Agent, OpenClaw)."""

from viki.evals.backends.external.hermes_agent import HermesBackend
from viki.evals.backends.external.openclaw import OpenClawBackend

__all__ = ["HermesBackend", "OpenClawBackend"]
