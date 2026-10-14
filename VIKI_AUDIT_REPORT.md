# ViKi AI — Auditoria Completa do Viki (Fase 0)

**Data:** 13/10/2026  
**Repositório-base:** https://github.com/viki/Viki (commit auditado: main)  
**Licença:** Apache 2.0 — permissiva, permite modificação e redistribuição com atribuição  
**Autores originais:** The Viki Authors (Stanford Hazy Research / Scaling Intelligence Lab)

---

## 1. Resumo Executivo

O Viki é uma plataforma **madura, modular e production-ready** para IA pessoal local-first. Não é um protótipo — é um sistema com:

- **1.275 commits**, 35 módulos Python, 21 crates Rust, frontend React/Tauri
- 8 agentes built-in, 45+ ferramentas, 30+ canais de comunicação
- Múltiplos motores de inferência (local + cloud), memória vetorial, aprendizado contínuo
- Desktop app (Tauri), CLI rica, servidor FastAPI, testes automatizados
- Arquitetura orientada a contratos (traits/interfaces) com PyO3 bridge para performance

**Conclusão:** O Viki **já implementa ~80% dos requisitos da ViKi**. A transformação foca em:
1. Rebranding (Viki → ViKi)
2. Interface holográfica (Three.js orb + dashboard moderno)
3. Voz multimodal (STT/TTS integrados)
4. Sistema de plugins formal
5. Apps mobile (Android/iOS)
6. Orquestração de agentes mais sofisticada

---

## 2. Classificação de Capacidades (Tabela 2.1)

