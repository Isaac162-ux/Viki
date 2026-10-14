"""Skill source resolvers — Hermes, OpenClaw, generic GitHub."""

from viki.skills.sources.base import ResolvedSkill, SourceResolver
from viki.skills.sources.github import GitHubResolver
from viki.skills.sources.hermes import HERMES_REPO_URL, HermesResolver
from viki.skills.sources.openclaw import OPENCLAW_REPO_URL, OpenClawResolver

__all__ = [
    "GitHubResolver",
    "HERMES_REPO_URL",
    "HermesResolver",
    "OPENCLAW_REPO_URL",
    "OpenClawResolver",
    "ResolvedSkill",
    "SourceResolver",
]
