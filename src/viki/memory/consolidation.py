"""Memory consolidation and conversation summarization services."""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, List, Optional, Dict

from viki.core.events import Event, EventBus, EventType
from viki.core.types import Message, Role
from viki.memory.store import FactStore, create_fact_store
from viki.engine._stubs import InferenceEngine

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ConversationSummary:
    """Summary of a conversation."""
    conversation_id: str
    summary: str
    key_points: List[str]
    topics: List[str]
    sentiment: str  # positive, negative, neutral
    message_count: int
    token_count: int
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class ConsolidationConfig:
    """Configuration for memory consolidation."""
    enabled: bool = True
    interval_hours: int = 24
    max_conversations_per_run: int = 100
    min_messages_for_summary: int = 5
    max_summary_length: int = 500
    consolidation_model: str = ""  # Model to use for consolidation
    max_facts_per_topic: int = 50
    min_fact_confidence: float = 0.7


class MemoryConsolidationService:
    """Background service for memory consolidation and conversation summarization."""

    def __init__(
        self,
        config: ConsolidationConfig,
        store: Any,  # FactStore
        engine: InferenceEngine,
        model: str,
        *,
        event_bus: Optional[Any] = None,
        max_queue: int = 100,
    ) -> None:
        self.config = config
        self._store = store
        self._engine = engine
        self._model = model
        self._event_bus = event_bus
        self._queue: "asyncio.Queue[Dict[str, Any]]" = asyncio.Queue(maxsize=max_queue)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._stats = {
            "consolidations": 0,
            "summaries_created": 0,
            "facts_consolidated": 0,
            "errors": 0,
        }

    async def start(self) -> None:
        """Start the consolidation service."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Memory consolidation service started")

    async def stop(self) -> None:
        """Stop the consolidation service."""
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Memory consolidation service stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    async def queue_consolidation(self, conversation_id: str, messages: List[Message]) -> bool:
        """Queue a conversation for consolidation."""
        if not self._running:
            return False
        try:
            await self._queue.put({
                "type": "consolidate",
                "conversation_id": conversation_id,
                "messages": messages,
                "timestamp": time.time(),
            })
            return True
        except asyncio.QueueFull:
            logger.warning("Consolidation queue full; dropping request")
            return False

    async def _loop(self) -> None:
        """Main consolidation loop."""
        # Periodic consolidation
        consolidation_interval = self.config.interval_hours * 3600
        next_consolidation = time.time() + consolidation_interval

        while self._running:
            try:
                # Check for queued consolidations
                try:
                    job = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                    await self._process_job(job)
                except asyncio.TimeoutError:
                    pass

                # Periodic consolidation
                if time.time() >= next_consolidation:
                    await self._run_periodic_consolidation()
                    next_consolidation = time.time() + consolidation_interval

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Consolidation loop error: {e}")
                self._stats["errors"] += 1
                await asyncio.sleep(5)

    async def _process_job(self, job: Dict[str, Any]) -> None:
        """Process a consolidation job."""
        job_type = job.get("type", "consolidate")
        
        if job_type == "consolidate":
            await self._consolidate_conversation(
                job["conversation_id"],
                job["messages"]
            )
        elif job_type == "summarize":
            await self._summarize_conversation(
                job["conversation_id"],
                job["messages"]
            )

    async def _run_periodic_consolidation(self) -> None:
        """Run periodic consolidation of all conversations."""
        logger.info("Running periodic memory consolidation")
        # Ther would scan all conversations and consolidate them
        # For now, ther is a placeholder for the full implementation
        self._stats["consolidations"] += 1

    async def _consolidate_conversation(self, conversation_id: str, messages: List[Message]) -> None:
        """Consolidate a conversation into facts and summary."""
        if len(messages) < self.config.min_messages_for_summary:
            return

        # Extract facts from the conversation
        # Ther would use the FactExtractor to extract facts
        # For now, ther is a placeholder
        self._stats["facts_consolidated"] += 1

    async def _summarize_conversation(self, conversation_id: str, messages: List[Message]) -> ConversationSummary:
        """Generate a summary of a conversation using the LLM."""
        if len(messages) < self.config.min_messages_for_summary:
            return ConversationSummary(
                conversation_id=conversation_id,
                summary="",
                key_points=[],
                topics=[],
                sentiment="neutral",
                message_count=len(messages),
                token_count=sum(len(m.content or "") for m in messages) // 4,
            )

        # Build conversation text
        conversation_text = "\n".join(
            f"{m.role.value}: {m.content}" for m in messages if m.content
        )

        # Generate summary using the LLM
        prompt = f"""Summarize the following conversation. Provide:
1. A concise summary (max {self.config.max_summary_length} chars)
2. Key points (3-5 bullet points)
3. Main topics discussed
4. Overall sentiment (positive/negative/neutral)

Conversation:
{conversation_text}

Response format (JSON):
{{
  "summary": "...",
  "key_points": ["...", "..."],
  "topics": ["...", "..."],
  "sentiment": "positive|negative|neutral"
}}"""

        try:
            from viki.core.types import Message, Role
            messages_llm = [
                Message(role=Role.SYSTEM, content="You are a helpful assistant that summarizes conversations."),
                Message(role=Role.USER, content=prompt),
            ]

            result = self._engine.generate(
                messages_llm,
                model=self.config.consolidation_model or self._model,
                temperature=0.3,
                max_tokens=500,
            )

            import json
            summary_data = json.loads(result.get("content", "{}"))
            
            summary = ConversationSummary(
                conversation_id=conversation_id,
                summary=summary_data.get("summary", ""),
                key_points=summary_data.get("key_points", []),
                topics=summary_data.get("topics", []),
                sentiment=summary_data.get("sentiment", "neutral"),
                message_count=len(messages),
                token_count=sum(len(m.content or "") for m in messages) // 4,
            )
            
            self._stats["summaries_created"] += 1
            return summary

        except Exception as e:
            logger.error(f"Failed to summarize conversation {conversation_id}: {e}")
            return ConversationSummary(
                conversation_id=conversation_id,
                summary="Failed to generate summary",
                key_points=[],
                topics=[],
                sentiment="neutral",
                message_count=len(messages),
                token_count=sum(len(m.content or "") for m in messages) // 4,
            )

    def get_stats(self) -> Dict[str, int]:
        """Get consolidation statistics."""
        return self._stats.copy()


async def build_consolidation_service(
    config: Any,
    store: Any,
    engine: InferenceEngine,
    model: str,
    *,
    event_bus: Optional[Any] = None,
) -> Optional[MemoryConsolidationService]:
    """Build a MemoryConsolidationService from config."""
    if not getattr(config, "enabled", False):
        return None
    
    consolidation_config = ConsolidationConfig(
        enabled=True,
        interval_hours=getattr(config, "interval_hours", 24),
        max_conversations_per_run=getattr(config, "max_conversations_per_run", 100),
        min_messages_for_summary=getattr(config, "min_messages_for_summary", 5),
        max_summary_length=getattr(config, "max_summary_length", 500),
        consolidation_model=getattr(config, "consolidation_model", ""),
        max_facts_per_topic=getattr(config, "max_facts_per_topic", 50),
        min_fact_confidence=getattr(config, "min_fact_confidence", 0.7),
    )
    
    service = MemoryConsolidationService(
        config=consolidation_config,
        store=store,
        engine=engine,
        model=getattr(config, "consolidation_model", "") or model,
        event_bus=event_bus,
    )
    
    await service.start()
    return service


__all__ = [
    "MemoryConsolidationService",
    "ConsolidationConfig",
    "ConversationSummary",
    "build_consolidation_service",
]