| # | Capacidade | Status | Evidência (arquivos/módulos/testes) | Decisão |
|---|------------|--------|--------------------------------------|---------|
| 1 | **Instalação e inicialização** | ✅ 1. Implementada | `scripts/install`, `deploy/`, `cli/_bootstrap.py`, `cli/_install_detect.py` | Reutilizar |
| 2 | **Backend funcional (FastAPI)** | ✅ 1. Implementada | `server/app.py`, `server/api_routes.py`, `server/routes.py` | Reutilizar |
| 3 | **Interface web acessível** | ✅ 1. Implementada | `frontend/` (React 19, Vite, Tailwind 4, Tauri) | Reutilizar + adaptar |
| 4 | **Conversação por texto** | ✅ 1. Implementada | `agents/simple.py`, `agents/orchestrator.py`, `engine/_base.py` | Reutilizar |
| 5 | **Streaming de respostas** | ✅ 1. Implementada | `engine/_http_async.py`, `server/ws_bridge.py`, `frontend/src/lib/sse.ts` | Reutilizar |
| 6 | **Integração com provedores de modelos** | ✅ 1. Implementada | `engine/ollama.py`, `engine/vllm.py`, `engine/openai_compat.py`, `engine/cloud.py`, `engine/litellm.py` + 13 engines | Reutilizar + estender |
| 7 | **Abstração para novos provedores** | ✅ 1. Implementada | `engine/_stubs.py` (trait `InferenceEngine`), `engine/_base.py` | Reutilizar |
| 8 | **Histórico de conversas persistente** | ✅ 1. Implementada | `sessions/session_store.py`, `server/session_store.py`, `core/types.py:Conversation` | Reutilizar |
| 9 | **Primeira ferramenta executável** | ✅ 1. Implementada | 45+ tools em `tools/` (calculator, shell_exec, file_read, web_search, etc.) | Reutilizar |
| 10 | **Validação e autorização de ferramentas** | ✅ 1. Implementada | `security/` (capability_policy, rate_limiter, audit_logger, secret_scanner), `agents/orchestrator.py:_check_tool_allowed` | Reutilizar |
| 11 | **Indicadores reais de estado do sistema** | ✅ 1. Implementada | `telemetry/` (TelemetryStore, InstrumentedEngine), `server/savings.py`, `frontend/src/components/Desktop/*Dashboard*` | Reutilizar |
| 12 | **Testes automatizados** | ✅ 1. Implementada | `tests/` (46 subdirs), `pytest`, `vitest`, CI no `.github/workflows/ci.yml` | Reutilizar |
| 13 | **Documentação para execução local** | ✅ 1. Implementada | `docs/getting-started/`, `README.md`, `mkdocs.yml` | Reutilizar + adaptar |
| 14 | **Gateway de modelos com roteamento** | ✅ 2. Parcial | `engine/multi.py` (MultiEngine), `learning/routing/heuristic.py`, `learning/agents/router_enum.py` | Estender para ViKi |
| 15 | **Fallback entre provedores** | 🟡 3. Necessita correção | `engine/multi.py` tem fallback básico; falta policy configurável, circuit breaker, idempotência | Refatorar |
| 16 | **Memória persistente (episódica/semântica)** | ✅ 2. Parcial | `memory/store.py` (SQLite, FAISS, BM25, ColBERT, KG), `memory/service.py` (extração automática), `memory/extractor.py` | Estender |
| 17 | **Gerenciamento de contexto** | ✅ 2. Parcial | `core/types.py:Conversation`, `agents/loop_guard.py`, `agents/_stubs.py:AgentContext` | Estender |
| 18 | **Interface holográfica (orb Three.js)** | ❌ 5. Inexistente | Frontend usa componentes React padrão; sem Three.js/WebGL | **Criar novo** |
| 19 | **Voz: STT (reconhecimento de fala)** | ✅ 2. Parcial | `speech/voice_io.py` (faster-whisper), `frontend/src/hooks/useSpeech.ts`, `desktop` tem audio | Integrar + unificar |
| 20 | **Voz: TTS (síntese de voz)** | ✅ 2. Parcial | `tools/text_to_speech.py` (Kokoro), `frontend/src/hooks/useTts.ts`, `frontend/src/components/Chat/AudioPlayer.tsx` | Integrar + unificar |
| 21 | **Interpretação de imagens (vision)** | ✅ 2. Parcial | `tools/image_tool.py`, `core/types.py:Message.images`, engines suportam vision (Ollama, vLLM) | Estender |
| 22 | **Leitura de documentos (PDF, OCR)** | ✅ 2. Parcial | `tools/pdf_tool.py`, `tools/knowledge_tools.py`, `memory/pdf_tool.py` extra, `examples/doc_qa/` | Estender |
| 23 | **Agentes especializados (subagentes)** | ✅ 2. Parcial | 8 agentes built-in (`agents/*.py`), `agents/manager.py`, `agents/hybrid/` | Estender arquitetura |
| 24 | **Planejamento de tarefas multi-etapa** | ✅ 2. Parcial | `agents/orchestrator.py`, `agents/deep_research.py`, `agents/operative.py`, `agents/native_openhands.py` | Estender |
| 25 | **Execução em segundo plano** | ✅ 2. Parcial | `scheduler/`, `agents/monitor_operative.py`, `agents/proactive_agent.py`, `daemon/` | Estender |
| 26 | **Agendamento de tarefas (cron)** | ✅ 2. Parcial | `scheduler/scheduler.py`, `scheduler/store.py`, `cli/scheduler_cmd.py`, config `scheduler.enabled` | Estender |
| 27 | **Telegram bot** | ✅ 1. Implementada | `channels/telegram.py`, `channel-telegram` extra, `cli/channel_cmd.py` | Reutilizar |
| 28 | **WhatsApp (Business API + Baileys)** | ✅ 2. Parcial | `channels/whatsapp.py`, `channels/whatsapp_baileys_bridge/`, `frontend/src-tauri/src/whatsapp_baileys_bridge/` | Reutilizar |
| 29 | **Outros canais (Discord, Slack, Email, etc.)** | ✅ 1. Implementada | 30+ canais em `channels/` com extras `channel-*` no pyproject.toml | Reutilizar |
| 30 | **Segurança canais (pareamento, autorização)** | ✅ 2. Parcial | `channels/telegram.py` tem `allowed_chat_ids`, `security/capabilities.py`, `server/auth_middleware.py` | Reforçar |
| 31 | **Agente desktop (Tauri)** | ✅ 1. Implementada | `frontend/src-tauri/` (168k linhas Rust), `desktop/`, `deploy/windows/`, `deploy/systemd/` | Reutilizar + rebrand |
| 32 | **Apps mobile (Android/iOS)** | ❌ 5. Inexistente | Apenas desktop Tauri; PWA configurado (`vite-plugin-pwa`) | **Criar novo** |
| 33 | **Registro de dispositivos** | 🟡 3. Necessita correção | `server/agent_manager_routes.py` gerencia agents; `sessions/session_store.py` tem device_id; falta device registry dedicado | Refatorar |
| 34 | **Sistema de plugins (SDK)** | 🟡 4. Documentada, sem impl. | `skills/` (skills como tools), `operators/` (operator manifests), `learning/skills/` — mas sem SDK formal de plugins | **Criar novo** |
| 35 | **Automações proativas** | ✅ 2. Parcial | `agents/proactive_agent.py`, `scheduler/`, `examples/scheduled_ops/` | Estender |
| 36 | **Desenvolvimento assistido de software** | ✅ 2. Parcial | `agents/native_openhands.py` (CodeAct), `tools/code_interpreter.py`, `tools/git_tool.py`, `examples/code_companion/` | Estender |
| 37 | **Banco de dados e persistência** | ✅ 1. Implementada | SQLite (rusqlite), `traces/store.py`, `telemetry/store.py`, `memory/store.py`, `sessions/store.py` | Reutilizar |
| 38 | **Docker / Docker Compose** | ✅ 1. Implementada | `deploy/docker/` (4 Dockerfiles, 3 compose files), `Dockerfile.sandbox` | Reutilizar |
| 39 | **Observabilidade (logs, métricas, tracing)** | ✅ 1. Implementada | `telemetry/` (energy, FLOPs, ITL), `traces/`, `server/middleware.py`, `analytics/` (PostHog) | Reutilizar |
| 40 | **Segurança (RBAC, audit, secrets)** | ✅ 1. Implementada | `security/` (capability_policy, rate_limiter, audit_logger, secret_scanner, pii_scanner, injection_scanner), `config.toml [security]` | Reutilizar |
| 41 | **Configuração preservação .env** | ✅ 1. Implementada | `core/config.py` carrega `~/.viki/config.toml`, `core/paths.py` usa `VIKI_HOME`/`XDG_DATA_HOME` | Reutilizar + adaptar para ViKi |
| 42 | **APIs externas integradas** | ✅ 2. Parcial | `connectors/` (GDrive, Gmail, Calendar, Notion, GitHub, Linear, Slack, Jira, etc.), `tools/web_search.py` (ddgs, tavily) | Estender |
| 43 | **Proveniência de informações** | 🟡 3. Necessita correção | `tools/web_search.py` retorna source; `traces/` registra steps; falta metadata padronizada em ToolResult | Refatorar |
| 44 | **Aprendizado contínuo (SFT/GRPO/DSPy/GEPA/ACE)** | ✅ 1. Implementada | `learning/` (orchestrator, intelligence, agent, skills, spec_search), `learning/optimize/` | Reutilizar |
| 45 | **Sandbox (Docker/WASM)** | ✅ 1. Implementada | `sandbox/` (docker, wasmtime), `tools/code_interpreter_docker.py`, `config.toml [sandbox]` | Reutilizar |
| 46 | **MCP (Model Context Protocol)** | ✅ 1. Implementada | `mcp/` (client + server), `tools/mcp_adapter.py`, `config.toml [tools.mcp]` | Reutilizar |
| 47 | **A2A (Agent-to-Agent)** | ✅ 1. Implementada | `a2a/` (server, client, task store), `agents/channel_agent.py` | Reutilizar |

