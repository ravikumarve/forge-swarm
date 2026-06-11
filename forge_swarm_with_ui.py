"""
Forge Swarm - Complete Production-Ready UI
Version: 1.0
Last updated: February 2026

A 100% local, offline, privacy-first multi-agent AI platform.
Fully refactored with proper error handling, configuration, and features.

Requirements:
    pip install streamlit crewai crewai-tools langchain-ollama chromadb python-dotenv pyyaml

Before running:
    1. Start Ollama: ollama serve
    2. Pull models: ollama pull llama3.1:8b && ollama pull nomic-embed-text
    3. Run: streamlit run forge_swarm_with_ui.py
"""

import os
import sys
import json
import subprocess
import traceback
import requests
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

# Disable telemetry BEFORE importing CrewAI
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy-ollama-only")

import streamlit as st
import yaml
from crewai import Agent, Task, Crew, Process
from crewai.llms.base_llm import BaseLLM

try:
    from crewai_tools import SerperDevTool

    SERPER_AVAILABLE = True
except ImportError:
    SERPER_AVAILABLE = False
    SerperDevTool = None
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import ollama
import litellm

load_dotenv()


class LLMProvider(BaseLLM):
    """Generic LLM provider supporting Ollama and NVIDIA NIM."""

    def __init__(
        self,
        provider: str,
        model: str,
        base_url: str = "",
        temperature: float = 0.7,
        num_ctx: int = 8192,
        api_key: str = "",
    ):
        super().__init__(model=model, base_url=base_url, temperature=temperature)
        self.provider = provider
        self.api_key = api_key
        self._num_ctx = num_ctx

        if provider == "ollama":
            self._litellm_model = f"ollama/{model}"
            self._api_base = base_url or "http://localhost:11434"
        elif provider == "nvidia_nim":
            self._litellm_model = f"nvidia_nim/{model}"
            self._api_base = base_url or "https://integrate.api.nvidia.com/v1"
            # Set API key for NVIDIA NIM
            if api_key:
                litellm.api_key = api_key
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def call(self, messages: list[dict], **kwargs) -> str:
        """Call the LLM via litellm."""
        # Extract CrewAI-specific kwargs
        tools = kwargs.pop("tools", None)
        callbacks = kwargs.pop("callbacks", None)
        available_functions = kwargs.pop("available_functions", None)
        from_task = kwargs.pop("from_task", None)
        from_agent = kwargs.pop("from_agent", None)
        response_model = kwargs.pop("response_model", None)

        # Build completion parameters
        completion_params = {
            "model": self._litellm_model,
            "messages": messages,
            "api_base": self._api_base,
            "temperature": self.temperature if self.temperature is not None else 0.7,
        }

        # Add provider-specific parameters
        if self.provider == "ollama":
            completion_params["num_ctx"] = self._num_ctx
        elif self.provider == "nvidia_nim":
            completion_params["max_tokens"] = self._num_ctx

        # Add any remaining kwargs
        completion_params.update(kwargs)

        response = litellm.completion(**completion_params)
        return response["choices"][0]["message"]["content"]

    def __call__(self, messages: list[dict], **kwargs) -> str:
        """Allow the instance to be called as a function."""
        return self.call(messages, **kwargs)


