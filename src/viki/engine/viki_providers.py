"""ViKi Model Provider Abstraction Layer.

Ther module provides a unified interface for ViKi to interact with various
model providers (local and cloud) while maintaining compatibility with
the existing Viki engine system.

Key features:
- Provider-agnostic model selection
- Capability-based routing (vision, tools, reasoning, etc.)
- Automatic fallback with circuit breaker
- Cost and latency tracking
- Streaming support
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Sequence

from viki.core.types import Message
from viki.engine._discovery import get_engine
from viki.engine._stubs import InferenceEngine
from viki.core.config import JarvisConfig

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
class ModelRequest:
    """Request for model inference."""

    messages: Sequence[Message]
    model: str
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ModelResponse:
    """Response from model inference."""

    content: str
    model: str
    provider: str
    usage: Dict[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CircuitBreakerState:
    """Circuit breaker state for provider fallback."""

    failures: int = 0
    last_failure: float = 0.0
    is_open: bool = False
    last_success: float = 0.0

    def record_success(self) -> None:
        self.failures = 0
        self.is_open = False
        self.last_success = time.time()

    def record_failure(self) -> None:
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= 5:
            self.is_open = True

    def can_attempt(self, reset_timeout: float = 60.0) -> bool:
        if not self.is_open:
            return True
        return (time.time() - self.last_failure) > reset_timeout


class ViKiModelProvider(ABC):
    """Abstract base class for ViKi model providers.

    Providers implement the core inference interface and expose
    capabilities for intelligent routing.
    """

    def __init__(self, config: Optional[JarvisConfig] = None) -> None:
        self.config = config
        self._circuit_breaker = CircuitBreakerState()
        self._engine: Optional[InferenceEngine] = None

    @property
    @abstractmethod
    def provider_info(self) -> ProviderInfo:
        """Return provider metadata and capabilities."""

    @abstractmethod
    def _initialize_engine(self) -> InferenceEngine:
        """Create and return the underlying inference engine."""

    def _get_engine(self) -> InferenceEngine:
        """Get or create the underlying engine."""
        if self._engine is None:
            self._engine = self._initialize_engine()
        return self._engine

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Synchronous generation."""
        if not self._circuit_breaker.can_attempt():
            raise RuntimeError(f"Circuit breaker open for {self.provider_info.name}")

        start = time.time()
        try:
            engine = self._get_engine()
            result = engine.generate(
                request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            self._circuit_breaker.record_success()
            return ModelResponse(
                content=result.get("content", ""),
                model=request.model,
                provider=self.provider_info.name,
                usage=result.get("usage", {}),
                finish_reason=result.get("finish_reason", "stop"),
                latency_ms=(time.time() - start) * 1000,
                tool_calls=result.get("tool_calls"),
                metadata={"engine": engine.engine_id},
            )
        except Exception as e:
            self._circuit_breaker.record_failure()
            logger.error(f"Provider {self.provider_info.name} generate failed: {e}")
            raise

    async def stream(self, request: ModelRequest) -> AsyncIterator[str]:
        """Stream tokens from the model."""
        if not self._circuit_breaker.can_attempt():
            raise RuntimeError(f"Circuit breaker open for {self.provider_info.name}")

        try:
            engine = self._get_engine()
            async for token in engine.stream(
                request.messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield token
            self._circuit_breaker.record_success()
        except Exception as e:
            self._circuit_breaker.record_failure()
            logger.error(f"Provider {self.provider_info.name} stream failed: {e}")
            raise

    def list_models(self) -> List[str]:
        """List available models."""
        return self._get_engine().list_models()

    def health_check(self) -> bool:
        """Check if provider is healthy."""
        if self._circuit_breaker.is_open and not self._circuit_breaker.can_attempt():
            return False
        try:
            return self._get_engine().health()
        except Exception:
            return False

    def can_serve(self, model: str) -> bool:
        """Check if provider can serve a specific model."""
        return self._get_engine().can_serve(model)

    def close(self) -> None:
        """Clean up resources."""
        if self._engine:
            self._engine.close()
            self._engine = None


class ViKiModelRouter:
    """Intelligent router for selecting the best model provider."""

    def __init__(self, config: JarvisConfig) -> None:
        self.config = config
        self._providers: Dict[str, ViKiModelProvider] = {}
        self._register_builtin_providers()

    def _register_builtin_providers(self) -> None:
        """Register built-in providers from the engine system."""
        # Discover engines and wrap them as ViKi providers
        engines = discover_engines(self.config)
        for key, engine in engines:
            self._providers[key] = _EngineAdapterProvider(key, engine)

    def register_provider(self, provider: ViKiModelProvider) -> None:
        """Register a custom provider."""
        self._providers[provider.provider_info.name] = provider

    def get_provider(self, name: str) -> Optional[ViKiModelProvider]:
        """Get a provider by name."""
        return self._providers.get(name)

    def list_providers(self) -> List[ProviderInfo]:
        """List all registered providers."""
        return [p.provider_info for p in self._providers.values()]

    def select_model(
        self,
        profile: ModelProfile,
        required_capabilities: Optional[List[ModelCapability]] = None,
        prefer_local: bool = True,
        max_cost_per_1k: Optional[float] = None,
    ) -> Optional[ViKiModelProvider]:
        """Select the best provider for the given requirements."""
        candidates = []

        for provider in self._providers.values():
            if not provider.health_check():
                continue

            info = provider.provider_info

            # Check capabilities
            if required_capabilities:
                if not all(c in info.capabilities for c in required_capabilities):
                    continue

            # Check profile match
            if profile == ModelProfile.LOCAL and not info.is_local:
                continue
            if profile == ModelProfile.CLOUD and info.is_local:
                continue

            # Check cost
            if max_cost_per_1k and info.cost_per_1k_tokens > max_cost_per_1k:
                continue

            candidates.append((info, provider))

        if not candidates:
            return None

        # Sort by preference: local first (if prefer_local), then by latency, then cost
        candidates.sort(key=lambda x: (
            0 if (prefer_local and x[0].is_local) else 1,
            x[0].estimated_latency_ms,
            x[0].cost_per_1k_tokens,
        ))

        return candidates[0][1]

    def get_fallback_chain(
        self,
        primary: ViKiModelProvider,
        required_capabilities: Optional[List[ModelCapability]] = None,
    ) -> List[ViKiModelProvider]:
        """Get a fallback chain for a primary provider."""
        chain = []
        for provider in self._providers.values():
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


class _EngineAdapterProvider(ViKiModelProvider):
    """Adapter to wrap an existing InferenceEngine as a ViKiModelProvider."""

    def __init__(self, engine_key: str, engine: InferenceEngine) -> None:
        super().__init__()
        self._engine_key = engine_key
        self._engine = engine

    @property
    def provider_info(self) -> ProviderInfo:
        is_cloud = getattr(self._engine, "is_cloud", False)
        return ProviderInfo(
            name=self._engine_key,
            display_name=self._engine_key.replace("_", " ").title(),
            is_local=not is_cloud,
            capabilities=self._infer_capabilities(self._engine),
            supported_models=self._engine.list_models(),
            requires_api_key=is_cloud,
            default_model=self._engine.list_models()[0] if self._engine.list_models() else "",
        )

    def _infer_capabilities(self, engine: InferenceEngine) -> List[ModelCapability]:
        caps = [ModelCapability.CHAT, ModelCapability.STREAMING]
        if engine.can_serve(""):
            caps.append(ModelCapability.TOOLS)
        return caps

    def _initialize_engine(self) -> InferenceEngine:
        return self._engine


# Import here to avoid circular dependency
def discover_engines(config: JarvisConfig):
    from viki.engine._discovery import discover_engines as _discover
    return _discover(config)


# -----------------------------------------------------------------------------
# Cloud Provider Adapters
# -----------------------------------------------------------------------------

class GeminiProvider(ViKiModelProvider):
    """Google Gemini API provider."""

    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="gemini",
            display_name="Google Gemini",
            is_local=False,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.REASONING,
                ModelCapability.CODING,
                ModelCapability.VISION,
                ModelCapability.TOOLS,
                ModelCapability.STREAMING,
                ModelCapability.LONG_CONTEXT,
                ModelCapability.STRUCTURED_OUTPUT,
            ],
            supported_models=[
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.0-pro",
                "gemini-1.0-pro-vision",
            ],
            requires_api_key=True,
            default_model="gemini-1.5-pro",
            estimated_latency_ms=800,
            cost_per_1k_tokens=0.00125,  # $1.25/M tokens for 1.5 Pro
            max_context_length=2_000_000,  # 2M for 1.5 Pro
            metadata={"provider": "google"},
        )

    def _initialize_engine(self) -> InferenceEngine:
        from viki.engine.litellm import LiteLLMEngine
        return LiteLLMEngine(default_model=self.provider_info.default_model)


