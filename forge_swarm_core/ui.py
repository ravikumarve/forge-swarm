"""Forge Swarm — UI Components (Pipeline Graph, File Upload, Theme, Sidebar)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from forge_swarm_core.core import Config, SystemChecker, ProjectStore
from forge_swarm_core.llm import LLMProvider, OllamaEmbeddings, LLMManager
from forge_swarm_core.memory import MemoryManager
from forge_swarm_core.sandbox import CodeSandbox


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

class VisualPipelineGraph:
    """Renders an SVG execution graph showing agent nodes, connections, and live status."""

    AGENTS = [
        ("01", "Planner", "🗺️", "#4fc3f7", "System architecture"),
        ("02", "Researcher", "🔍", "#81c784", "Deep research"),
        ("03", "Coder", "⚙️", "#ffb74d", "Implementation"),
        ("04", "Tester", "🧪", "#ce93d8", "Test suite"),
        ("05", "Critic", "🎯", "#e57373", "Quality gate"),
    ]
    # Data flow connections between agents
    EDGES = [(0, 1), (1, 2), (2, 3), (3, 4)]

    @staticmethod
    def render_pipeline(current_agent_idx: int = -1, iteration: int = 0, score: int = None) -> None:
        """Render an SVG execution graph.

        Args:
            current_agent_idx: -1=idle, 0-4=active agent, 5=complete
            iteration: Current retry iteration number
            score: Final critic score (shown when complete)
        """
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div class="section-tag">COGNITIVE_PIPELINE</div>
        </div>
        """, unsafe_allow_html=True)

        NODE_R = 36
        SPACING = 180
        START_X = 60
        Y = 80
        svg_w = START_X + len(VisualPipelineGraph.AGENTS) * SPACING + 60
        svg_h = 180

        svg_parts = [
            f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg" '
            f'style="display:block;margin:0 auto;max-width:100%;font-family:\'JetBrains Mono\',monospace;">'
            f'<defs>'
            f'  <filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/>'
            f'    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'</defs>'
        ]

        # Draw edges (connection arrows)
        for src_idx, dst_idx in VisualPipelineGraph.EDGES:
            x1 = START_X + src_idx * SPACING + NODE_R
            y1 = Y
            x2 = START_X + dst_idx * SPACING - NODE_R
            y2 = Y

            # Edge is lit if source agent is done or active
            src_done = current_agent_idx > src_idx
            src_active = current_agent_idx == src_idx
            edge_color = "rgba(0, 243, 255, 0.4)" if (src_done or src_active) else "rgba(255,255,255,0.08)"
            edge_width = 2 if (src_done or src_active) else 1

            svg_parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{edge_color}" stroke-width="{edge_width}" '
                f'stroke-dasharray="4,3"/>'
            )
            # Arrow head
            ax = x2 - 6
            svg_parts.append(
                f'<polygon points="{x2},{y2} {ax},{y2-4} {ax},{y2+4}" '
                f'fill="{edge_color}"/>'
            )

        # Draw agent nodes
        for i, (num, name, icon, color, desc) in enumerate(VisualPipelineGraph.AGENTS):
            cx = START_X + i * SPACING
            cy = Y

            if current_agent_idx == -1:
                status = "idle"
                fill = "rgba(255,255,255,0.03)"
                stroke = "rgba(255,255,255,0.1)"
                glow = ""
            elif i < current_agent_idx:
                status = "done"
                fill = "rgba(0,255,65,0.06)"
                stroke = "rgba(0,255,65,0.3)"
                glow = ""
            elif i == current_agent_idx:
                status = "active"
                fill = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)"
                stroke = color
                glow = 'filter="url(#glow)"'
            else:
                status = "idle"
                fill = "rgba(255,255,255,0.03)"
                stroke = "rgba(255,255,255,0.1)"
                glow = ""

            svg_parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{NODE_R}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="2" {glow}/>'
            )
            # Status dot
            dot_y = cy + NODE_R + 8
            dot_colors = {
                "idle": "rgba(255,255,255,0.15)",
                "active": color,
                "done": "#00ff41",
            }
            svg_parts.append(
                f'<circle cx="{cx}" cy="{dot_y}" r="4" fill="{dot_colors[status]}"/>'
            )
            # Agent icon
            svg_parts.append(
                f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-size="22">{icon}</text>'
            )
            # Agent name
            svg_parts.append(
                f'<text x="{cx}" y="{cy+NODE_R+24}" text-anchor="middle" '
                f'fill="{color}" font-size="11" font-weight="600">{name}</text>'
            )
            # Description
            svg_parts.append(
                f'<text x="{cx}" y="{cy+NODE_R+38}" text-anchor="middle" '
                f'fill="rgba(255,255,255,0.3)" font-size="8">{desc}</text>'
            )

        # Iteration counter in top-right
        if iteration > 0:
            svg_parts.append(
                f'<text x="{svg_w-20}" y="24" text-anchor="end" '
                f'fill="rgba(255,255,255,0.3)" font-size="10">ITERATION {iteration}</text>'
            )

        # Score badge on completion
        if score is not None:
            score_color = "#00ff41" if score >= 8 else "#f0ff00" if score >= 6 else "#ff00ff"
            svg_parts.append(
                f'<text x="{svg_w-20}" y="42" text-anchor="end" '
                f'fill="{score_color}" font-size="14" font-weight="700">SCORE {score}/10</text>'
            )

        svg_parts.append('</svg>')
        st.markdown('\n'.join(svg_parts), unsafe_allow_html=True)

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

