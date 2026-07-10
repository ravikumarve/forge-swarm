"""Forge Swarm — Core Infrastructure (Config, SystemChecker, ProjectStore)."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
import yaml


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

class SystemChecker:
    """Check system dependencies and health"""

    @staticmethod
    @st.cache_data(ttl=60)
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
    @st.cache_data(ttl=60)
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
    @st.cache_data(ttl=60)
    def check_chromadb(persist_dir: str) -> tuple[bool, str]:
        """Check if ChromaDB can be initialized at path."""
        try:
            db_path = Path(persist_dir)
            db_path.mkdir(parents=True, exist_ok=True)

            _chroma_module, _Settings = _chromadb()
            test_client = _chroma_module.PersistentClient(
                path=str(db_path), settings=_Settings(anonymized_telemetry=False)
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
    @st.cache_data(ttl=60)
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

class ProjectStore:
    """Persist code generation projects to local JSON files."""

    PROJECTS_DIR = Path("projects")

    @classmethod
    def ensure_dir(cls):
        cls.PROJECTS_DIR.mkdir(exist_ok=True)

    @classmethod
    def list_projects(cls) -> List[Dict[str, Any]]:
        """Return all projects sorted by updated_at DESC."""
        cls.ensure_dir()
        projects = []
        for d in cls.PROJECTS_DIR.iterdir():
            if d.is_dir():
                meta_path = d / "metadata.json"
                if meta_path.exists():
                    try:
                        with open(meta_path) as f:
                            meta = json.load(f)
                        projects.append(meta)
                    except Exception:
                        pass
        projects.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
        return projects

    @classmethod
    def get_project(cls, project_id: str) -> Optional[Dict[str, Any]]:
        """Load a single project by ID."""
        meta_path = cls.PROJECTS_DIR / project_id / "metadata.json"
        if not meta_path.exists():
            return None
        try:
            with open(meta_path) as f:
                return json.load(f)
        except Exception:
            return None

    @classmethod
    def create_project(cls, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new project, return its metadata."""
        cls.ensure_dir()
        project_id = datetime.now().strftime("proj_%Y%m%d_%H%M%S")
        now = datetime.now().isoformat()
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": now,
            "updated_at": now,
            "run_count": 0,
            "last_score": None,
            "model_used": None,
        }
        (cls.PROJECTS_DIR / project_id).mkdir(exist_ok=True)
        with open(cls.PROJECTS_DIR / project_id / "metadata.json", "w") as f:
            json.dump(project, f, indent=2)
        return project

    @classmethod
    def update_project(cls, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update project metadata fields."""
        project = cls.get_project(project_id)
        if not project:
            return False
        project.update(updates)
        project["updated_at"] = datetime.now().isoformat()
        with open(cls.PROJECTS_DIR / project_id / "metadata.json", "w") as f:
            json.dump(project, f, indent=2)
        return True

    @classmethod
    def delete_project(cls, project_id: str) -> bool:
        """Delete a project and all its files."""
        import shutil
        path = cls.PROJECTS_DIR / project_id
        if path.exists():
            shutil.rmtree(path)
            return True
        return False

    @classmethod
    def save_run(cls, project_id: str, result: Dict[str, Any]) -> bool:
        """Save a pipeline run result into the project directory."""
        run_id = datetime.now().strftime("run_%Y%m%d_%H%M%S")
        run_dir = cls.PROJECTS_DIR / project_id / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save run metadata
        with open(run_dir / "result.json", "w") as f:
            json.dump(result, f, indent=2, default=str)

        # Extract and save files separately for multi-file projects
        files = result.get("files", {})
        if not files:
            # Single blob output — save as main code file
            code = result.get("final_code", "")
            if code:
                files = {"output.py": code}

        for filename, content in files.items():
            file_path = run_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)

        # Update project metadata
        project = cls.get_project(project_id)
        if project:
            cls.update_project(project_id, {
                "run_count": project.get("run_count", 0) + 1,
                "last_score": result.get("critic_result", {}).get("score"),
                "last_run_id": run_id,
            })

        return True

    @classmethod
    def get_runs(cls, project_id: str) -> List[Dict[str, str]]:
        """Return list of run summaries for a project."""
        runs_dir = cls.PROJECTS_DIR / project_id / "runs"
        if not runs_dir.exists():
            return []
        runs = []
        for d in sorted(runs_dir.iterdir(), reverse=True):
            result_path = d / "result.json"
            if result_path.exists():
                try:
                    with open(result_path) as f:
                        result = json.load(f)
                    runs.append({
                        "run_id": d.name,
                        "timestamp": d.stat().st_mtime,
                        "score": result.get("critic_result", {}).get("score"),
                        "iterations": result.get("iterations"),
                        "summary": (result.get("final_code", "") or "")[:120],
                    })
                except Exception:
                    pass
        return runs