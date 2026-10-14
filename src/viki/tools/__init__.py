"""Tools primitive — tool system with ABC interface and built-in tools."""

from __future__ import annotations

from viki.tools._stubs import BaseTool, ToolExecutor, ToolSpec

# Import built-in tools to trigger @ToolRegistry.register() decorators.
# Each is wrapped in try/except so the package loads even before the
# individual tool modules are created.
try:
    import viki.tools.calculator  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.think  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.retrieval  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.llm_tool  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.file_read  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.web_search  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.weather  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.fx_macro  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.code_interpreter  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.code_interpreter_docker  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.repl  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.storage_tools  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.mcp_adapter  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.channel_tools  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.http_request  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.docker_shell_exec  # noqa: F401
    import viki.tools.shell_exec  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.memory_manage  # noqa: F401
except ImportError:
    pass
try:
    import viki.tools.user_profile_manage  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.skill_manage  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.file_write  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.apply_patch  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.git_tool  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.db_query  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.pdf_tool  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.image_tool  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.audio_tool  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.knowledge_tools  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.text_to_speech  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.digest_collect  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.scan_chunks  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.knowledge_sql  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.apple_calendar  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.knowledge_search  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.browser  # noqa: F401
    import viki.tools.browser_axtree  # noqa: F401
except ImportError:
    pass

try:
    import viki.tools.proactive_tools  # noqa: F401
except ImportError:
    pass

__all__ = ["BaseTool", "ToolExecutor", "ToolSpec"]