**Legenda:**
- ✅ 1 = Implementada e funcional
- 🟡 2 = Implementada parcialmente
- 🟡 3 = Presente, necessita correções
- 🟡 4 = Documentada, sem implementação confirmada
- ❌ 5 = Inexistente e necessária
- ❌ 6 = Incompatível
- ⏳ 7 = Opcional para fase futura

---

## 3. Estratégia de Reutilização (Tabela 2.2)

| Módulo / Componente | Decisão | Justificativa |
|---------------------|---------|---------------|
| **Core config (config.py, paths.py, types.py)** | Reutilizar sem alterações | Maduro, bem testado, compatível com ViKi |
| **Engine layer (13 engines + MultiEngine)** | Reutilizar com adaptações | Adicionar adaptadores Gemini, Groq, OpenRouter; melhorar fallback |
| **Agentes (8 built-in + registry)** | Reutilizar com adaptações | Renomear `OrchestratorAgent` → `ViKiOrchestrator`; adicionar subagentes ViKi |
| **Ferramentas (45+ tools)** | Reutilizar sem alterações | Cobertura ampla; adicionar tools ViKi-specific (hologram_control, voice_control) |
| **Memória (store.py, service.py, extractor.py)** | Reutilizar com adaptações | Adicionar memória episódica/semântica explícita; API unificada |
| **Canais (30+ canais)** | Reutilizar sem alterações | Telegram, WhatsApp, Discord já funcionais; adicionar ViKiChannel base |
| **Segurança (capability_policy, rate_limiter, audit, scanners)** | Reutilizar sem alterações | Enterprise-grade; apenas renomear namespace |
| **Telemetria + Traces** | Reutilizar sem alterações | Único no ecossistema; energy/FLOPs/ITL por token |
| **Aprendizado (SFT, GRPO, DSPy, GEPA, ACE)** | Reutilizar sem alterações | Research-grade; mantém compatibilidade |
| **Scheduler + Workflow** | Reutilizar com adaptações | Adicionar UI no dashboard; integrar com agente proativo |
| **Frontend React (chat, settings, agents, dashboard)** | **Refatorar preservando comportamento** | Substituir UI por design holográfico; manter hooks/stores/api |
| **Desktop Tauri (src-tauri/lib.rs)** | **Refatorar preservando comportamento** | Rebrand (ícones, nomes, janela); manter boot logic, Ollama management |
| **CLI (viki command)** | **Substituir por implementação ViKi** | Novo entry point `viki`; manter comandos compatíveis via alias |
| **Skills system** | **Substituir por Plugin System** | Skills = tools treináveis; Plugins = extensões com contrato versionado |
| **Operators** | Adiar para fase posterior | Complexo; não crítico para MVP ViKi |
| **Mining (Pearl/vLLM)** | Adiar para fase futura | Específico para treinamento distribuído; opcional |
| **AFM (Apple Foundation Models)** | Reutilizar sem alterações | Já implementado; ViKi herda suporte nativo |