class OllamaEmbeddings:
    """Wrapper for ollama embeddings compatible with ChromaDB."""

    def __init__(
        self,
        model: str = "nomic-embed-text:latest",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        response = self.client.embeddings(model=self.model, prompt=text)
        return response["embedding"]


# ============================================================================
# DARK THEME CSS
# ============================================================================

DARK_THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Background & Text */
    .stApp { 
        background-color: #000000; 
        color: #e0e0e0; 
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Ambient Background Effect */
    .stApp::before {
        content: "";
        position: fixed;
        width: 80vw;
        height: 80vw;
        background: radial-gradient(circle, rgba(0, 243, 255, 0.03) 0%, transparent 70%);
        top: -20vh;
        left: -10vw;
        filter: blur(100px);
        z-index: 0;
        pointer-events: none;
    }
    
    .stApp::after {
        content: "";
        position: fixed;
        width: 60vw;
        height: 60vw;
        background: radial-gradient(circle, rgba(0, 255, 65, 0.02) 0%, transparent 70%);
        bottom: -10vh;
        right: -10vw;
        filter: blur(120px);
        z-index: 0;
        pointer-events: none;
    }
    
    /* Grain Texture Overlay */
    .stApp > div:first-child::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 9998;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 15, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Expanders */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 4px !important;
    }
    
    /* Text Areas */
    .stTextArea textarea {
        background-color: #0a0a0f !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }
    .stTextArea textarea:focus {
        border-color: #00f3ff !important;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.3) !important;
    }
    
    /* Text Inputs */
    .stTextInput input {
        background-color: #0a0a0f !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stTextInput input:focus {
        border-color: #00f3ff !important;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.3) !important;
    }
    
    /* Select Boxes */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #0a0a0f !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
    }
    
    /* Buttons - Primary */
    .stButton > button[kind="primary"] {
        background: rgba(0, 243, 255, 0.1) !important;
        color: #00f3ff !important;
        border: 1px solid rgba(0, 243, 255, 0.3) !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        font-size: 11px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: rgba(0, 243, 255, 0.2) !important;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.2) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Buttons - Secondary */
    .stButton > button:not([kind="primary"]) {
        background: rgba(255, 255, 255, 0.02) !important;
        color: rgba(255, 255, 255, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    .stTabs [data-baseweb="tab"] { 
        color: rgba(255, 255, 255, 0.4) !important; 
        font-weight: 500 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00f3ff !important;
        border-bottom: 2px solid #00f3ff !important;
    }
    
    /* Code Blocks */
    .stCodeBlock {
        background-color: #0a0a0a !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stCodeBlock pre {
        background-color: #0a0a0a !important;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0, 243, 255, 0.3); }
    
    /* Status elements */
    div[data-testid="stStatus"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
    }
    
    /* Toast notifications */
    .stToast {
        background: rgba(10, 10, 15, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    /* Tooltips */
    .stTooltip {
        background: rgba(10, 10, 15, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #e0e0e0 !important;
    }
    
    /* ===== GLASS CARD SYSTEM ===== */
    .glass-panel {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        padding: 16px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(0, 243, 255, 0.2);
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.05);
    }
    .glass-card.state-idle { border-color: rgba(255,255,255,0.05); opacity: 0.6; }
    .glass-card.state-active { border-color: rgba(0,243,255,0.4); box-shadow: 0 0 15px rgba(0,243,255,0.1); }
    .glass-card.state-done { border-color: rgba(0,255,65,0.3); opacity: 0.7; }
    .glass-card.state-error { border-color: rgba(255,0,255,0.4); box-shadow: 0 0 15px rgba(255,0,255,0.1); }
    .status-dot {
        width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 8px;
    }
    .status-dot.idle { background: rgba(255,255,255,0.2); }
    .status-dot.active { background: #00f3ff; box-shadow: 0 0 8px #00f3ff; animation: pulse-cyan 2s infinite; }
    .status-dot.done { background: #00ff41; }
    .status-dot.error { background: #ff00ff; box-shadow: 0 0 8px #ff00ff; }
    @keyframes pulse-cyan {
        0% { opacity: 1; box-shadow: 0 0 4px #00f3ff; }
        50% { opacity: 0.5; box-shadow: 0 0 16px #00f3ff; }
        100% { opacity: 1; box-shadow: 0 0 4px #00f3ff; }
    }
    .font-mono { font-family: 'JetBrains Mono', monospace; }
    .font-brand { font-family: 'Space Grotesk', sans-serif; }
    .section-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px; letter-spacing: 0.4em; text-transform: uppercase;
        color: rgba(255,255,255,0.4); border-left: 2px solid #00f3ff; padding-left: 12px;
    }
</style>
"""

class AgentStatusDisplay:
    """Renders real-time agent pipeline status in Streamlit."""

    AGENTS = [
        ("01", "Planner", "System architecture and mission mapping"),
        ("02", "Researcher", "Deep documentation and web search analysis"),
        ("03", "Coder", "Production-ready implementation entirely offline"),
        ("04", "Tester", "Unit testing and logic verification"),
        ("05", "Critic", "Self-improvement loop scoring (8/10 threshold)"),
    ]

    @staticmethod
    def render_pipeline(current_agent_idx: int = -1) -> None:
        """Render all 5 agents as status cards."""
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div class="section-tag">COGNITIVE_PIPELINE</div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(5)
        for i, (num, name, desc) in enumerate(AgentStatusDisplay.AGENTS):
            with cols[i]:
                if current_agent_idx == -1:
                    dot_class, card_class = "idle", "state-idle"
                elif i < current_agent_idx:
                    dot_class, card_class = "done", "state-done"
                elif i == current_agent_idx:
                    dot_class, card_class = "active", "state-active"
                else:
                    dot_class, card_class = "idle", "state-idle"
                
                st.markdown(
                    f'<div class="glass-card {card_class}" style="text-align: center;">'
                    f'  <div style="font-family: JetBrains Mono, monospace; font-size: 9px; color: rgba(255,255,255,0.4); margin-bottom: 12px;">{num}_{name.upper()}</div>'
                    f'  <div class="status-dot {dot_class}" style="margin: 0 auto 8px auto;"></div>'
                    f'  <div style="font-family: Space Grotesk, sans-serif; font-size: 14px; font-weight: 700; margin-bottom: 4px;">{name}</div>'
                    f'  <div style="font-size: 10px; color: rgba(255,255,255,0.4); line-height: 1.4;">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    @staticmethod
    def render_score(score: int, verdict: str) -> None:
        """Render critic score badge with LP2 styling."""
        if score >= 8:
            color = "#00ff41"
            glow = "0 0 20px rgba(0, 255, 65, 0.3)"
        elif score >= 6:
            color = "#f0ff00"
            glow = "0 0 20px rgba(240, 255, 0, 0.2)"
        else:
            color = "#ff00ff"
            glow = "0 0 20px rgba(255, 0, 255, 0.3)"
        
        st.markdown(
            f'<div style="margin: 16px 0; padding: 16px; background: rgba(255,255,255,0.02); '
            f'border: 1px solid {color}; border-radius: 4px; text-align: center; box-shadow: {glow};">'
            f'  <div style="font-family: JetBrains Mono, monospace; font-size: 10px; color: rgba(255,255,255,0.4); margin-bottom: 8px; letter-spacing: 0.2em;">CRITIC SCORE</div>'
            f'  <div style="font-family: Space Grotesk, sans-serif; font-size: 48px; font-weight: 700; color: {color}; line-height: 1;">{score}<span style="font-size: 18px; opacity: 0.6;">/10</span></div>'
            f'  <div style="font-family: JetBrains Mono, monospace; font-size: 11px; color: {color}; margin-top: 8px; letter-spacing: 0.1em; text-transform: uppercase;">{verdict}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )



# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================


class Config:
    """Centralized configuration management"""

    DEFAULT_CONFIG = {
        "llm": {
            "model": "llama3.1:8b",
            "base_url": "http://localhost:11434",
            "temperature": 0.7,
            "num_ctx": 8192,
            "timeout": 120,
        },
        "embeddings": {
            "model": "nomic-embed-text",
            "base_url": "http://localhost:11434",
        },
        "memory": {
            "db_path": "./forge_swarm_memory",
            "collection_name": "improvement_lessons",
            "max_lessons": 100,
            "retention_days": 180,
        },
        "agents": {
            "max_iterations": 3,
            "verbose": True,
            "allow_delegation": False,
            "quality_threshold": 8,
            "retry_on_below_threshold": True,
        },
        "ui": {"page_title": "Forge Swarm", "page_icon": "🤖", "layout": "wide"},
    }

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load config from file or return defaults"""
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    user_config = yaml.safe_load(f)
                # Merge with defaults
                config = cls.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except Exception as e:
                st.warning(f"Could not load config: {e}. Using defaults.")
        return cls.DEFAULT_CONFIG

    @classmethod
    def save(cls, config: Dict[str, Any], config_path: str = "config.yaml"):
        """Save config to file"""
        try:
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            st.error(f"Could not save config: {e}")
            return False

    @classmethod
    def get_ollama_config(cls, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Return Ollama-specific config block (llm + embeddings)."""
        if config is None:
            config = cls.load()
        return {
            "base_url": config.get("llm", {}).get("base_url", "http://localhost:11434"),
            "model": config.get("llm", {}).get("model", "llama3.1:8b"),
            "embedding_model": config.get("embeddings", {}).get(
                "model", "nomic-embed-text"
            ),
            "temperature": config.get("llm", {}).get("temperature", 0.7),
            "timeout": config.get("llm", {}).get("timeout", 120),
        }

    @classmethod
    def get_agent_config(cls, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Return agent-specific config block."""
        if config is None:
            config = cls.load()
        return {
            "max_iterations": config.get("agents", {}).get("max_iterations", 3),
            "verbose": config.get("agents", {}).get("verbose", True),
            "memory": True,
        }


# ============================================================================
# SYSTEM HEALTH CHECKS
# ============================================================================


class SystemChecker:
    """Check system dependencies and health"""

    @staticmethod
    @st.cache_data(ttl=5)
    def check_ollama() -> tuple[bool, str]:
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                return True, "Ollama is running"
            return False, f"Ollama returned status {response.status_code}"
        except Exception:
            return False, "Ollama is not running. Start it with: ollama serve"
    @staticmethod
    @st.cache_data(ttl=5)
    def get_available_models() -> List[str]:
        """Get list of available Ollama models from API, excluding embeddings."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Filter out embedding models
                models = [m for m in models if "embed" not in m.lower()]
                return models
            return []
        except Exception:
            return []

    @staticmethod
    def check_model(model_name: str) -> tuple[bool, str]:
        """Check if a model is available"""
        available = SystemChecker.get_available_models()

        if model_name in available:
            return True, f"Model {model_name} is available"

        if available:
            first_model = available[0]
            return True, f"Model {first_model} is available"

        return False, "No LLM model found. Pull one with: ollama pull qwen2.5:3b"

    @staticmethod
    @st.cache_data(ttl=10)
    def check_chromadb(persist_dir: str) -> tuple[bool, str]:
        """Check if ChromaDB can be initialized at path."""
        try:
            db_path = Path(persist_dir)
            db_path.mkdir(parents=True, exist_ok=True)

            test_client = chromadb.PersistentClient(
                path=str(db_path), settings=Settings(anonymized_telemetry=False)
            )
            test_collection = test_client.get_or_create_collection("test_check")
            test_client.delete_collection("test_check")
            return True, "ChromaDB is accessible"
        except Exception as e:
            return False, f"ChromaDB error: {str(e)}"

    @staticmethod
    def run_all_checks(config: Dict[str, Any]) -> Dict[str, tuple[bool, str]]:
        """Run all system checks, return dict of {check_name: (passed, message)}."""
        ollama_ok, ollama_msg = SystemChecker.check_ollama()

        # Check embedding model specifically
        emb_model = config.get("embeddings", {}).get("model", "nomic-embed-text")
        emb_ok, emb_msg = SystemChecker.check_embedding_model(emb_model)

        # Check LLM model
        available_models = SystemChecker.get_available_models()
        if available_models:
            model_ok, model_msg = True, f"Model {available_models[0]} is available"
        else:
            model_ok, model_msg = False, "No LLM model found"

        chromadb_path = config.get("memory", {}).get("db_path", "./forge_swarm_memory")
        chromadb_ok, chromadb_msg = SystemChecker.check_chromadb(chromadb_path)

        return {
            "ollama": (ollama_ok, ollama_msg),
            "model": (model_ok, model_msg),
            "embeddings": (emb_ok, emb_msg),
            "chromadb": (chromadb_ok, chromadb_msg),
        }

    @staticmethod
    def check_embedding_model(model_name: str) -> tuple[bool, str]:
        """Check if the embedding model is available."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check specifically for embedding models
                for m in models:
                    if "embed" in m.lower():
                        return True, f"Embeddings: {m}"
                return False, "Embedding model not found"
            return False, "Could not check embedding model"
        except Exception:
            return False, "Could not check embedding model"

    @staticmethod
    def get_best_available_model() -> str:
        """Return the first available LLM model (non-embedding)."""
        available = SystemChecker.get_available_models()
        if available:
            return available[0]
        return "qwen2.5:3b"  # Default fallback


# ============================================================================
# LLM MANAGER
# ============================================================================


class LLMManager:
    """Manage LLM and embeddings initialization"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._llm = None
        self._embedder = None

    @property
    def embedder(self) -> OllamaEmbeddings:
        """Lazy-load embeddings"""
        if self._embedder is None:
            emb_config = self.config["embeddings"]
            self._embedder = OllamaEmbeddings(
                model=emb_config["model"], base_url=emb_config["base_url"]
            )
        return self._embedder

    def test_connection(self) -> tuple[bool, str]:
        """Test LLM connection"""
        try:
            response = self.llm.invoke("Hello")
            return True, "LLM connection successful"
        except Exception as e:
            return False, f"LLM connection failed: {str(e)}"


# ============================================================================
# MEMORY MANAGER
# ============================================================================


class MemoryManager:
    """Manage long-term memory with ChromaDB"""

    def __init__(self, config: Dict[str, Any], embedder: OllamaEmbeddings):
        self.config = config["memory"]
        self.embedder = embedder
        self.client = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize ChromaDB"""
        try:
            db_path = self.config["db_path"]
            Path(db_path).mkdir(parents=True, exist_ok=True)

            self.client = chromadb.PersistentClient(
                path=db_path, settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.config["collection_name"]
            )
        except Exception as e:
            st.error(f"Failed to initialize memory database: {e}")
            raise

    def save_lesson(
        self, task_desc: str, output: str, critic_feedback: str, score: float
    ):
        """Save a lesson to memory"""
        try:
            text = f"Task: {task_desc}\nFeedback: {critic_feedback}"
            embedding = self.embedder.embed_documents([text])[0]

            lesson_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.collection.count()}"

            self.collection.add(
                documents=[critic_feedback],
                metadatas=[
                    {
                        "task": task_desc[:200],
                        "output_summary": output[:200],
                        "score": score,
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
                ids=[lesson_id],
                embeddings=[embedding],
            )

            # Prune old lessons if needed
            self._prune_old_lessons()

        except Exception as e:
            st.warning(f"Could not save lesson: {e}")

    def get_relevant_lessons(self, task_desc: str, n: int = 3) -> List[str]:
        """Retrieve similar past lessons"""
        try:
            if self.collection.count() == 0:
                return []

            query_emb = self.embedder.embed_documents([task_desc])[0]
            results = self.collection.query(
                query_embeddings=[query_emb], n_results=min(n, self.collection.count())
            )

            if not results["metadatas"] or not results["metadatas"][0]:
                return []

            lessons = []
            for metadata, doc in zip(results["metadatas"][0], results["documents"][0]):
                score = metadata.get("score", "N/A")
                task = metadata.get("task", "Unknown task")
                lessons.append(f"[Score: {score}] {task}: {doc}")

            return lessons

        except Exception as e:
            st.warning(f"Could not retrieve lessons: {e}")
            return []

    def _prune_old_lessons(self):
        """Remove old lessons to stay within max_lessons limit"""
        try:
            max_lessons = self.config["max_lessons"]
            current_count = self.collection.count()

            if current_count > max_lessons:
                # Get all items sorted by timestamp
                all_items = self.collection.get()
                if all_items["metadatas"]:
                    # Sort by timestamp and remove oldest
                    items_with_time = [
                        (id_, meta.get("timestamp", ""))
                        for id_, meta in zip(all_items["ids"], all_items["metadatas"])
                    ]
                    items_with_time.sort(key=lambda x: x[1])

                    # Remove oldest items
                    to_remove = items_with_time[: current_count - max_lessons]
                    ids_to_remove = [item[0] for item in to_remove]

                    if ids_to_remove:
                        self.collection.delete(ids=ids_to_remove)

        except Exception as e:
            st.warning(f"Could not prune old lessons: {e}")

    def export_memory(self) -> str:
        """Export all stored lessons as JSON string for download."""
        try:
            results = self.collection.get(include=["documents", "metadatas"])
            export = {
                "exported_at": datetime.now().isoformat(),
                "collection": self.collection.name,
                "count": len(results["documents"]),
                "lessons": [
                    {"document": doc, "metadata": meta}
                    for doc, meta in zip(results["documents"], results["metadatas"])
                ],
            }
            return json.dumps(export, indent=2)
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return json.dumps({"error": str(e)})

    def search_memory(self, query: str, n_results: int = 10) -> List[Dict]:
        """Search memory with text query, return ranked results."""
        try:
            count = self.collection.count()
            if count == 0:
                return []
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
                include=["documents", "metadatas", "distances"],
            )
            return [
                {
                    "task": meta.get("task_description", "Unknown"),
                    "result": doc,
                    "score": meta.get("quality_score", 0),
                    "distance": round(dist, 4),
                    "stored_at": meta.get("stored_at", "Unknown"),
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        except Exception as e:
            print(f"❌ Memory search failed: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            return {
                "total_lessons": self.collection.count(),
                "collection_name": self.config["collection_name"],
                "max_lessons": self.config["max_lessons"],
            }
        except Exception:
            return {"total_lessons": 0}

    def clear_memory(self) -> bool:
        """Delete all stored memories. Returns True on success."""
        try:
            self.collection.delete(where={})
            return True
        except Exception as e:
            st.error(f"Could not clear memory: {e}")
            return False

    def store_result(
        self,
        task_id: str,
        task_description: str,
        result: str,
        quality_score: int = 0,
        iterations: int = 1,
    ) -> None:
        """Store a completed task result - only if score meets threshold."""
        min_score = self.config.get("min_score_to_store", 7)
        if quality_score < min_score:
            print(
                f"⚠️ Score {quality_score} below threshold {min_score}. Skipping storage."
            )
            return
        try:
            text = f"Task: {task_description}\nResult: {result}"
            embedding = self.embedder.embed_documents([text])[0]

            self.collection.add(
                documents=[result],
                metadatas=[
                    {
                        "task_id": task_id,
                        "task_description": task_description[:500],
                        "quality_score": quality_score,
                        "iterations": iterations,
                        "stored_at": datetime.now().isoformat(),
                    }
                ],
                ids=[task_id],
                embeddings=[embedding],
            )
            print(f"💾 Stored lesson (score: {quality_score}/10)")
        except Exception as e:
            print(f"❌ Failed to store result: {e}")

    def query_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """Return top-n similar past results as dicts (alias for get_relevant_lessons)."""
        lessons = self.get_relevant_lessons(query, n_results)
        return [{"lesson": lesson} for lesson in lessons]

    def get_memory_stats(self) -> Dict[str, int]:
        """Return count of stored items and collection size."""
        stats = self.get_stats()
        return {
            "items_stored": stats.get("total_lessons", 0),
            "collection_size": stats.get("total_lessons", 0),
        }


# ============================================================================
# AGENT FACTORY
# ============================================================================


class AgentFactory:
    """Create and manage agents"""

    def __init__(self, llm: LLMProvider, config: Dict[str, Any]):
        self.llm = llm
        self.config = config["agents"]

    def create_planner(self) -> Agent:
        """Create planner agent - Strategic Engineering Lead"""
        return Agent(
            role="Strategic Engineering Lead",
            goal="Decompose any coding request into a precise, dependency-ordered execution plan with clear acceptance criteria per subtask.",
            backstory=(
                "15 years shipping production systems across fintech, healthcare, and SaaS. "
                "Has a pathological hatred of ambiguity. Every plan you write must answer: "
                "What are we building? What does done look like? What can go wrong? "
                "You think in trees — break the root problem into branches, branches into leaves. "
                "Output format: numbered tasks, each with input, output, and acceptance criteria."
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_researcher(self, enable_web_search: bool = False) -> Agent:
        """Create researcher agent - Principal Technical Researcher"""
        tools = []
        if enable_web_search and SERPER_AVAILABLE:
            try:
                tools.append(SerperDevTool())
            except Exception:
                pass

        return Agent(
            role="Principal Technical Researcher",
            goal="Produce a concise, high-signal research brief covering the best implementation patterns, known pitfalls, and idiomatic approaches for the task.",
            backstory=(
                "Obsessive reader of RFCs, PEPs, source code, and engineering blogs. "
                "Knows when to use a library vs roll your own. Hates cargo-culting. "
                "Every research brief must include: recommended approach, alternatives considered, "
                "top 3 gotchas, and one non-obvious insight the coder would miss."
            ),
            tools=tools,
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_coder(self) -> Agent:
        """Create coder agent - Senior Software Craftsperson"""
        return Agent(
            role="Senior Software Craftsperson",
            goal="Write complete, production-grade, immediately runnable code based on the plan and research brief. No placeholders. No TODOs without tracking. No magic numbers.",
            backstory=(
                "Treats code like prose. Every function has one job. Every variable name "
                "tells a story. Uses type hints everywhere. Writes comments that explain "
                "WHY, not WHAT. Has strong opinions: explicit > implicit, simple > clever, "
                "boring > exciting. Will refuse to ship code that 'works but is embarrassing.'"
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_tester(self) -> Agent:
        """Create tester agent - Adversarial QA Engineer"""
        return Agent(
            role="Adversarial QA Engineer",
            goal="Write a complete test suite that tries to break the code before production does.",
            backstory=(
                "Broke prod 3 times early in career. Now sees failure modes everywhere. "
                "Writes tests in three categories: "
                "1. Happy path — does it work when everything is correct? "
                "2. Sad path — does it fail gracefully when inputs are wrong? "
                "3. Evil path — what happens with None, empty strings, huge numbers, unicode? "
                "Uses pytest. Aims for 80%+ coverage. Names tests like documentation."
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_critic(self) -> Agent:
        """Create critic agent - Principal Engineer & Gatekeeper"""
        return Agent(
            role="Principal Engineer & Gatekeeper",
            goal="Score the complete output (code + tests) on a scale of 1-10 with surgical specificity. Approve if score >= 8. Request targeted revisions if below.",
            backstory=(
                "Zero tolerance for mediocrity. Has reviewed 10,000+ PRs. Scores on: "
                "- Correctness (does it actually work?) "
                "- Readability (can a junior follow it?) "
                "- Robustness (does it handle edge cases?) "
                "- Idiomatic style (is it Pythonic?) "
                "- Test coverage (are the tests meaningful?) "
                "Output format MUST be: "
                "SCORE: X/10 "
                "VERDICT: APPROVED / REVISION REQUIRED "
                "ISSUES: [bulleted list of specific line-level issues] "
                "REQUIRED CHANGES: [only if REVISION REQUIRED]"
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_all(self) -> Dict[str, Agent]:
        """Create all agents, return as named dict."""
        return {
            "planner": self.create_planner(),
            "researcher": self.create_researcher(),
            "coder": self.create_coder(),
            "tester": self.create_tester(),
            "critic": self.create_critic(),
        }


# ============================================================================
# CRITIC PARSER
# ============================================================================


class CriticParser:
    """Parses structured Critic agent output into typed fields."""

    @staticmethod
    def parse(critic_output: str) -> Dict[str, Any]:
        """
        Extract score, verdict, issues, and required changes from critic output.

        Returns:
            Dict with keys: score (int), verdict (str), issues (List[str]),
            required_changes (List[str]), approved (bool)
        """
        result = {
            "score": 0,
            "verdict": "UNKNOWN",
            "issues": [],
            "required_changes": [],
            "approved": False,
        }

        lines = critic_output.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    score_str = line.replace("SCORE:", "").strip()
                    result["score"] = int(score_str.split("/")[0])
                except (ValueError, IndexError):
                    result["score"] = 0
            elif line.startswith("VERDICT:"):
                result["verdict"] = line.replace("VERDICT:", "").strip()
                result["approved"] = "APPROVED" in result["verdict"].upper()
            elif line.startswith("ISSUES:"):
                current_section = "issues"
            elif line.startswith("REQUIRED CHANGES:"):
                current_section = "required_changes"
            elif line.startswith("- ") and current_section:
                result[current_section].append(line[2:])

        return result


# ============================================================================
# TASK FACTORY
# ============================================================================


class TaskFactory:
    """Create and manage tasks"""

    @staticmethod
    def create_plan_task(
        user_query: str, past_lessons: List[str], agent: Agent
    ) -> Task:
        """Create planning task"""
        lessons_str = (
            "\n".join(past_lessons)
            if past_lessons
            else "No previous lessons available."
        )

        return Task(
            description=(
                f"Create a detailed step-by-step plan for the following request:\n\n"
                f"USER REQUEST: {user_query}\n\n"
                f"PAST LESSONS (apply if relevant):\n{lessons_str}\n\n"
                f"Your plan should:\n"
                f"1. Break the task into clear, numbered steps\n"
                f"2. Specify which agent should handle each step (Researcher, Coder, Tester)\n"
                f"3. Identify dependencies between steps\n"
                f"4. Consider potential challenges and mitigation strategies\n"
                f"5. Apply relevant lessons from past attempts\n\n"
                f"Output format: Numbered plan with clear agent assignments and rationale."
            ),
            expected_output="Detailed numbered plan with agent assignments and dependencies",
            agent=agent,
        )

    @staticmethod
    def create_research_task(plan: str, agent: Agent) -> Task:
        """Create research task"""
        return Task(
            description=(
                f"Based on this plan:\n{plan}\n\n"
                f"Perform necessary research:\n"
                f"1. Identify what information is needed\n"
                f"2. Find relevant documentation, best practices, examples\n"
                f"3. Verify information from multiple sources when possible\n"
                f"4. Summarize key findings\n\n"
                f"If no research is needed, state: 'No research needed - sufficient context available'\n"
            ),
            expected_output="Research findings summary or 'No research needed'",
            agent=agent,
        )

    @staticmethod
    def create_code_task(plan: str, research: str, agent: Agent) -> Task:
        """Create coding task"""
        return Task(
            description=(
                f"PLAN:\n{plan}\n\n"
                f"RESEARCH:\n{research}\n\n"
                f"Implement the solution:\n"
                f"1. Write clean, well-structured code\n"
                f"2. Include proper error handling\n"
                f"3. Add comments for complex logic\n"
                f"4. Follow language-specific best practices\n"
                f"5. Include usage examples if applicable\n"
                f"6. Consider security and performance\n\n"
                f"Provide:\n"
                f"- Complete, runnable code\n"
                f"- Brief explanation of key decisions\n"
                f"- Any assumptions made\n"
            ),
            expected_output="Complete code implementation with explanation",
            agent=agent,
        )

    @staticmethod
    def create_test_task(code: str, agent: Agent) -> Task:
        """Create testing task"""
        return Task(
            description=(
                f"CODE TO TEST:\n{code}\n\n"
                f"Create comprehensive tests:\n"
                f"1. Write unit tests for key functions\n"
                f"2. Test edge cases and error conditions\n"
                f"3. Include integration test scenarios\n"
                f"4. Suggest manual testing steps\n"
                f"5. If APIs are involved, suggest Keploy recording commands\n\n"
                f"Provide:\n"
                f"- Test code (using appropriate framework)\n"
                f"- List of test scenarios covered\n"
                f"- Any additional testing recommendations\n"
            ),
            expected_output="Test code and testing recommendations",
            agent=agent,
        )

    @staticmethod
    def create_critic_task(all_outputs: str, agent: Agent) -> Task:
        """Create critic/review task"""
        return Task(
            description=(
                f"REVIEW ALL OUTPUTS:\n{all_outputs}\n\n"
                f"Provide a critical review:\n\n"
                f"1. SCORE (1-10):\n"
                f"   - Accuracy (3 pts): Is the solution correct?\n"
                f"   - Completeness (2 pts): Does it fully address the request?\n"
                f"   - Code Quality (2 pts): Is it clean and maintainable?\n"
                f"   - Security (2 pts): Are there security concerns?\n"
                f"   - Best Practices (1 pt): Does it follow standards?\n\n"
                f"2. STRENGTHS: What was done well?\n\n"
                f"3. WEAKNESSES: What issues exist?\n\n"
                f"4. IMPROVEMENTS: Specific suggestions to fix issues\n\n"
                f"5. KEPLOY TESTING: If code/APIs are involved, provide specific commands:\n"
                f"   Example: keploy record --cmd 'python app.py' --port 8000\n\n"
                f"6. VERDICT: If score < 8, state 'REPLAN NEEDED' with reasons\n\n"
                f"Be thorough but fair. Focus on actionable feedback."
            ),
            expected_output="Structured critic report with score and specific feedback",
            agent=agent,
        )


# ============================================================================
# SWARM ORCHESTRATOR
# ============================================================================


class SwarmOrchestrator:
    """Orchestrate the multi-agent workflow"""

    def __init__(
        self,
        llm_manager: LLMManager,
        memory_manager: MemoryManager,
        config: Dict[str, Any],
    ):
        self.llm_manager = llm_manager
        self.memory = memory_manager
        self.config = config
        self.agent_factory = AgentFactory(llm_manager.llm, config)

    def execute(
        self, user_query: str, enable_web_search: bool = False, max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Execute the swarm workflow"""

        # Create agents
        planner = self.agent_factory.create_planner()
        researcher = self.agent_factory.create_researcher(enable_web_search)
        coder = self.agent_factory.create_coder()
        tester = self.agent_factory.create_tester()
        critic = self.agent_factory.create_critic()

        best_result = None
        best_score = 0

        for iteration in range(max_iterations):
            try:
                st.info(f"🔄 Iteration {iteration + 1}/{max_iterations}")

                # Get relevant lessons
                past_lessons = self.memory.get_relevant_lessons(user_query)

                # Create tasks
                plan_task = TaskFactory.create_plan_task(
                    user_query, past_lessons, planner
                )

                # Execute planning first
                st.write("📋 Planning...")
                plan_crew = Crew(
                    agents=[planner],
                    tasks=[plan_task],
                    process=Process.sequential,
                    verbose=False,
                )
                plan_result = plan_crew.kickoff()
                plan_output = str(plan_result)

                # Research
                st.write("🔍 Researching...")
                research_task = TaskFactory.create_research_task(
                    plan_output, researcher
                )
                research_crew = Crew(
                    agents=[researcher],
                    tasks=[research_task],
                    process=Process.sequential,
                    verbose=False,
                )
                research_result = research_crew.kickoff()
                research_output = str(research_result)

                # Code
                st.write("💻 Coding...")
                code_task = TaskFactory.create_code_task(
                    plan_output, research_output, coder
                )
                code_crew = Crew(
                    agents=[coder],
                    tasks=[code_task],
                    process=Process.sequential,
                    verbose=False,
                )
                code_result = code_crew.kickoff()
                code_output = str(code_result)

                # Test
                st.write("🧪 Testing...")
                test_task = TaskFactory.create_test_task(code_output, tester)
                test_crew = Crew(
                    agents=[tester],
                    tasks=[test_task],
                    process=Process.sequential,
                    verbose=False,
                )
                test_result = test_crew.kickoff()
                test_output = str(test_result)

                # Critic review
                st.write("⚖️ Reviewing...")
                all_outputs = f"PLAN:\n{plan_output}\n\nRESEARCH:\n{research_output}\n\nCODE:\n{code_output}\n\nTESTS:\n{test_output}"
                critic_task = TaskFactory.create_critic_task(all_outputs, critic)
                critic_crew = Crew(
                    agents=[critic],
                    tasks=[critic_task],
                    process=Process.sequential,
                    verbose=False,
                )
                critic_result = critic_crew.kickoff()
                critic_output = str(critic_result)

                # Extract score
                score = self._extract_score(critic_output)

                # Save to memory
                self.memory.save_lesson(user_query, all_outputs, critic_output, score)

                # Track best result
                if score > best_score:
                    best_score = score
                    best_result = {
                        "plan": plan_output,
                        "research": research_output,
                        "code": code_output,
                        "tests": test_output,
                        "critique": critic_output,
                        "score": score,
                        "iteration": iteration + 1,
                    }

                # Check if we should stop
                if score >= 8:
                    st.success(f"✅ High quality output achieved (Score: {score}/10)")
                    break
                elif iteration < max_iterations - 1:
                    st.warning(f"⚠️ Score: {score}/10. Retrying with feedback...")

            except Exception as e:
                st.error(f"Error in iteration {iteration + 1}: {str(e)}")
                if best_result is None and iteration == max_iterations - 1:
                    raise

        return best_result or {"error": "All iterations failed", "score": 0}

    def _extract_score(self, critic_output: str) -> float:
        """Extract numeric score from critic output"""
        try:
            # Look for patterns like "Score: 8/10" or "8/10" or "SCORE: 8"
            import re

            patterns = [
                r"score[:\s]+(\d+(?:\.\d+)?)\s*/\s*10",
                r"(\d+(?:\.\d+)?)\s*/\s*10",
                r"score[:\s]+(\d+(?:\.\d+)?)",
            ]

            for pattern in patterns:
                match = re.search(pattern, critic_output.lower())
                if match:
                    return float(match.group(1))

            return 5.0  # Default mid-score if not found

        except Exception:
            return 5.0


# ============================================================================
# TASK ORCHESTRATOR
# ============================================================================


class TaskOrchestrator:
    """Orchestrates task creation and crew execution with retry loop."""

    def __init__(self, agents: Dict[str, Agent], config: Dict[str, Any]):
        self.agents = agents
        self.config = config

    def build_tasks(self, user_request: str, context: str = "") -> List[Task]:
        """Create ordered task list from user request."""
        tasks = []

        # Planning task
        plan_task = Task(
            description=(
                f"Create a detailed step-by-step plan for:\n\n{user_request}\n\n"
                f"Context:\n{context}\n\n"
                f"Output format: numbered tasks, each with input, output, and acceptance criteria."
            ),
            expected_output="Numbered plan with acceptance criteria",
            agent=self.agents["planner"],
        )
        tasks.append(plan_task)

        # Research task
        research_task = Task(
            description=(
                f"Based on the plan, research implementation patterns.\n"
                f"Include: recommended approach, alternatives, top 3 gotchas, one non-obvious insight."
            ),
            expected_output="Research brief with patterns and pitfalls",
            agent=self.agents["researcher"],
        )
        tasks.append(research_task)

        # Coding task
        code_task = Task(
            description=(
                f"Write complete, production-grade code.\n"
                f"No placeholders. No TODOs. No magic numbers. Use type hints."
            ),
            expected_output="Complete runnable code",
            agent=self.agents["coder"],
        )
        tasks.append(code_task)

        # Testing task
        test_task = Task(
            description=(
                f"Write pytest test suite covering: happy path, sad path, evil path.\n"
                f"Include edge cases: None, empty strings, huge numbers, unicode."
            ),
            expected_output="Complete test suite",
            agent=self.agents["tester"],
        )
        tasks.append(test_task)

        # Critic task
        critic_task = Task(
            description=(
                f"Review all output and score quality 1-10.\n"
                f"Output format MUST be:\n"
                f"SCORE: X/10\n"
                f"VERDICT: APPROVED / REVISION REQUIRED\n"
                f"ISSUES: [bulleted list]\n"
                f"REQUIRED CHANGES: [if REVISION REQUIRED]"
            ),
            expected_output="SCORE, VERDICT, ISSUES, REQUIRED CHANGES",
            agent=self.agents["critic"],
        )
        tasks.append(critic_task)

        return tasks

    def run(self, user_request: str, context: str = "") -> Dict[str, Any]:
        """
        Execute the crew with retry loop based on Critic score.

        Returns:
            Dict with keys: final_code (str), critic_result (dict),
            iterations (int), agent_log (str)
        """
        quality_threshold = self.config["agents"]["quality_threshold"]
        max_iterations = self.config["agents"]["max_iterations"]
        retry = self.config["agents"]["retry_on_below_threshold"]

        iteration = 0
        last_result = None
        agent_log = []

        while iteration < max_iterations:
            iteration += 1
            agent_log.append(f"🔄 Iteration {iteration}/{max_iterations}")

            tasks = self.build_tasks(user_request, context)
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
            )

            try:
                result = crew.kickoff()
                critic_data = CriticParser.parse(str(result))
                agent_log.append(f"📊 Critic score: {critic_data['score']}/10")

                last_result = {
                    "final_code": str(result),
                    "critic_result": critic_data,
                    "iterations": iteration,
                    "agent_log": "\n".join(agent_log),
                }
            except Exception as e:
                agent_log.append(f"❌ Error: {str(e)}")
                last_result = {
                    "final_code": "",
                    "critic_result": {
                        "score": 0,
                        "verdict": "ERROR",
                        "approved": False,
                        "issues": [str(e)],
                    },
                    "iterations": iteration,
                    "agent_log": "\n".join(agent_log),
                }
                break

            if critic_data["approved"] or critic_data["score"] >= quality_threshold:
                agent_log.append(f"✅ Approved at iteration {iteration}")
                break

            if not retry:
                break

            context += f"\n\nPrevious attempt issues:\n" + "\n".join(
                critic_data["required_changes"]
            )
            agent_log.append("⚠️ Below threshold. Retrying with critic feedback.")

        return last_result


# ============================================================================
# SETUP WIZARD
# ============================================================================


def setup_wizard():
    """First-time setup wizard"""
    st.title("🛠️ Forge Swarm Setup Wizard")

    st.write("Let's check your system and get everything ready...")

    # Check Ollama
    with st.spinner("Checking Ollama..."):
        ollama_ok, ollama_msg = SystemChecker.check_ollama()

    if ollama_ok:
        st.success(f"✅ {ollama_msg}")
    else:
        st.error(f"❌ {ollama_msg}")
        st.code("# Start Ollama with:\nollama serve")
        return False

    # Check models
    config = Config.load()
    llm_model = config["llm"]["model"]
    emb_model = config["embeddings"]["model"]

    with st.spinner(f"Checking model: {llm_model}..."):
        llm_ok, llm_msg = SystemChecker.check_model(llm_model)

    if llm_ok:
        st.success(f"✅ {llm_msg}")
    else:
        st.error(f"❌ {llm_msg}")
        if st.button(f"Pull {llm_model} now (this may take a while)"):
            with st.spinner("Downloading model..."):
                try:
                    subprocess.run(["ollama", "pull", llm_model], check=True)
                    st.success("Model downloaded!")
                    st.rerun()
                except Exception:
                    st.error("Failed to download model. Please run manually.")
        return False

    with st.spinner(f"Checking embeddings model: {emb_model}..."):
        emb_ok, emb_msg = SystemChecker.check_model(emb_model)

    if emb_ok:
        st.success(f"✅ {emb_msg}")
    else:
        st.error(f"❌ {emb_msg}")
        if st.button(f"Pull {emb_model} now"):
            with st.spinner("Downloading embeddings model..."):
                try:
                    subprocess.run(["ollama", "pull", emb_model], check=True)
                    st.success("Embeddings model downloaded!")
                    st.rerun()
                except Exception:
                    st.error("Failed to download model. Please run manually.")
        return False

    # Test LLM connection
    with st.spinner("Testing LLM connection..."):
        try:
            llm_manager = LLMManager(config)
            test_ok, test_msg = llm_manager.test_connection()
            if test_ok:
                st.success(f"✅ {test_msg}")
            else:
                st.error(f"❌ {test_msg}")
                return False
        except Exception as e:
            st.error(f"❌ LLM test failed: {e}")
            return False

    st.success("🎉 All systems ready! Click 'Continue to App' below.")

    if st.button("Continue to App", type="primary"):
        st.session_state.setup_complete = True
        st.rerun()

    return True


# ============================================================================
# CODE SANDBOX
# ============================================================================


class CodeSandbox:
    """Safe, restricted Python code execution using RestrictedPython."""

    def __init__(self, config: Dict[str, Any]):
        self.timeout = config.get("sandbox", {}).get("timeout_seconds", 10)
        self.max_lines = config.get("sandbox", {}).get("max_output_lines", 100)
        self.enabled = config.get("sandbox", {}).get("enabled", True)

    def execute(self, code: str) -> Dict[str, Any]:
        """Execute a Python code snippet safely."""
        if not self.enabled:
            return {
                "output": "",
                "error": "Sandbox disabled in config",
                "success": False,
                "truncated": False,
            }

        import io
        import contextlib
        from RestrictedPython import compile_restricted, safe_globals

        result = {"output": "", "error": None, "success": False, "truncated": False}
        try:
            byte_code = compile_restricted(code, "<sandbox>", "exec")
            output_buffer = io.StringIO()
            restricted_globals = {**safe_globals, "_print_": print}
            with contextlib.redirect_stdout(output_buffer):
                exec(byte_code, restricted_globals)  # noqa: S102
            lines = output_buffer.getvalue().split("\n")
            if len(lines) > self.max_lines:
                lines = lines[: self.max_lines]
                result["truncated"] = True
            result["output"] = "\n".join(lines)
            result["success"] = True
        except SyntaxError as e:
            result["error"] = f"Syntax error: {e}"
        except Exception as e:
            result["error"] = f"Runtime error: {type(e).__name__}: {e}"
        return result

    def render_ui(self, code: str) -> None:
        """Render sandbox execution UI in Streamlit."""
        st.markdown("### 🧪 Code Sandbox")
        st.caption(
            "⚠️ Restricted execution — safe imports only. No filesystem or network access."
        )
        editable = st.text_area(
            "Edit before running", value=code, height=300, key="sandbox_code"
        )
        if st.button("▶️ Run Code", type="primary"):
            with st.spinner("Executing..."):
                result = self.execute(editable)
            if result["success"]:
                st.success("✅ Execution successful")
                if result["output"]:
                    st.code(result["output"], language="text")
                    if result["truncated"]:
                        st.warning(f"Output truncated to {self.max_lines} lines")
                else:
                    st.info("No output produced")
            else:
                st.error(f"❌ {result['error']}")


# ============================================================================
# FILE UPLOAD HANDLER
# ============================================================================


class FileUploadHandler:
    """Handles file uploads for context injection into agent runs."""

    SUPPORTED_TYPES = ["py", "txt", "md", "json", "yaml", "toml", "js", "ts"]
    MAX_FILE_SIZE_KB = 500

    @staticmethod
    def render_upload_ui() -> Optional[str]:
        """Render file upload widget, return file contents or None."""
        uploaded = st.file_uploader(
            "Upload a file for context",
            type=FileUploadHandler.SUPPORTED_TYPES,
            help=f"Max {FileUploadHandler.MAX_FILE_SIZE_KB}KB",
        )
        if uploaded is None:
            return None
        size_kb = uploaded.size / 1024
        if size_kb > FileUploadHandler.MAX_FILE_SIZE_KB:
            st.error(
                f"❌ File too large ({size_kb:.0f}KB). Max {FileUploadHandler.MAX_FILE_SIZE_KB}KB."
            )
            return None
        try:
            contents = uploaded.read().decode("utf-8")
            st.success(f"✅ Loaded `{uploaded.name}` ({size_kb:.1f}KB)")
            with st.expander("Preview"):
                st.code(contents[:800] + ("..." if len(contents) > 800 else ""))
            return f"# File: {uploaded.name}\n\n{contents}"
        except UnicodeDecodeError:
            st.error("❌ Could not decode file. Upload a text file.")
            return None


# ============================================================================
# MAIN UI
# ============================================================================


def main() -> None:
    """Main application"""
    st.set_page_config(
        page_title="⚡ Forge Swarm",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

    config = Config.load()

    # Session state initialization
    if "run_history" not in st.session_state:
        st.session_state.run_history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False
    if "template_loaded" not in st.session_state:
        st.session_state.template_loaded = ""

    # Initialize memory manager for sidebar
    if "memory_manager" not in st.session_state:
        try:
            llm_manager = LLMManager(config)
            st.session_state.memory_manager = MemoryManager(
                config, llm_manager.embedder
            )
        except Exception:
            st.session_state.memory_manager = None

    # ── SIDEBAR ──────────────────────────────────────────────
    # ── SIDEBAR (Command Deck) ──────────────────────────────
    with st.sidebar:
        # Compact Brand Header
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                FORGE_SWARM
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: rgba(255,255,255,0.4); letter-spacing: 0.1em; text-transform: uppercase;">
                v3.0 // Local Multi-Agent AI
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # System Status - Compact Row
        checks = SystemChecker.run_all_checks(config)
        st.markdown("### SYS_STATUS", help="System health indicators")
        
        status_html = "<div style='display: flex; gap: 8px; margin-bottom: 20px;'>"
        for name, (passed, _) in checks.items():
            icon = "●" if passed else "○"
            color = "#00ff41" if passed else "#ff00ff"
            status_html += f"<span title='{name}' style='color: {color}; font-size: 14px;'>{icon}</span>"
        status_html += "</div>"
        st.markdown(status_html, unsafe_allow_html=True)
        
        # Model / Provider - Compact
        st.markdown("### CONFIG", help="AI Model settings")
        llm_config = config["llm"]
        current_provider = llm_config.get("provider", "ollama")
        
        # Provider toggle
        provider = st.selectbox(
            "Provider",
            options=["ollama", "nvidia_nim"],
            index=0 if current_provider == "ollama" else 1,
            label_visibility="collapsed",
        )
        
        if provider != current_provider:
            config["llm"]["provider"] = provider
            st.rerun()
        
        # Model selector
        if provider == "ollama":
            available_models = SystemChecker.get_available_models()
            if available_models:
                current_model = config["llm"]["model"]
                if current_model not in available_models:
                    current_model = available_models[0]
                model = st.selectbox(
                    "Model",
                    options=available_models,
                    index=available_models.index(current_model) if current_model in available_models else 0,
                    label_visibility="collapsed",
                )
            else:
                model = st.text_input("Model", value=config["llm"]["model"], label_visibility="collapsed")
                if not model:
                    model = "qwen2.5:3b"
        elif provider == "nvidia_nim":
            nim_models_config = config.get("nvidia_nim", {}).get("models", [])
            nim_model_options = []
            nim_model_ids = []
            
            for model_data in nim_models_config:
                model_id = model_data.get("id", "")
                model_name = model_data.get("name", model_id)
                nim_model_options.append(model_name)
                nim_model_ids.append(model_id)
            
            if not nim_model_options:
                nim_model_ids = [
                    "meta/llama-3.1-8b-instruct",
                    "meta/llama-3.1-70b-instruct",
                    "mistralai/mistral-7b-instruct-v0.3",
                ]
                nim_model_options = nim_model_ids
            
            current_model = config["nvidia_nim"]["model"]
            try:
                current_index = nim_model_ids.index(current_model)
            except ValueError:
                current_index = 0
            
            selected_option = st.selectbox(
                "Model",
                options=nim_model_options,
                index=current_index,
                label_visibility="collapsed",
            )
            model = nim_model_ids[nim_model_options.index(selected_option)]
            config["nvidia_nim"]["model"] = model
            
            # NIM API Key
            nim_config = config["nvidia_nim"]
            api_key = st.text_input(
                "API Key",
                value=nim_config.get("api_key", ""),
                type="password",
                label_visibility="collapsed",
            )
            if api_key:
                config["nvidia_nim"]["api_key"] = api_key
                os.environ["NIM_API_KEY"] = api_key

        st.markdown("---")
        
        # Memory - Compact Card
        memory_manager = st.session_state.memory_manager
        if memory_manager:
            stats = memory_manager.get_memory_stats()
            count = stats.get("items_stored", 0)
        else:
            count = 0
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 12px; margin-bottom: 16px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: rgba(255,255,255,0.4); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px;">
                VECTOR_MEMORY
            </div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #00f3ff;">
                {count}
                <span style="font-size: 11px; color: rgba(255,255,255,0.4); font-weight: 400;">lessons</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Memory Actions - Compact
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Export", use_container_width=True):
                if memory_manager:
                    export_data = memory_manager.export_memory()
                    st.download_button(
                        "⬇️ Download",
                        data=export_data,
                        file_name="forge_swarm_memory.json",
                        mime="application/json",
                    )
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                if st.session_state.confirm_clear:
                    if memory_manager:
                        memory_manager.clear_memory()
                    st.session_state.confirm_clear = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm")
        
        # Memory Search - Compact
        search_query = st.text_input("Search memory", placeholder="e.g. FastAPI", label_visibility="collapsed")
        if search_query and memory_manager:
            results = memory_manager.search_memory(search_query, n_results=5)
            if results:
                for r in results:
                    dot = "●" if r["score"] >= 8 else "●" if r["score"] >= 6 else "●"
                    color = "#00ff41" if r["score"] >= 8 else "#f0ff00" if r["score"] >= 6 else "#ff00ff"
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 8px; margin-bottom: 4px; border-left: 2px solid {color};">
                        <div style="font-size: 11px; color: #e0e0e0; margin-bottom: 2px;">{r['task'][:40]}...</div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: {color};">Score: {r['score']}/10</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No matches found")
        
        st.markdown("---")
        
        # Templates - Compact Grid
        st.markdown("### TEMPLATES", help="Quick-start task templates")
        TEMPLATES = {
            "⚡ FastAPI CRUD": "templates/fastapi_crud.md",
            "📊 Data Pipeline": "templates/data_pipeline.md",
            "🤖 Discord Bot": "templates/discord_bot.md",
            "🕷️ Web Scraper": "templates/web_scraper.md",
            "🖥️ CLI Tool": "templates/cli_tool.md",
        }
        
        # Display templates in 2-column grid
        template_items = list(TEMPLATES.items())
        for i in range(0, len(template_items), 2):
            cols = st.columns(2)
            for j, (label, path) in enumerate(template_items[i:i+2]):
                with cols[j]:
                    if st.button(label, use_container_width=True):
                        p = Path(path)
                        if p.exists():
                            st.session_state.template_loaded = p.read_text()
                            st.success(f"Loaded: {label}")
                        else:
                            st.error(f"Missing: {path}")

    # ── MAIN AREA ─────────────────────────────────────────────

    # LP2 Hero
    st.markdown("""
    <div style="margin-bottom: 32px;">
        <div class="section-tag">COGNITIVE_PIPELINE</div>
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; font-weight: 700; margin-top: 8px;">FIVE AGENTS.<br><span style="color: #00f3ff;">ONE MISSION.</span></h1>
        <p style="color: rgba(255,255,255,0.6); font-size: 1rem; line-height: 1.6; max-width: 600px;">
            Forge Swarm is a 100% local, privacy-first multi-agent AI platform for autonomous code generation. No cloud. No telemetry. No data leaks.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Agent Pipeline
    AgentStatusDisplay.render_pipeline(current_agent_idx=-1)
    st.markdown("---")

    # Command Prompt Input
    default_text = st.session_state.template_loaded or ""
    
    st.markdown('<div class="glass-panel" style="padding: 20px; margin-bottom: 24px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family: JetBrains Mono, monospace; font-size: 10px; color: #00f3ff; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 12px;">TASK_INPUT</div>', unsafe_allow_html=True)
    
    user_request = st.text_area(
        "**Input Task Request**",
        value=default_text,
        placeholder="e.g. Build a FastAPI REST API for a todo app with SQLite, Pydantic models, and pytest tests",
        height=130,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Context input
    with st.expander("📎 Add context (paste code, errors, or upload a file)"):
        context_code = st.text_area(
            "Existing code or context",
            placeholder="Paste any existing code, error messages, or background context here...",
            height=180,
        )
        uploaded_content = FileUploadHandler.render_upload_ui()
        if uploaded_content:
            context_code = (context_code + "\n\n" + uploaded_content).strip()

    submit = st.button("🚀 Run Forge Swarm", type="primary", use_container_width=True)

    # ── EXECUTION ─────────────────────────────────────────────
    if submit and user_request.strip():
        # Initialize LLM based on provider
        if provider == "ollama":
            llm = LLMProvider(
                provider="ollama",
                model=model,
                base_url=config["llm"]["base_url"],
                temperature=config["llm"]["temperature"],
                num_ctx=config["llm"]["num_ctx"],
            )
        else:  # nvidia_nim
            llm = LLMProvider(
                provider="nvidia_nim",
                model=model,
                base_url="https://integrate.api.nvidia.com/v1",
                temperature=config["nvidia_nim"].get("temperature", config["llm"]["temperature"]),
                num_ctx=config["nvidia_nim"].get("max_tokens", 8192),
                api_key=config["nvidia_nim"].get("api_key", ""),
            )

        factory = AgentFactory(llm=llm, config=config)
        orchestrator = TaskOrchestrator(agents=factory.create_all(), config=config)

        with st.status("⚡ Running Forge Swarm...", expanded=True) as status:
            result = orchestrator.run(user_request, context_code)
            st.session_state.last_result = result

            critic = result.get("critic_result", {})
            score = critic.get("score", 0)

            if memory_manager:
                memory_manager.store_result(
                    task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    task_description=user_request,
                    result=result.get("final_code", ""),
                    quality_score=score,
                    iterations=result.get("iterations", 1),
                )

            st.session_state.run_history.append(
                {
                    "request": user_request[:60] + "...",
                    "score": score,
                    "iterations": result.get("iterations", 1),
                }
            )
            status.update(label="✅ Complete!", state="complete")

    # ── RESULTS ───────────────────────────────────────────────
    if st.session_state.last_result:
        result = st.session_state.last_result
        critic = result.get("critic_result", {})

        AgentStatusDisplay.render_score(
            critic.get("score", 0), critic.get("verdict", "UNKNOWN")
        )
        st.caption(f"Completed in {result.get('iterations', 1)} iteration(s)")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["📄 Final Code", "📋 Agent Log", "🧠 Memory Context", "🧪 Run Code"]
        )

        with tab1:
            st.code(result.get("final_code", ""), language="python")

        with tab2:
            st.text(result.get("agent_log", ""))
            issues = critic.get("issues", [])
            if issues:
                st.markdown("**Issues found by Critic:**")
                for issue in issues:
                    st.markdown(f"- {issue}")

        with tab3:
            memory_manager = st.session_state.memory_manager
            if memory_manager and st.session_state.run_history:
                similar = memory_manager.query_similar(
                    st.session_state.run_history[-1]["request"]
                )
                if similar:
                    for item in similar:
                        with st.expander(f"📚 {item.get('task', 'Past task')[:60]}"):
                            st.text(item.get("result", "")[:400])
                else:
                    st.info("No relevant past lessons found for this task.")
            else:
                st.info("No memory context available.")

        with tab4:
            sandbox = CodeSandbox(config)
            sandbox.render_ui(result.get("final_code", ""))

    else:
        # Empty State
        st.markdown("---")
        st.markdown("""
        <div class="glass-panel" style="padding: 32px; text-align: center; margin-top: 24px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #00f3ff; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 12px;">> SYSTEM_IDLE</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #e0e0e0; margin-bottom: 12px;">Awaiting Input</div>
            <div style="color: rgba(255,255,255,0.4); font-size: 14px; line-height: 1.6; max-width: 500px; margin: 0 auto;">
                Describe a coding task above and click <strong>Run Forge Swarm</strong> to start the multi-agent pipeline.
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