class GroqProvider(ViKiModelProvider):
    """Groq API provider (fast inference)."""

    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="groq",
            display_name="Groq",
            is_local=False,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.REASONING,
                ModelCapability.CODING,
                ModelCapability.TOOLS,
                ModelCapability.STREAMING,
                ModelCapability.STRUCTURED_OUTPUT,
            ],
            supported_models=[
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ],
            requires_api_key=True,
            default_model="llama-3.1-70b-versatile",
            estimated_latency_ms=300,  # Very fast
            cost_per_1k_tokens=0.00059,  # $0.59/M tokens for 70B
            max_context_length=32768,
            metadata={"provider": "groq"},
        )

    def _initialize_engine(self) -> InferenceEngine:
        from viki.engine.litellm import LiteLLMEngine
        return LiteLLMEngine(default_model=self.provider_info.default_model)


class OpenRouterProvider(ViKiModelProvider):
    """OpenRouter API provider (multi-provider gateway)."""

    @property
    def provider_info(self) -> ProviderInfo:
        return ProviderInfo(
            name="openrouter",
            display_name="OpenRouter",
            is_local=False,
            capabilities=[
                ModelCapability.CHAT,
                ModelCapability.REASONING,
                ModelCapability.CODING,
                ModelCapability.VISION,
                ModelCapability.TOOLS,
                ModelCapability.STREAMING,
                ModelCapability.LONG_CONTEXT,
                ModelCapability.STRUCTURED_OUTPUT,
            ],
            supported_models=[
                "openrouter/auto",
                "openrouter/anthropic/claude-3.5-sonnet",
                "openrouter/google/gemini-pro-1.5",
                "openrouter/meta-llama/llama-3.1-70b-instruct",
                "openrouter/mistral/mistral-large",
            ],
            requires_api_key=True,
            default_model="openrouter/auto",
            estimated_latency_ms=1000,
            cost_per_1k_tokens=0.002,  # Varies by model
            max_context_length=128000,
            metadata={"provider": "openrouter", "gateway": True},
        )

    def _initialize_engine(self) -> InferenceEngine:
        from viki.engine.litellm import LiteLLMEngine
        return LiteLLMEngine(default_model=self.provider_info.default_model)


# -----------------------------------------------------------------------------
# Factory
# -----------------------------------------------------------------------------

def create_viki_router(config: JarvisConfig) -> ViKiModelRouter:
    """Create a ViKiModelRouter with all built-in and cloud providers."""
    router = ViKiModelRouter(config)

    # Register cloud providers if API keys are available
    import os

    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        router.register_provider(GeminiProvider(config))

    if os.environ.get("GROQ_API_KEY"):
        router.register_provider(GroqProvider(config))

    if os.environ.get("OPENROUTER_API_KEY"):
        router.register_provider(OpenRouterProvider(config))

    return router


__all__ = [
    "ModelCapability",
    "ModelProfile",
    "ProviderInfo",
    "ModelRequest",
    "ModelResponse",
    "CircuitBreakerState",
    "ViKiModelProvider",
    "ViKiModelRouter",
    "GeminiProvider",
    "GroqProvider",
    "OpenRouterProvider",
    "create_viki_router",
]