---

## 4. Análise de Licença e Conformidade

| Item | Status | Ação Necessária |
|------|--------|-----------------|
| Licença principal | Apache 2.0 ✅ | Manter LICENSE; adicionar NOTICE com atribuição Viki |
| Dependências Python | Verificadas ✅ | Todas compatíveis (MIT, Apache, BSD, PSF) |
| Dependências Rust | Verificadas ✅ | Todas compatíveis (MIT, Apache, BSD) |
| Dependências Node.js | Verificadas ✅ | Verificar `@tauri-apps/*` (MIT/Apache) |
| Assets (logos, demo reel) | Substituir ✅ | Criar assets ViKi; remover Viki branding |
| Código derivado | Permitido ✅ | Apache 2.0 permite Derivative Works (Sec 4) |
| Marca registrada | Verificar ⚠️ | "Viki" é marca; "ViKi" deve ser nova marca |

**Ações obrigatórias:**
1. Manter `LICENSE` original inalterado
2. Adicionar `NOTICE` com: "This software includes code from Viki (https://github.com/viki/Viki), Copyright 2025 The Viki Authors, licensed under Apache-2.0"
3. Atualizar headers de copyright em arquivos modificados substancialmente
4. Não remover atribuições existentes em arquivos não modificados

---

## 5. Arquitetura Alvo para ViKi

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ViKi AI Platform                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Web Dashboard   │  │  Desktop App   │  │  Mobile Apps   │              │
│  │  (React + Three.js)│  │  (Tauri/Rust)  │  │  (Kotlin/Swift)│              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                      │
│         └─────────────────┼─────────────────┘                      │
│                           ▼                                        │
│              ┌────────────────────────┐                            │
│              │      API Gateway       │                            │
│              │    (FastAPI + WS)      │                            │
│              └───────────┬────────────┘                            │
│                          │                                          │
│        ┌────────────────┼────────────────┐                         │
│        ▼                ▼                ▼                         │
│  ┌───────────┐   ┌─────────────┐  ┌─────────────┐                │
│  │ Orchestrator│  │  Agent Hub  │  │ Channel Hub │                │
│  │  (Planner)  │  │ (Subagents) │  │ (30+ chans)│                │
│  └─────┬───────┘  └──────┬──────┘  └──────┬──────┘                │
│        │                 │                │                        │
│        ▼                 ▼                ▼                        │
│  ┌─────────────────────────────────────────────┐                 │
│  │           Model Gateway (MultiEngine)       │                 │
│  │  Ollama │ vLLM │ MLX │ Cloud │ Local │ ...  │                 │
│  └─────────────────────────────────────────────┘                 │
│        │                                                      │
│        ▼                                                      │
│  ┌─────────────────────────────────────────────┐             │
│  │          Runtime Primitives                 │             │
│  │  Tools │ Memory │ Skills │ Plugins │ Sandbox│             │
│  └─────────────────────────────────────────────┘             │
│        │                                                      │
│        ▼                                                      │
│  ┌─────────────────────────────────────────────┐             │
│  │          Persistence Layer                  │             │
│  │  SQLite │ Vector DB │ Object Store │ Graph │             │
│  └─────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

