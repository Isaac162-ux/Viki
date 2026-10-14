"""ViKi Unified Model Gateway — Advanced routing, fallback, and monitoring."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Sequence, Set

from viki.core.config import JarvisConfig
from viki.core.types import Message
from viki.engine._discovery import discover_engines, get_engine
from viki.engine._stubs import InferenceEngine

logger = logging.getLogger(__name__)


class ModelCapability(Enum):
    """Capabilities that a model/provider may support."""

    CHAT = "chat"
    REASONING = "reasoning"
    CODING = "coding"
    VISION = "vision"
    TOOLS = "tools"
    STREAMING = "streaming"
    EMBEDDING = "embedding"
    AUDIO = "audio"
    LONG_CONTEXT = "long_context"
    STRUCTURED_OUTPUT = "structured_output"


class ModelProfile(Enum):
    """Model profiles for different use cases."""

    FAST_CHAT = "fast_chat"          # Low latency, simple responses
    CODING = "coding"                # Code generation/analysis
    REASONING = "reasoning"          # Complex reasoning tasks
    VISION = "vision"                # Image understanding
    RESEARCH = "research"            # Deep research with tools
    LONG_CONTEXT = "long_context"    # Large document processing
    LOCAL = "local"                  # Local-only execution
    CLOUD = "cloud"                  # Cloud APIs (requires keys)


class RequestPriority(Enum):
    """Priority levels for gateway requests."""
    LOW = 0
    NORMAL = 50
    HIGH = 100
    CRITICAL = 200


@dataclass(slots=True)
class ProviderInfo:
    """Information about a model provider."""

    name: str
    display_name: str
    is_local: bool
    capabilities: List[ModelCapability] = field(default_factory=list)
    supported_models: List[str] = field(default_factory=list)
    requires_api_key: bool = False
    default_model: str = ""
    estimated_latency_ms: int = 1000
    cost_per_1k_tokens: float = 0.0
    max_context_length: int = 8192
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GatewayRequest:
    """Enhanced request with gateway metadata."""

    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    messages: Sequence[Message] = ()
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    priority: RequestPriority = RequestPriority.NORMAL
    required_capabilities: List[ModelCapability] = field(default_factory=list)
    preferred_providers: List[str] = field(default_factory=list)
    excluded_providers: List[str] = field(default_factory=list)
    max_cost_usd: Optional[float] = None
    max_latency_ms: Optional[int] = None
    prefer_local: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class GatewayResponse:
    """Enhanced response with gateway metadata."""

    request_id: str
    content: str
    model: str
    provider: str
    usage: Dict[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    fallback_used: bool = False
    fallback_chain: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass(slots=True)
class ProviderMetrics:
    """Runtime metrics for a provider."""

    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    circuit_breaker_opens: int = 0
    last_request_at: Optional[float] = None
    last_error: Optional[str] = None
    last_error_at: Optional[float] = None

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def avg_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests

    @property
    def avg_cost_per_1k(self) -> float:
        if self.total_tokens == 0:
            return 0.0
        return (self.total_cost_usd / self.total_tokens) * 1000


class BudgetManager:
    """Manages cost budgets for providers and overall gateway."""

    def __init__(self) -> None:
        self._budgets: Dict[str, float] = {}  # provider -> budget USD
        self._spending: Dict[str, float] = defaultdict(float)  # provider -> spent USD
        self._period_start: float = time.time()
        self._period_hours: int = 24
        self._lock = asyncio.Lock()

    def set_budget(self, provider: str, budget_usd: float, period_hours: int = 24) -> None:
        with self._lock:
            self._budgets[provider] = budget_usd
            self._period_hours = period_hours
            self._reset_if_needed()

    def _reset_if_needed(self) -> None:
        elapsed = time.time() - self._period_start
        if elapsed >= self._period_hours * 3600:
            self._spending.clear()
            self._period_start = time.time()

    def can_afford(self, provider: str, estimated_cost: float) -> bool:
        with self._lock:
            self._reset_if_needed()
            budget = self._budgets.get(provider)
            if budget is None:
                return True  # No budget set = unlimited
            return (self._spending[provider] + estimated_cost) <= budget

    def record_spending(self, provider: str, cost: float) -> None:
        with self._lock:
            self._reset_if_needed()
            self._spending[provider] += cost

    def get_remaining(self, provider: str) -> Optional[float]:
        with self._lock:
            self._reset_if_needed()
            budget = self._budgets.get(provider)
            if budget is None:
                return None
            return budget - self._spending.get(provider, 0.0)


class CircuitBreaker:
    """Circuit breaker for provider fallback."""

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure: float = 0.0
        self.is_open = False
        self.last_success: float = 0.0

    def record_success(self) -> None:
        self.failures = 0
        self.is_open = False
        self.last_success = time.time()

    def record_failure(self) -> None:
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.failure_threshold:
            self.is_open = True

    def can_attempt(self) -> bool:
        if not self.is_open:
            return True
        return (time.time() - self.last_failure) > self.reset_timeout

    def reset(self) -> None:
        self.failures = 0
        self.is_open = False


class ViKiGateway:
    """Unified model gateway with intelligent routing and fallback."""

    def __init__(
        self,
        config: JarvisConfig,
        budget_manager: Optional[BudgetManager] = None,
    ) -> None:
        self.config = config
        self.router = self._create_router(config)
        self.budget_manager = budget_manager or BudgetManager()
        self._metrics: Dict[str, ProviderMetrics] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = defaultdict(CircuitBreaker)
        self._request_log: List[GatewayResponse] = []
        self._log_max_size = 10000
        self._lock = asyncio.Lock()
        self._hooks: Dict[str, List[Callable]] = defaultdict(list)

    def _create_router(self, config: JarvisConfig):
        """Create a model router with all available providers."""
        from viki.engine.viki_providers import create_viki_router
        return create_viki_router(config)

    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a callback for gateway events."""
        self._hooks[event].append(callback)

    def _emit(self, event: str, *args, **kwargs) -> None:
        for callback in self._hooks[event]:
            try:
                callback(*args, **kwargs)
            except Exception:
                logger.debug(f"Hook {event} failed", exc_info=True)

    def _get_metrics(self, provider: str) -> ProviderMetrics:
        if provider not in self._metrics:
            self._metrics[provider] = ProviderMetrics(provider_name=provider)
        return self._metrics[provider]

    def _get_circuit_breaker(self, provider: str) -> CircuitBreaker:
        return self._circuit_breakers[provider]

    def _estimate_cost(self, provider: ViKiModelProvider, tokens: int) -> float:
        return (tokens / 1000) * provider.provider_info.cost_per_1k_tokens

    def _infer_profile(self, request: GatewayRequest) -> ModelProfile:
        """Infer the model profile from request characteristics."""
        if request.required_capabilities:
            if ModelCapability.CODING in request.required_capabilities:
                return ModelProfile.CODING
            if ModelCapability.REASONING in request.required_capabilities:
                return ModelProfile.REASONING
            if ModelCapability.VISION in request.required_capabilities:
                return ModelProfile.VISION
            if ModelCapability.TOOLS in request.required_capabilities:
                return ModelProfile.RESEARCH

        # Check message length for long context
        total_chars = sum(len(m.content or "") for m in request.messages)
        if total_chars > 50000:
            return ModelProfile.LONG_CONTEXT

        # Default based on prefer_local
        if request.prefer_local:
            return ModelProfile.LOCAL
        return ModelProfile.FAST_CHAT

    def _get_max_cost_per_1k(self, request: GatewayRequest) -> Optional[float]:
        if request.max_cost_usd and request.max_tokens:
            return (request.max_cost_usd / request.max_tokens) * 1000
        return None

    def _select_provider(self, request: GatewayRequest) -> Optional[ViKiModelProvider]:
        """Select the best provider for the request."""
        # Check preferred providers first
        for name in request.preferred_providers:
            provider = self.router.get_provider(name)
            if provider and provider.health_check():
                if name not in request.excluded_providers:
                    return provider

        # Use router for intelligent selection
        profile = self._infer_profile(request)
        return self.router.select_model(
            profile=profile,
            required_capabilities=request.required_capabilities,
            prefer_local=request.prefer_local,
            max_cost_per_1k=self._get_max_cost_per_1k(request),
        )

    def _build_fallback_chain(
        self,
        primary: ViKiModelProvider,
        required_capabilities: Optional[List[ModelCapability]] = None,
    ) -> List[ViKiModelProvider]:
        """Get a fallback chain for a primary provider."""
        chain = []
        for provider in self.router._providers.values():
            if provider == primary:
                continue
            if not provider.health_check():
                continue
            if required_capabilities and not all(
                c in provider.provider_info.capabilities for c in required_capabilities
            ):
                continue
            chain.append(provider)

        # Sort by similarity to primary (local/local, cloud/cloud)
        primary_is_local = primary.provider_info.is_local
        chain.sort(key=lambda p: (
            0 if p.provider_info.is_local == primary_is_local else 1,
            p.provider_info.estimated_latency_ms,
        ))
        return chain

    async def generate(
        self,
        request: GatewayRequest,
        timeout: Optional[float] = None,
    ) -> GatewayResponse:
        """Synchronous generation with routing and fallback."""
        start = time.time()
        self._emit("request_start", request)

        # Select primary provider
        primary = self._select_provider(request)
        if not primary:
            raise RuntimeError("No suitable provider available")

        # Build fallback chain
        fallback_chain = self.router.get_fallback_chain(
            primary, request.required_capabilities
        )

        # Try primary, then fallbacks
        providers_to_try = [primary] + fallback_chain
        last_error = None

        for i, provider in enumerate(providers_to_try):
            if i > 0:
                logger.warning(
                    f"Falling back to {provider.provider_info.name} "
                    f"(attempt {i+1}/{len(providers_to_try)})"
                )

            # Check budget
            estimated_cost = self._estimate_cost(primary, request.max_tokens)
            if not self.budget_manager.can_afford(primary.provider_info.name, estimated_cost):
                logger.warning(f"Budget exceeded for {primary.provider_info.name}, skipping")
                continue

            # Check circuit breaker
            cb = self._get_circuit_breaker(primary.provider_info.name)
            if not cb.can_attempt():
                logger.warning(f"Circuit breaker open for {primary.provider_info.name}")
                continue

            # Check health
            if not provider.health_check():
                logger.warning(f"Provider {provider.provider_info.name} unhealthy")
                continue

            # Check if provider is excluded
            if provider.provider_info.name in request.excluded_providers:
                continue

            try:
                # Check health
                if not provider.health_check():
                    raise RuntimeError(f"Provider {provider.provider_info.name} unhealthy")

                # Execute request
                model_req = ModelRequest(
                    messages=request.messages,
                    model=request.model or primary.provider_info.default_model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=False,
                    tools=request.tools,
                    response_format=request.response_format,
                    metadata=request.metadata,
                )

                result = provider.generate(model_req)

                # Record metrics
                self._record_success(provider, result)

                response = GatewayResponse(
                    request_id=request.request_id,
                    content=result.content,
                    model=result.model,
                    provider=result.provider,
                    usage=result.usage,
                    finish_reason=result.finish_reason,
                    latency_ms=(time.time() - start) * 1000,
                    cost_usd=result.cost_usd,
                    tool_calls=result.tool_calls,
                    metadata=result.metadata,
                    fallback_used=i > 0,
                    fallback_chain=[p.provider_info.name for p in providers_to_try[:i+1]],
                )

                self._log_response(response)
                self._emit("request_complete", response)
                return response

            except Exception as e:
                last_error = e
                self._record_failure(provider, str(e))
                logger.warning(
                    f"Provider {provider.provider_info.name} failed: {e}"
                )
                continue

        # All providers failed
        raise RuntimeError(
            f"All providers failed for request {request.request_id}. "
            f"Last error: {last_error}"
        )

    async def stream_sse(
        self,
        request: GatewayRequest,
    ) -> AsyncIterator[str]:
        """Stream tokens as Server-Sent Events with automatic fallback."""
        self._emit("request_start", request)

        primary = self._select_provider(request)
        if not primary:
            raise RuntimeError("No suitable provider available")

        fallback_chain = self.router.get_fallback_chain(
            primary, request.required_capabilities
        )
        providers_to_try = [primary] + fallback_chain

        for i, provider in enumerate(providers_to_try):
            if i > 0:
                logger.warning(f"Streaming fallback to {provider.provider_info.name}")

            if not self.budget_manager.can_afford(primary.provider_info.name, 0.01):
                continue

            if not provider._circuit_breaker.can_attempt():
                continue

            try:
                if not provider.health_check():
                    raise RuntimeError(f"Provider {provider.provider_info.name} unhealthy")

                model_req = ModelRequest(
                    messages=request.messages,
                    model=request.model or primary.provider_info.default_model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=True,
                    tools=request.tools,
                    response_format=request.response_format,
                    metadata=request.metadata,
                )

                # Send initial event
                yield f"data: {json.dumps({'type': 'start', 'provider': provider.provider_info.name, 'model': request.model or primary.provider_info.default_model})}\n\n"

                async for token in provider.stream(model_req):
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

                # Send completion event
                yield f"data: {json.dumps({'type': 'end', 'provider': provider.provider_info.name})}\n\n"

                self._record_success(provider, ModelResponse(
                    content="", model="", provider="",
                    latency_ms=0, cost_usd=0
                ))
                self._emit("stream_complete", provider.provider_info.name)
                return

            except Exception as e:
                self._record_failure(provider, str(e))
                logger.warning(f"Streaming provider {provider.provider_info.name} failed: {e}")
                # Send error event before trying fallback
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                continue

        raise RuntimeError("All streaming providers failed")

    def _record_success(self, provider: ViKiModelProvider, response: ModelResponse) -> None:
        metrics = self._get_metrics(provider.provider_info.name)
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.total_latency_ms += response.latency_ms
        metrics.total_cost_usd += response.cost_usd
        metrics.total_tokens += response.usage.get("total_tokens", 0)
        metrics.last_request_at = time.time()
        provider._circuit_breaker.record_success()

        self.budget_manager.record_spending(
            provider.provider_info.name, response.cost_usd
        )

    def _record_failure(self, provider: ViKiModelProvider, error: str) -> None:
        metrics = self._get_metrics(provider.provider_info.name)
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.last_error = error
        metrics.last_error_at = time.time()
        provider._circuit_breaker.record_failure()

        if provider._circuit_breaker.is_open:
            metrics.circuit_breaker_opens += 1

    def _log_response(self, response: GatewayResponse) -> None:
        with self._lock:
            self._request_log.append(response)
            if len(self._request_log) > self._log_max_size:
                self._request_log = self._request_log[-self._log_max_size:]

    def get_metrics(self) -> Dict[str, ProviderMetrics]:
        """Get current provider metrics."""
        return dict(self._metrics)

    def get_recent_requests(self, limit: int = 100) -> List[GatewayResponse]:
        """Get recent request log."""
        with self._lock:
            return self._request_log[-limit:]

    def get_provider_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all providers."""
        health = {}
        for name, provider in self.router._providers.items():
            metrics = self._metrics.get(name, ProviderMetrics(name))
            health[name] = {
                "healthy": provider.health_check(),
                "circuit_breaker_open": provider._circuit_breaker.is_open,
                "success_rate": metrics.success_rate,
                "avg_latency_ms": metrics.avg_latency_ms,
                "avg_cost_per_1k": metrics.avg_cost_per_1k,
                "total_requests": metrics.total_requests,
                "last_error": metrics.last_error,
            }
        return health

    def set_provider_budget(self, provider: str, budget_usd: float, period_hours: int = 24) -> None:
        """Set a cost budget for a provider."""
        self.budget_manager.set_budget(provider, budget_usd, period_hours)

    def close(self) -> None:
        """Close all providers."""
        for provider in self.router._providers.values():
            provider.close()


def create_viki_gateway(config: JarvisConfig) -> ViKiGateway:
    """Factory function to create a ViKiGateway with default configuration."""
    gateway = ViKiGateway(config)

    # Register default hooks for logging
    gateway.register_hook("request_start", lambda req: logger.debug(f"Gateway request {req.request_id} started"))
    gateway.register_hook("request_complete", lambda resp: logger.debug(f"Gateway request {resp.request_id} completed via {resp.provider}"))

    return gateway


# Import ViKiModelProvider and ModelRequest at the end to avoid circular imports
from viki.engine.viki_providers import (
    ViKiModelProvider,
    ModelRequest,
    ModelResponse,
)

__all__ = [
    "ViKiGateway",
    "GatewayRequest",
    "GatewayResponse",
    "ProviderMetrics",
    "BudgetManager",
    "CircuitBreaker",
    "ModelCapability",
    "ModelProfile",
    "RequestPriority",
    "ProviderInfo",
    "ModelRequest",
    "ModelResponse",
    "create_viki_gateway",
]