"""Forge Swarm — LLM Provider & Embeddings."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import streamlit as st

from forge_swarm_core._lazy import _litellm, _ollama


class LLMProvider:
    """Generic LLM provider supporting Ollama and NVIDIA NIM.

    ⚡ Lazy-imports litellm on first call — does NOT load at module level.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        base_url: str = "",
        temperature: float = 0.7,
        num_ctx: int = 8192,
        api_key: str = "",
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self._num_ctx = num_ctx
        self.temperature = temperature
        self._api_base = base_url

        if provider == "ollama":
            self._litellm_model = f"ollama/{model}"
            self._api_base = base_url or "http://localhost:11434"
        elif provider == "nvidia_nim":
            self._litellm_model = f"nvidia_nim/{model}"
            self._api_base = base_url or "https://integrate.api.nvidia.com/v1"
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def call(self, messages: list[dict], **kwargs) -> str:
        """Call the LLM via litellm (lazy-imported on first call)."""
        _litellm_module = _litellm()

        # Set API key for NVIDIA NIM
        if self.provider == "nvidia_nim" and self.api_key:
            _litellm_module.api_key = self.api_key

        # Extract CrewAI-specific kwargs
        kwargs.pop("tools", None)
        kwargs.pop("callbacks", None)
        kwargs.pop("available_functions", None)
        kwargs.pop("from_task", None)
        kwargs.pop("from_agent", None)
        kwargs.pop("response_model", None)

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

        response = _litellm_module.completion(**completion_params)
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
        # ⚡ Lazy-import ollama on first embedding call
        self._client = None

    @property
    def client(self):
        """Initialize ollama client lazily on first access."""
        if self._client is None:
            _ollama_module = _ollama()
            self._client = _ollama_module.Client(host=self.base_url)
        return self._client

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text."""
        response = self.client.embeddings(model=self.model, prompt=text)
        return response["embedding"]

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