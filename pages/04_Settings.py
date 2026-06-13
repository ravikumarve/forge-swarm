"""
Forge Swarm — Settings (Page 5)
================================
In-app config.yaml editor for Forge Swarm settings.
Supports LLM, Embeddings, Memory, and Agents configuration sections.
"""

from __future__ import annotations

import os

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy-ollama-only")

import streamlit as st

from forge_swarm_core import Config, DARK_THEME_CSS, render_sidebar

st.set_page_config(page_title="Settings - Forge Swarm", page_icon="⚙️", layout="wide")
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

config = Config.load()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar(config)

# ── Page Header ──────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 24px;">
    <div class="section-tag">SETTINGS</div>
    <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; margin-top: 8px;">
        ⚙️ Configuration Editor
    </h1>
    <p style="color: rgba(255,255,255,0.6); font-size: 1rem;">
        Edit <code>config.yaml</code> settings directly from the UI. All changes are saved immediately on submit.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Settings Form ────────────────────────────────────────────────────
with st.form("settings_form", clear_on_submit=False):

    # ── LLM Section ────────────────────────────────────────────────
    st.markdown("### 🤖 LLM Configuration")
    st.caption("Language model provider and generation parameters")

    llm = config.get("llm", {})
    col1, col2 = st.columns(2)
    with col1:
        provider = st.selectbox(
            "Provider",
            options=["ollama", "nvidia_nim"],
            index=0 if llm.get("provider", "ollama") == "ollama" else 1,
            help="LLM backend provider — Ollama (local) or NVIDIA NIM (cloud)",
        )
        model = st.text_input(
            "Model",
            value=llm.get("model", "llama3.1:8b"),
            help="Model name (e.g. llama3.1:8b, phi3:mini, deepseek-v4-flash)",
        )
        base_url = st.text_input(
            "Base URL",
            value=llm.get("base_url", "http://localhost:11434"),
            help="API endpoint for the LLM provider",
        )
    with col2:
        temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=2.0, step=0.1,
            value=float(llm.get("temperature", 0.7)),
            help="Higher = more creative output, lower = more deterministic",
        )
        num_ctx = st.number_input(
            "Context Size (num_ctx)",
            min_value=1024, max_value=131072, step=1024,
            value=int(llm.get("num_ctx", 8192)),
            help="Maximum context window in tokens",
        )
        timeout = st.number_input(
            "Timeout (seconds)",
            min_value=10, max_value=600, step=10,
            value=int(llm.get("timeout", 120)),
            help="LLM request timeout in seconds",
        )

    st.markdown("---")

    # ── Embeddings Section ──────────────────────────────────────────
    st.markdown("### 📊 Embeddings Configuration")
    st.caption("Vector embedding model for memory search and similarity")

    emb = config.get("embeddings", {})
    col1, col2 = st.columns(2)
    with col1:
        emb_model = st.text_input(
            "Embedding Model",
            value=emb.get("model", "nomic-embed-text"),
            help="Ollama embedding model name (e.g. nomic-embed-text, all-minilm)",
        )
    with col2:
        emb_base_url = st.text_input(
            "Embeddings Base URL",
            value=emb.get("base_url", "http://localhost:11434"),
            help="Ollama API endpoint for embedding generation",
        )

    st.markdown("---")

    # ── Memory Section ──────────────────────────────────────────────
    st.markdown("### 🧠 Memory Configuration")
    st.caption("ChromaDB vector store settings for persistent lesson memory")

    mem = config.get("memory", {})
    col1, col2 = st.columns(2)
    with col1:
        db_path = st.text_input(
            "DB Path",
            value=mem.get("db_path", "./forge_swarm_memory"),
            help="Directory path for ChromaDB persistence",
        )
        collection_name = st.text_input(
            "Collection Name",
            value=mem.get("collection_name", "improvement_lessons"),
            help="ChromaDB collection used for storing lessons",
        )
    with col2:
        max_lessons = st.number_input(
            "Max Lessons",
            min_value=10, max_value=10000, step=10,
            value=int(mem.get("max_lessons", 200)),
            help="Maximum number of stored lessons before oldest are pruned",
        )
        min_score_to_store = st.slider(
            "Min Score to Store",
            min_value=0, max_value=10, step=1,
            value=int(mem.get("min_score_to_store", 7)),
            help="Minimum critic quality score required to persist a lesson",
        )

    st.markdown("---")

    # ── Agents Section ──────────────────────────────────────────────
    st.markdown("### 🤖 Agents Configuration")
    st.caption("Multi-agent pipeline behavior and quality control")

    agents = config.get("agents", {})
    col1, col2 = st.columns(2)
    with col1:
        max_iterations = st.number_input(
            "Max Iterations",
            min_value=1, max_value=20, step=1,
            value=int(agents.get("max_iterations", 5)),
            help="Maximum retry iterations for quality improvement loop",
        )
        quality_threshold = st.slider(
            "Quality Threshold",
            min_value=0, max_value=10, step=1,
            value=int(agents.get("quality_threshold", 8)),
            help="Minimum critic score to auto-approve pipeline output",
        )
    with col2:
        retry_on_below = st.checkbox(
            "Retry on Below Threshold",
            value=bool(agents.get("retry_on_below_threshold", True)),
            help="Automatically retry pipeline when critic score is below threshold",
        )
        verbose = st.checkbox(
            "Verbose Agent Output",
            value=bool(agents.get("verbose", True)),
            help="Show detailed agent reasoning and logging in output",
        )

    st.markdown("---")

    # ── NVIDIA NIM Section ─────────────────────────────────────────
    with st.expander("🔷 NVIDIA NIM Configuration", expanded=False):
        st.caption("Cloud LLM provider settings. Only used when LLM Provider is set to `nvidia_nim`.")
        nim = config.get("nvidia_nim", {})
        col1, col2 = st.columns(2)
        with col1:
            nim_api_key = st.text_input(
                "NIM API Key",
                value=nim.get("api_key", ""),
                type="password",
                help="NVIDIA NIM API key. Can also be set via NIM_API_KEY environment variable.",
            )
            nim_model = st.text_input(
                "NIM Model",
                value=nim.get("model", "meta/llama-3.1-8b-instruct"),
                help="NVIDIA NIM model ID (e.g. meta/llama-3.1-8b-instruct, deepseek-v4-flash)",
            )
        with col2:
            nim_base_url = st.text_input(
                "NIM Base URL",
                value=nim.get("base_url", "https://integrate.api.nvidia.com/v1"),
                help="NVIDIA NIM API endpoint",
            )
            nim_temperature = st.slider(
                "NIM Temperature",
                min_value=0.0, max_value=2.0, step=0.1,
                value=float(nim.get("temperature", 0.7)),
                help="Temperature for NVIDIA NIM model",
            )
            nim_max_tokens = st.number_input(
                "NIM Max Tokens",
                min_value=256, max_value=131072, step=1024,
                value=int(nim.get("max_tokens", 8192)),
                help="Maximum tokens for NVIDIA NIM model",
            )

    st.markdown("---")

    # ── Form Buttons ────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        submitted = st.form_submit_button("💾 Save", type="primary", use_container_width=True)
    with col2:
        reset = st.form_submit_button("🔄 Reset", use_container_width=True)

