"""
Forge Swarm - Dashboard (Page 1)
==================================
Multi-agent AI code generation dashboard.
Imports shared classes from forge_swarm_core.
"""

from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime

# Disable telemetry BEFORE any heavy imports
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy-ollama-only")

import streamlit as st

# ── Import shared core ──────────────────────────────────────────────
from forge_swarm_core import (
    # Core
    Config, LLMProvider, LLMManager, MemoryManager,
    SystemChecker, AgentFactory, TaskOrchestrator, CriticParser,
    CodeSandbox, FileUploadHandler, AgentStatusDisplay,
    OllamaEmbeddings,
    # UI helpers
    DARK_THEME_CSS, setup_wizard, get_memory_manager,
    # Projects
    ProjectStore,
)

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
if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = None

# ── SIDEBAR (Command Deck) ──────────────────────────────────────────
with st.sidebar:
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

    # Model / Provider
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
            "Model", options=nim_model_options, index=current_index,
            label_visibility="collapsed",
        )
        model = nim_model_ids[nim_model_options.index(selected_option)]
        config["nvidia_nim"]["model"] = model
        nim_config = config["nvidia_nim"]
        api_key = st.text_input(
            "API Key", value=nim_config.get("api_key", ""),
            type="password", label_visibility="collapsed",
        )
        if api_key:
            config["nvidia_nim"]["api_key"] = api_key
            os.environ["NIM_API_KEY"] = api_key

    st.markdown("---")

    # Memory - Compact Card
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
            if st.session_state.confirm_clear:
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

    # Templates
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
        if st.session_state.active_project_id in proj_ids:
            selected_idx = proj_ids.index(st.session_state.active_project_id)
        sel = st.selectbox("Active project", options=proj_names, index=selected_idx, label_visibility="collapsed")
        st.session_state.active_project_id = proj_ids[proj_names.index(sel)]

    if st.button("➕ New Project", use_container_width=True):
        st.session_state.show_new_project = True
        st.rerun()

# ── New Project Dialog ──────────────────────────────────────────────
if st.session_state.get("show_new_project"):
    with st.form("new_project_form"):
        st.markdown("### ➕ New Project")
        proj_name = st.text_input("Project name", placeholder="My API Generator")
        proj_desc = st.text_area("Description", placeholder="What does this project do?", height=80)
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                if proj_name.strip():
                    p = ProjectStore.create_project(proj_name.strip(), proj_desc.strip())
                    st.session_state.active_project_id = p["id"]
                    st.session_state.show_new_project = False
                    st.rerun()
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_new_project = False
                st.rerun()

# ── MAIN AREA ───────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 32px;">
    <div class="section-tag">COGNITIVE_PIPELINE</div>
    <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; font-weight: 700; margin-top: 8px;">
        FIVE AGENTS.<br><span style="color: #00f3ff;">ONE MISSION.</span>
    </h1>
    <p style="color: rgba(255,255,255,0.6); font-size: 1rem; line-height: 1.6; max-width: 600px;">
        Forge Swarm is a 100% local, privacy-first multi-agent AI platform for autonomous code generation.
    </p>
</div>
""", unsafe_allow_html=True)

AgentStatusDisplay.render_pipeline(current_agent_idx=-1)
st.markdown("---")

# Task input
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

# ── EXECUTION ───────────────────────────────────────────────────────
memory_manager = get_memory_manager(config)

if submit and user_request.strip():
    if provider == "ollama":
        llm = LLMProvider(
            provider="ollama",
            model=model,
            base_url=config["llm"]["base_url"],
            temperature=config["llm"]["temperature"],
            num_ctx=config["llm"]["num_ctx"],
        )
    else:
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

        st.session_state.run_history.append({
            "request": user_request[:60] + "...",
            "score": score,
            "iterations": result.get("iterations", 1),
        })

        # Auto-save to active project if one is selected
        active_id = st.session_state.active_project_id
        if active_id:
            ProjectStore.save_run(active_id, result)
            ProjectStore.update_project(active_id, {"description": user_request[:200]})

        status.update(label="✅ Complete!", state="complete")

# ── RESULTS ─────────────────────────────────────────────────────────
if st.session_state.last_result:
    result = st.session_state.last_result
    critic = result.get("critic_result", {})

    AgentStatusDisplay.render_score(critic.get("score", 0), critic.get("verdict", "UNKNOWN"))
    st.caption(f"Completed in {result.get('iterations', 1)} iteration(s)")

    files = result.get("files", {})
    file_list = result.get("file_list", [])

    tab_labels = ["📄 Final Code", "📋 Agent Log", "🧠 Memory Context", "🧪 Run Code"]
    if file_list:
        tab_labels.insert(0, "📁 Project Files")

    tabs = st.tabs(tab_labels)
    tab_idx = 0

    # Project Files tab (only when multi-file output exists)
    if file_list:
        with tabs[tab_idx]:
            tab_idx += 1
            st.markdown(f"**{len(file_list)} files** generated")
            st.markdown("---")
            for fname in file_list:
                content = files.get(fname, "")
                lang = "python" if fname.endswith(".py") else \
                       "markdown" if fname.endswith((".md", ".rst")) else \
                       "yaml" if fname.endswith((".yaml", ".yml")) else \
                       "json" if fname.endswith(".json") else \
                       "text"
                with st.expander(f"📄 {fname}", expanded=True):
                    st.code(content, language=lang)

            # Download as zip
            if st.button("📦 Download All as ZIP", type="primary"):
                import io, zipfile
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for fname, content in files.items():
                        zf.writestr(fname, content)
                st.download_button(
                    "⬇️ Download ZIP",
                    data=buf.getvalue(),
                    file_name="forge_swarm_output.zip",
                    mime="application/zip",
                )
        tab_idx = 1

    with tabs[tab_idx]:
        tab_idx += 1
        st.code(result.get("final_code", ""), language="python")

    with tabs[tab_idx]:
        tab_idx += 1
        st.text(result.get("agent_log", ""))
        issues = critic.get("issues", [])
        if issues:
            st.markdown("**Issues found by Critic:**")
            for issue in issues:
                st.markdown(f"- {issue}")

    with tabs[tab_idx]:
        tab_idx += 1
        if memory_manager and st.session_state.run_history:
            similar = memory_manager.query_similar(st.session_state.run_history[-1]["request"])
            if similar:
                for item in similar:
                    with st.expander(f"📚 {item.get('task', 'Past task')[:60]}"):
                        st.text(item.get("result", "")[:400])
            else:
                st.info("No relevant past lessons found for this task.")
        else:
            st.info("No memory context available.")

    with tabs[tab_idx]:
        tab_idx += 1
        sandbox = CodeSandbox(config)
        sandbox.render_ui(result.get("final_code", ""))

else:
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