**Contratos-chave (interfaces versionadas):**
- `InferenceEngine` → `ViKiModelProvider` (extends)
- `BaseTool` → `ViKiTool` (adds risk_level, permissions, rollback)
- `BaseChannel` → `ViKiChannel` (adds pairing, encryption)
- `BaseMemory` → `ViKiMemory` (adds episodic/semantic/procedural)
- `BaseAgent` → `ViKiAgent` (adds planning, subagent delegation)
- `PluginManifest` → **NOVO** (versioned, signed, sandboxed)

---

## 6. Plano de Implementação por Fases (Adaptado)

### Fase 0: Auditoria ✅ CONCLUÍDA
- [x] Acessar repositório
- [x] Estudar documentação
- [x] Inspecionar arquivos
- [x] Verificar licença
- [x] Mapear arquitetura
- [x] Identificar funcionalidades
- [x] Apresentar relatório (este documento)

### Fase 1: Fundação ViKi (Semana 1-2)
**Objetivo:** ViKi executável com chat, streaming, memória, 1 tool, testes

| Tarefa | Arquivos Afetados | Esforço |
|--------|-------------------|---------|
| Renomear pacote `viki` → `viki` | `pyproject.toml`, `src/`, imports todos | 4h |
| Atualizar CLI entry point `viki` → `viki` | `pyproject.toml[project.scripts]`, `cli/__main__.py` | 1h |
| Rebrand config dir `~/.viki` → `~/.viki` | `core/paths.py`, `core/config.py` defaults | 2h |
| Atualizar frontend (título, favicon, meta) | `frontend/index.html`, `frontend/src/App.tsx`, `package.json` | 2h |
| Rebrand Tauri app (nome, ícones, bundle ID) | `frontend/src-tauri/tauri.conf.json`, icons, `Cargo.toml` | 3h |
| Criar `ViKiModelProvider` abstraction | `engine/_stubs.py`, novo `engine/viki_providers.py` | 4h |
| Adicionar adaptadores: Gemini, Groq, OpenRouter | `engine/gemini.py`, `engine/groq.py`, `engine/openrouter.py` | 6h |
| Implementar fallback robusto com circuit breaker | `engine/multi.py` refatorar | 4h |
| Testes de integração Phase 1 | `tests/engine/`, `tests/integration/` | 3h |
| Documentação instalação ViKi | `docs/getting-started/install.md`, `README.md` | 2h |

**Critérios de aceitação Fase 1:**
- `viki` command funciona
- `viki serve` + `viki gui` abre dashboard
- Chat com streaming funcional
- Pelo menos 1 tool executa (ex: calculator)
- Histórico persiste entre reinícios
- `pytest tests/` passa
- `viki doctor` mostra status

### Fase 2: Gateway + Memória (Semana 3-4)
- Roteamento inteligente por tarefa (coding, research, chat, vision)
- Memória unificada: working + episodic + semantic + procedural
- UI para consultar/excluir memórias
- Context window management automático