# ── Handle Save ──────────────────────────────────────────────────────
if submitted:
    try:
        # Update LLM config
        config["llm"]["provider"] = provider
        config["llm"]["model"] = model.strip()
        config["llm"]["base_url"] = base_url.strip()
        config["llm"]["temperature"] = float(temperature)
        config["llm"]["num_ctx"] = int(num_ctx)
        config["llm"]["timeout"] = int(timeout)

        # Update Embeddings config
        config["embeddings"]["model"] = emb_model.strip()
        config["embeddings"]["base_url"] = emb_base_url.strip()

        # Update Memory config
        config["memory"]["db_path"] = db_path.strip()
        config["memory"]["collection_name"] = collection_name.strip()
        config["memory"]["max_lessons"] = int(max_lessons)
        config["memory"]["min_score_to_store"] = int(min_score_to_store)

        # Update Agents config
        config["agents"]["max_iterations"] = int(max_iterations)
        config["agents"]["quality_threshold"] = int(quality_threshold)
        config["agents"]["retry_on_below_threshold"] = bool(retry_on_below)
        config["agents"]["verbose"] = bool(verbose)

        # Update NVIDIA NIM config
        if "nvidia_nim" not in config:
            config["nvidia_nim"] = {}
        config["nvidia_nim"]["api_key"] = nim_api_key.strip()
        config["nvidia_nim"]["model"] = nim_model.strip()
        config["nvidia_nim"]["base_url"] = nim_base_url.strip()
        config["nvidia_nim"]["temperature"] = float(nim_temperature)
        config["nvidia_nim"]["max_tokens"] = int(nim_max_tokens)
        if nim_api_key.strip():
            os.environ["NIM_API_KEY"] = nim_api_key.strip()

        if Config.save(config):
            st.toast("✅ Settings saved to config.yaml!", icon="💾")
            st.success("✅ **Settings saved to `config.yaml`**")
        else:
            st.error("❌ Failed to save settings. Check file permissions.")
    except Exception as e:
        st.error(f"❌ Error saving settings: {e}")

# ── Handle Reset ─────────────────────────────────────────────────────
if reset:
    try:
        defaults = Config.DEFAULT_CONFIG

        # Reset to factory defaults for editable sections
        config["llm"] = defaults.get("llm", {}).copy()
        config["embeddings"] = defaults.get("embeddings", {}).copy()
        config["memory"] = defaults.get("memory", {}).copy()
        config["agents"] = defaults.get("agents", {}).copy()
        config["nvidia_nim"] = {
            "model": "meta/llama-3.1-8b-instruct",
            "base_url": "https://integrate.api.nvidia.com/v1",
            "api_key": "",
            "temperature": 0.7,
            "max_tokens": 8192,
        }

        # Ensure min_score_to_store exists (it's in config.yaml but not DEFAULT_CONFIG)
        config["memory"]["min_score_to_store"] = 7

        if Config.save(config):
            st.toast("🔄 Settings reset to defaults!", icon="🔄")
            st.rerun()
        else:
            st.error("❌ Failed to reset settings.")
    except Exception as e:
        st.error(f"❌ Error resetting settings: {e}")
