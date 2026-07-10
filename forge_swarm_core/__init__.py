"""Forge Swarm Core — domain modules with backward-compatible re-exports."""

from __future__ import annotations

# ── Import in dependency order to avoid circular imports ────────────────
from forge_swarm_core._lazy import _crewai, _crewai_tools, _chromadb, _ollama, _litellm  # noqa: F401
from forge_swarm_core.core import Config, SystemChecker, ProjectStore  # noqa: F401
from forge_swarm_core.llm import LLMProvider, OllamaEmbeddings, LLMManager  # noqa: F401
from forge_swarm_core.sandbox import CodeSandbox  # noqa: F401
from forge_swarm_core.memory import MemoryManager  # noqa: F401
from forge_swarm_core.agents import AgentStatusDisplay, AgentFactory, CriticParser, TaskFactory  # noqa: F401
from forge_swarm_core.mcp_tools import MCPToolManager  # noqa: F401
from forge_swarm_core.orchestrator import (  # noqa: F401
    SwarmOrchestrator, parse_multi_file_output, TaskOrchestrator,
)
from forge_swarm_core.ui import (  # noqa: F401
    VisualPipelineGraph, FileUploadHandler, DARK_THEME_CSS,
    setup_wizard, get_memory_manager, render_sidebar,
)
