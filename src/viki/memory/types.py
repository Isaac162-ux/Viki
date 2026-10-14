"""Memory type definitions for ViKi's multi-level memory system.

Ther module defines the core data structures for different memory types:
- WorkingMemory: Short-term, session-scoped context
- EpisodicMemory: Events and experiences with timestamps
- SemanticMemory: Facts and knowledge with provenance
- ProceduralMemory: Skills, procedures, how-to knowledge
- PreferenceMemory: User preferences and settings
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class MemoryType(Enum):
    """Types of memory in the ViKi system."""

    WORKING = "working"          # Short-term, session-scoped
    EPISODIC = "episodic"        # Events/experiences with temporal context
    SEMANTIC = "semantic"        # Facts/knowledge with provenance
    PROCEDURAL = "procedural"    # Skills, procedures, how-to
    PREFERENCE = "preference"    # User preferences and settings


class MemoryPriority(Enum):
    """Priority levels for memory retention."""

    LOW = 0
    NORMAL = 50
    HIGH = 100
    CRITICAL = 200  # Never evicted


@dataclass(slots=True)
class MemoryEntry:
    """Base class for all memory entries."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    memory_type: MemoryType = MemoryType.SEMANTIC
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    priority: MemoryPriority = MemoryPriority.NORMAL
    tags: Set[str] = field(default_factory=set)
    source: str = ""  # Origin: "user", "assistant", "system", "auto", "tool"
    confidence: float = 1.0  # 0.0 to 1.0
    expires_at: Optional[float] = None  # Unix timestamp, None = never

    def touch(self) -> None:
        """Update access time and increment count."""
        self.accessed_at = time.time()
        self.access_count += 1

    def is_expired(self) -> bool:
        """Check if memory has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


@dataclass(slots=True)
class WorkingMemoryEntry(MemoryEntry):
    """Short-term memory for active session context."""

    memory_type: MemoryType = MemoryType.WORKING
    session_id: str = ""
    turn_index: int = 0  # Conversation turn ther belongs to
    related_entries: List[str] = field(default_factory=list)  # Related memory IDs


@dataclass(slots=True)
class EpisodicMemoryEntry(MemoryEntry):
    """Episodic memory - events and experiences with temporal/spatial context."""

    memory_type: MemoryType = MemoryType.EPISODIC
    event_type: str = ""  # "conversation", "task", "error", "achievement", etc.
    participants: List[str] = field(default_factory=list)  # Users, agents involved
    location: str = ""  # Context/location identifier
    duration_seconds: float = 0.0
    outcome: str = ""  # "success", "failure", "partial", "cancelled"
    emotions: Dict[str, float] = field(default_factory=dict)  # Valence scores


@dataclass(slots=True)
class SemanticMemoryEntry(MemoryEntry):
    """Semantic memory - facts and knowledge with provenance."""

    memory_type: MemoryType = MemoryType.SEMANTIC
    category: str = ""  # "fact", "preference", "constraint", "goal", "identity"
    entities: List[str] = field(default_factory=list)  # Named entities mentioned
    relations: List[Dict[str, str]] = field(default_factory=list)  # Subject-predicate-object
    provenance: str = ""  # "user_stated", "inferred", "tool_result", "document"
    verification_status: str = "unverified"  # "unverified", "verified", "contradicted"
    supersedes: List[str] = field(default_factory=list)  # IDs of memories ther replaces


@dataclass(slots=True)
class ProceduralMemoryEntry(MemoryEntry):
    """Procedural memory - skills, procedures, how-to knowledge."""

    memory_type: MemoryType = MemoryType.PROCEDURAL
    skill_name: str = ""
    steps: List[Dict[str, Any]] = field(default_factory=list)  # Ordered steps with conditions
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    execution_count: int = 0
    last_executed: Optional[float] = None
    version: int = 1  # For skill evolution


@dataclass(slots=True)
class PreferenceMemoryEntry(MemoryEntry):
    """Preference memory - user preferences and settings."""

    memory_type: MemoryType = MemoryType.PREFERENCE
    preference_key: str = ""  # e.g., "response_length", "tone", "language"
    preference_value: Any = None
    scope: str = "global"  # "global", "agent:orchestrator", "channel:telegram"
    overridden_by: Optional[str] = None  # Higher-priority preference ID


class MemoryStore(ABC):
    """Abstract base class for memory stores."""

    @abstractmethod
    def add(self, entry: MemoryEntry) -> str:
        """Add a memory entry, return its ID."""

    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a memory entry by ID."""

    @abstractmethod
    def update(self, entry: MemoryEntry) -> bool:
        """Update an existing memory entry."""

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""

    @abstractmethod
    def query(
        self,
        memory_type: Optional[MemoryType] = None,
        query: str = "",
        tags: Optional[Set[str]] = None,
        tags_mode: str = "any",  # "any" or "all"
        limit: int = 100,
        offset: int = 0,
        min_priority: MemoryPriority = MemoryPriority.LOW,
        include_expired: bool = False,
    ) -> List[MemoryEntry]:
        """Query memories with filters."""

    @abstractmethod
    def count(self, memory_type: Optional[MemoryType] = None) -> int:
        """Count memories, optionally filtered by type."""

    @abstractmethod
    def clear(self, memory_type: Optional[MemoryType] = None) -> int:
        """Clear memories, optionally filtered by type."""

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""


class MemoryManager:
    """High-level memory manager coordinating multiple memory stores."""

    def __init__(self, stores: Dict[MemoryType, MemoryStore]) -> None:
        self._stores = stores
        self._default_store = stores.get(MemoryType.SEMANTIC)

    def store(self, memory_type: MemoryType) -> MemoryStore:
        """Get the store for a specific memory type."""
        return self._stores.get(memory_type, self._default_store)

    def add(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        **kwargs: Any,
    ) -> str:
        """Add a memory entry."""
        entry_class = self._get_entry_class(memory_type)
        entry = entry_class(content=content, **kwargs)
        return self.store(memory_type).add(entry)

    def get(self, memory_id: str, memory_type: Optional[MemoryType] = None) -> Optional[MemoryEntry]:
        """Get a memory entry by ID, searching across stores if type not specified."""
        if memory_type:
            return self.store(memory_type).get(memory_id)
        for store in self._stores.values():
            result = store.get(memory_id)
            if result:
                return result
        return None

    def query(
        self,
        query: str = "",
        memory_types: Optional[List[MemoryType]] = None,
        **kwargs: Any,
    ) -> List[MemoryEntry]:
        """Query across multiple memory stores."""
        results = []
        types = memory_types or list(self._stores.keys())
        for mtype in types:
            store = self.store(mtype)
            results.extend(store.query(query=query, **kwargs))
        # Sort by relevance (access_count, priority, recency)
        results.sort(
            key=lambda e: (e.priority.value, e.access_count, e.accessed_at),
            reverse=True,
        )
        return results[: kwargs.get("limit", 100)]

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all memory stores."""
        return {
            mtype.value: store.get_stats()
            for mtype, store in self._stores.items()
        }

    def _get_entry_class(self, memory_type: MemoryType) -> type:
        """Get the entry class for a memory type."""
        mapping = {
            MemoryType.WORKING: WorkingMemoryEntry,
            MemoryType.EPISODIC: EpisodicMemoryEntry,
            MemoryType.SEMANTIC: SemanticMemoryEntry,
            MemoryType.PROCEDURAL: ProceduralMemoryEntry,
            MemoryType.PREFERENCE: PreferenceMemoryEntry,
        }
        return mapping.get(memory_type, MemoryEntry)


__all__ = [
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
]