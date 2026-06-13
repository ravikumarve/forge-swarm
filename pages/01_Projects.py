"""
Forge Swarm — Projects (Page 2)
=================================
Create, browse, and manage code generation projects with persistent storage.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from datetime import datetime

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy-ollama-only")

import streamlit as st

from forge_swarm_core import (
    Config, DARK_THEME_CSS, ProjectStore, get_memory_manager,
    SystemChecker, AgentStatusDisplay,
)

st.set_page_config(page_title="Projects - Forge Swarm", page_icon="📁", layout="wide")
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

config = Config.load()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
            FORGE_SWARM
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: rgba(255,255,255,0.4); letter-spacing: 0.1em; text-transform: uppercase;">
            v3.0 // Projects
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        checks = SystemChecker.run_all_checks(config)
    st.markdown("### SYS_STATUS")
    status_html = "<div style='display: flex; gap: 8px; margin-bottom: 20px;'>"
    for name, (passed, _) in checks.items():
        icon = "●" if passed else "○"
        color = "#00ff41" if passed else "#ff00ff"
        status_html += f"<span title='{name}' style='color: {color}; font-size: 14px;'>{icon}</span>"
    status_html += "</div>"
    st.markdown(status_html, unsafe_allow_html=True)

    st.markdown("### 📁 NAVIGATION")
    projects = ProjectStore.list_projects()
    st.metric("Total Projects", len(projects))
    total_runs = sum(p.get("run_count", 0) for p in projects)
    st.metric("Total Runs", total_runs)

# ── Main Area ────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 24px;">
    <div class="section-tag">PROJECTS</div>
    <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; margin-top: 8px;">
        📁 Code Generation Projects
    </h1>
    <p style="color: rgba(255,255,255,0.6); font-size: 1rem;">
        Persisted, searchable project history with multi-file output and run tracking.
    </p>
</div>
""", unsafe_allow_html=True)

# ── New Project Button ───────────────────────────────────────────────
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("➕ New Project", type="primary", use_container_width=True):
        st.session_state.show_new_project = True
        st.rerun()

# ── New Project Dialog ───────────────────────────────────────────────
if st.session_state.get("show_new_project"):
    with st.form("new_project_form", clear_on_submit=True):
        st.markdown("### ➕ New Project")
        proj_name = st.text_input("Project name", placeholder="My API Generator")
        proj_desc = st.text_area("Description", placeholder="What does this project build?", height=100)
        c1, c2 = st.columns(2)
        with c1:
            if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                if proj_name.strip():
                    p = ProjectStore.create_project(proj_name.strip(), proj_desc.strip())
                    st.session_state.show_new_project = False
                    st.session_state._selected_project_id = p["id"]
                    st.rerun()
        with c2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_new_project = False
                st.rerun()

# ── Project List ─────────────────────────────────────────────────────
projects = ProjectStore.list_projects()

if not projects:
    st.markdown("""
    <div class="glass-panel" style="padding: 48px; text-align: center; margin-top: 32px;">
        <div style="font-size: 48px; margin-bottom: 16px;">📂</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 600; color: #e0e0e0; margin-bottom: 8px;">No Projects Yet</div>
        <div style="color: rgba(255,255,255,0.4); font-size: 14px;">
            Create a project to start organizing your code generation runs.<br>
            Click <strong>➕ New Project</strong> to begin.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Selected project
    selected_id = st.session_state.get("_selected_project_id")
    if not selected_id or selected_id not in [p["id"] for p in projects]:
        selected_id = projects[0]["id"]

    # Project tabs
    proj_titles = [p["name"][:40] for p in projects]
    proj_ids = [p["id"] for p in projects]
    default_idx = proj_ids.index(selected_id) if selected_id in proj_ids else 0
    tab_labels = [f"📁 {t}" for t in proj_titles]
    selected_tab = st.radio(
        "Projects", options=tab_labels, index=default_idx,
        horizontal=True, label_visibility="collapsed",
    )
    selected_id = proj_ids[tab_labels.index(selected_tab)]
    st.session_state._selected_project_id = selected_id

    # ── Project Detail ───────────────────────────────────────────
    project = ProjectStore.get_project(selected_id)
    if project:
        st.markdown("---")
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"### {project['name']}")
            if project.get("description"):
                st.caption(project["description"])
        with col2:
            st.metric("Runs", project.get("run_count", 0))
        with col3:
            score = project.get("last_score")
            if score is not None:
                st.metric("Last Score", f"{score}/10")
        with col4:
            if st.button("🗑️ Delete", use_container_width=True):
                if st.session_state.get("confirm_delete_project"):
                    ProjectStore.delete_project(selected_id)
                    st.session_state.confirm_delete_project = False
                    st.session_state._selected_project_id = None
                    st.rerun()
                else:
                    st.session_state.confirm_delete_project = True
                    st.warning("Click again to confirm")

        st.caption(f"Created: {project.get('created_at', '')[:10]}  ·  Updated: {project.get('updated_at', '')[:10]}")

        # Runs
        runs = ProjectStore.get_runs(selected_id)
        if runs:
            st.markdown("### 📜 Run History")
            for run in runs:
                score = run.get("score")
                score_str = f"{score}/10" if score is not None else "N/A"
                score_color = "#00ff41" if score and score >= 8 else "#f0ff00" if score and score >= 6 else "#ff00ff"
                summary = run.get("summary", "") or ""
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 12px; margin-bottom: 8px; border-left: 3px solid {score_color};">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #888;">{run['run_id']}</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {score_color};">Score: {score_str}</span>
                    </div>
                    <div style="font-size: 12px; color: rgba(255,255,255,0.6); margin-top: 4px;">
                        {summary[:200]}{'...' if len(summary) > 200 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No runs yet. Go to the Dashboard to run a task with this project selected.")