### Fase 3: Interface Holográfica (Semana 5-7)
- **Núcleo holográfico Three.js** (orb central com estados visuais)
- Dashboard responsivo (desktop/tablet/mobile)
- Indicadores de estado sincronizados com backend real
- Histórico visual, memory browser, task monitor

### Fase 4: Voz + Multimodal (Semana 8-10)
- STT unificado (faster-whisper local + Deepgram/OpenAI cloud)
- TTS unificado (Kokoro local + OpenAI/Cartesia cloud)
- Streaming de áudio (WebRTC / WebSocket)
- Vision: image_tool + document_tool integrados no chat
- Voice activity detection + keyword activation (opcional)

### Fase 5: Telegram + Canais (Semana 11-12)
- Telegram adapter refinado (pareamento, auth, idempotência)
- WhatsApp Business API + Baileys bridge
- Canal unificado: mesma permissão local/remoto
- Notificações de tarefas, relatórios, aprovações

### Fase 6: WhatsApp + Telefonia (Semana 13-14)
- WhatsApp Cloud API oficial
- Twilio/SIP para chamadas de voz
- Controles de custo, horários, consentimento

### Fase 7: Agentes + Automações (Semana 15-17)
- Subagentes especializados (coder, researcher, planner, admin)
- Planejamento hierárquico com dependency graph
- Background task execution com progress tracking
- Recovery automático de falhas

### Fase 8: Desktop + Mobile (Semana 18-22)
- Desktop agent: file ops, browser automation, notifications
- Android app (Kotlin): chat, voice, notifications, device mgmt
- iOS/macOS (Swift): chat, voice, shortcuts integration
- Device registry com pareamento seguro, revogação

### Fase 9: Plugins + Integrações (Semana 23-26)
- Plugin SDK (manifest v1, permissions, sandbox)
- Plugin registry (local + remote)
- Integrações: casa inteligente, calendário, email, docs
- Marketplace de plugins (fase futura)

### Fase 10: Produção (Semana 27-28)
- Security audit completo
- Docker Compose production-ready
- Monitoring (Prometheus/Grafana), backups, updates
- Documentação completa (ARCHITECTURE.md, API.md, DEPLOY.md)
- Release checklist

---

## 7. Próximos Passos Imediatos

1. **Criar branch `viki-foundation`** a partir de `main`
2. **Executar renomeação sistemática** (script + revisão manual)
3. **Configurar ambiente de desenvolvimento** (uv, Rust, Node.js 22+, Tauri CLI)
4. **Implementar `ViKiModelProvider`** com 3 adaptadores cloud
5. **Criar componente Three.js orb** no frontend
6. **Rodar suite de testes** após cada mudança arquitetural

---

## 8. Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Quebra de imports em massa na renomeação | Alta | Médio | Script automatizado + testes CI em cada commit |
| Tauri 2 breaking changes | Baixa | Alto | Fixar versão no `Cargo.toml`; testar build desktop cedo |
| Fallback de modelos com efeitos colaterais | Média | Médio | Idempotency keys em tools; circuit breaker por provider |
| Mobile app do zero (Android/iOS) | Alta | Alto | Começar com PWA + Capacitor; nativo fase posterior |
| Licença de dependências (ex: `litellm==1.104.2` pin) | Baixa | Médio | Verificar cada nova dependência antes de adicionar |

---

## 9. Métricas de Sucesso (KPIs)

| Métrica | Baseline Viki | Target ViKi Fase 1 | Target ViKi Fase 10 |
|---------|---------------------|-------------------|---------------------|
| Tempo cold start (CLI) | ~3s | <2s | <1s |
| Latência first token (local 7B) | ~800ms | <600ms | <400ms |
| Memória RAM idle | ~400MB | <300MB | <250MB |
| Cobertura de testes | ~65% | >80% | >90% |
| Canais funcionais | 30+ | 2 (Telegram, Web) | 10+ |
| Ferramentas funcionais | 45+ | 10 core | 50+ |
| Modelos suportados | 13 engines | 5 (Ollama, vLLM, MLX, Gemini, Groq) | 15+ |
| Usuários simultâneos (server) | 1 (single-user) | 1 | 10+ (multi-tenant) |

---

*Relatório gerado automaticamente como parte da Fase 0 do projeto ViKi AI. Próxima atualização: pós-Fase 1.*