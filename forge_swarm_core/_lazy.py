"""Forge Swarm — Lazy Import Helpers.

Heavy libraries (crewai, chromadb, litellm, ollama) are imported only when
first needed, not at module load time. This keeps startup fast (~1.5s).
"""

from __future__ import annotations

import os

import streamlit as st


@st.cache_resource
def _crewai():
    """Lazy-load crewai classes. Cached for the lifetime of the app."""
    from crewai import Agent as _Agent, Task as _Task, Crew as _Crew, Process as _Process
    return _Agent, _Task, _Crew, _Process


@st.cache_resource
def _crewai_tools():
    """Lazy-load crewai_tools (optional — graceful fallback)."""
    try:
        from crewai_tools import SerperDevTool as _SerperDevTool
        return _SerperDevTool, True
    except ImportError:
        return None, False


@st.cache_resource
def _chromadb():
    """Lazy-load chromadb."""
    import chromadb as _chromadb
    from chromadb.config import Settings as _Settings
    return _chromadb, _Settings


def _ollama():
    """Lazy-load ollama client."""
    import ollama as _ollama
    return _ollama


def _litellm():
    """Lazy-load litellm."""
    import litellm as _litellm
    return _litellm