def get_memory_manager(config):
    """Lazy-init MemoryManager, cached in session state (shared across pages)."""
    if "memory_manager" not in st.session_state:
        try:
            llm_manager = LLMManager(config)
            st.session_state.memory_manager = MemoryManager(
                config, llm_manager.embedder
            )
        except Exception:
            st.session_state.memory_manager = None
    return st.session_state.memory_manager

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

def render_sidebar(config: dict) -> tuple:
    """Render the full sidebar (system status, model config, memory, templates, project selector).

    Returns (provider: str, model: str) — the currently selected provider and model.
    Should be called inside ``with st.sidebar:`` block.
    """
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

    with st.spinner(""):
        checks = SystemChecker.run_all_checks(config)
    st.markdown("### SYS_STATUS", help="System health indicators")
    status_html = "<div style='display: flex; gap: 8px; margin-bottom: 20px;'>"
    for name, (passed, _) in checks.items():
        icon = "●" if passed else "○"
        color = "#00ff41" if passed else "#ff00ff"
        status_html += f"<span title='{name}' style='color: {color}; font-size: 14px;'>{icon}</span>"
    status_html += "</div>"
    st.markdown(status_html, unsafe_allow_html=True)

    st.markdown("### CONFIG", help="AI Model settings")
    llm_config = config["llm"]
    current_provider = llm_config.get("provider", "ollama")
    provider = st.selectbox(
        "Provider",
        options=["ollama", "nvidia_nim"],
        index=0 if current_provider == "ollama" else 1,
        label_visibility="collapsed",
    )
    if provider != current_provider:
        config["llm"]["provider"] = provider
        Config.save(config)
        st.rerun()

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
        nim_model_options = ["Custom..."]
        nim_model_ids = [""]
        for model_data in nim_models_config:
            model_id = model_data.get("id", "")
            model_name = model_data.get("name", model_id)
            nim_model_options.append(model_name)
            nim_model_ids.append(model_id)
        if len(nim_model_options) <= 1:
            nim_model_ids = [
                "",
                "meta/llama-3.1-8b-instruct",
                "meta/llama-3.1-70b-instruct",
                "mistralai/mistral-7b-instruct-v0.3",
            ]
            nim_model_options = ["Custom...", "Llama 3.1 8B", "Llama 3.1 70B", "Mistral 7B"]

        current_model = config["nvidia_nim"]["model"]
        try:
            current_index = nim_model_ids.index(current_model) if current_model else 0
        except ValueError:
            current_index = 0  # Not in list → show "Custom..."
        selected_option = st.selectbox(
            "Model", options=nim_model_options, index=current_index,
            label_visibility="collapsed",
        )
        if selected_option == "Custom...":
            # Saved model isn't in dropdown → show text input
            model = st.text_input(
                "Custom NIM model",
                value=current_model,
                label_visibility="collapsed",
                placeholder="e.g. meta/llama-3.1-8b-instruct",
            )
        else:
            model = nim_model_ids[nim_model_options.index(selected_option)]
        if model:
            config["nvidia_nim"]["model"] = model
        nim_config = config["nvidia_nim"]
        api_key = st.text_input(
            "API Key", value=nim_config.get("api_key", ""),
            type="password", label_visibility="collapsed",
        )
        if api_key and api_key != nim_config.get("api_key", ""):
            config["nvidia_nim"]["api_key"] = api_key
            os.environ["NIM_API_KEY"] = api_key
            Config.save(config)

    st.markdown("---")

    memory_manager = get_memory_manager(config)
    if memory_manager:
        try:
            stats = memory_manager.get_memory_stats()
            count = stats.get("items_stored", 0)
        except Exception:
            count = 0
    else:
        count = 0
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 12px; margin-bottom: 16px;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: rgba(255,255,255,0.4); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px;">VECTOR_MEMORY</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: #00f3ff;">
            {count}
            <span style="font-size: 11px; color: rgba(255,255,255,0.4); font-weight: 400;">lessons</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Export", use_container_width=True):
            if memory_manager:
                export_data = memory_manager.export_memory()
                st.download_button(
                    "⬇️ Download", data=export_data,
                    file_name="forge_swarm_memory.json", mime="application/json",
                )
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            if st.session_state.get("confirm_clear"):
                if memory_manager:
                    memory_manager.clear_memory()
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm")

    search_query = st.text_input("Search memory", placeholder="e.g. FastAPI", label_visibility="collapsed")
    if search_query and memory_manager:
        results = memory_manager.search_memory(search_query, n_results=5)
        if results:
            for r in results:
                dot_color = "#00ff41" if r["score"] >= 8 else "#f0ff00" if r["score"] >= 6 else "#ff00ff"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; padding: 8px; margin-bottom: 4px; border-left: 2px solid {dot_color};">
                    <div style="font-size: 11px; color: #e0e0e0; margin-bottom: 2px;">{r['task'][:40]}...</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: {dot_color};">Score: {r['score']}/10</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No matches found")

    st.markdown("---")

    st.markdown("### TEMPLATES", help="Quick-start task templates")
    TEMPLATES = {
        "⚡ FastAPI CRUD": "templates/fastapi_crud.md",
        "📊 Data Pipeline": "templates/data_pipeline.md",
        "🤖 Discord Bot": "templates/discord_bot.md",
        "🕷️ Web Scraper": "templates/web_scraper.md",
        "🖥️ CLI Tool": "templates/cli_tool.md",
    }
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

    st.markdown("---")
    st.markdown("### 📁 CURRENT PROJECT")
    projects = ProjectStore.list_projects()
    if projects:
        proj_names = [f"{p['name']} ({p.get('run_count', 0)} runs)" for p in projects]
        proj_ids = [p["id"] for p in projects]
        selected_idx = 0
        active_id = st.session_state.get("active_project_id")
        if active_id in proj_ids:
            selected_idx = proj_ids.index(active_id)
        sel = st.selectbox("Active project", options=proj_names, index=selected_idx, label_visibility="collapsed")
        st.session_state.active_project_id = proj_ids[proj_names.index(sel)]

    if st.button("➕ New Project", use_container_width=True):
        st.session_state.show_new_project = True
        st.rerun()

    return provider, model