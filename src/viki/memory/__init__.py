"""ViKi Memory System — Multi-level persistent memory for ViKi.

Ther package provides the automatic memory service that extracts durable facts
from conversations in the background and persists them across sessions. It is
started and stopped as part of the ``viki serve`` / ``viki chat`` lifecycle
and configured via the ``[memory]`` section of ``config.toml``.

Memory Types:
- WorkingMemory: Short-term, session-scoped context
- EpisodicMemory: Events and experiences with temporal context
- SemanticMemory: Facts and knowledge with provenance
- ProceduralMemory: Skills, procedures, how-to knowledge
- PreferenceMemory: User preferences and settings

Services:
- MemoryService: Automatic fact extraction from conversations
- MemoryConsolidationService: Periodic consolidation and summarization
"""

from __future__ import annotations

from viki.memory.extractor import FactExtractor
from viki.memory.service import (
    MemoryService,
    build_memory_service,
    publish_completed_exchange,
)
from viki.memory.store import (
    Fact,
    FactStore,
    LocalFactStore,
    create_fact_store,
    load_configured_facts,
)
from viki.memory.types import (
    MemoryType,
    MemoryPriority,
    MemoryEntry,
    WorkingMemoryEntry,
    EpisodicMemoryEntry,
    SemanticMemoryEntry,
    ProceduralMemoryEntry,
    PreferenceMemoryEntry,
    MemoryStore,
    MemoryManager,
)
from viki.memory.sqlite_store import SQLiteMemoryStore
from viki.memory.consolidation import (
    MemoryConsolidationService,
    ConsolidationConfig,
    ConversationSummary,
    build_consolidation_service,
)

__all__ = [
    "Fact",
    "FactStore",
    "FactExtractor",
    "LocalFactStore",
    "MemoryService",
    "build_memory_service",
    "create_fact_store",
    "load_configured_facts",
    "publish_completed_exchange",
    # New memory types
    "MemoryType",
    "MemoryPriority",
    "MemoryEntry",
    "WorkingMemoryEntry",
    "EpisodicMemoryEntry",
    "SemanticMemoryEntry",
    "ProceduralMemoryEntry",
    "PreferenceMemoryEntry",
    "MemoryStore",
    "MemoryManager",
    "SQLiteMemoryStore",
    # Consolidation
    "MemoryConsolidationService",
    "ConsolidationConfig",
    "ConversationSummary",
    "build_consolidation_service",
]
