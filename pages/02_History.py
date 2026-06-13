"""
Forge Swarm — History (Page 3)
================================
Browse, search, and re-visit every past code generation run across all projects.
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
    Config, DARK_THEME_CSS, ProjectStore, render_sidebar,
)

st.set_page_config(page_title="History - Forge Swarm", page_icon="📜", layout="wide")
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
config = Config.load()

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar(config)

# ── Main Area ────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 24px;">
    <div class="section-tag">RUN HISTORY</div>
    <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; margin-top: 8px;">
        📜 All Runs
    </h1>
    <p style="color: rgba(255,255,255,0.6); font-size: 1rem;">
        Every code generation run, searchable and filterable.
    </p>
</div>
""", unsafe_allow_html=True)

# Filters row
col1, col2 = st.columns([2, 1])
with col1:
    search_term = st.text_input("🔍 Search runs", placeholder="e.g. FastAPI, score:8", label_visibility="collapsed")
with col2:
    min_score = st.slider("Min score", 0, 10, 0, label_visibility="collapsed")

# Collect all runs across projects
all_projects = ProjectStore.list_projects()
all_runs = []
for proj in all_projects:
    runs = ProjectStore.get_runs(proj["id"])
    for run in runs:
        run["project_name"] = proj["name"]
        run["project_id"] = proj["id"]
    all_runs.extend(runs)

all_runs.sort(key=lambda r: r.get("timestamp", 0), reverse=True)

# Apply filters
filtered = all_runs
if search_term:
    term = search_term.lower()
    filtered = [
        r for r in filtered
        if term in (r.get("summary", "") or "").lower()
        or term in (r.get("project_name", "") or "").lower()
        or term in (r.get("run_id", "") or "").lower()
    ]
if min_score > 0:
    filtered = [r for r in filtered if (r.get("score") or 0) >= min_score]

# Stats bar
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Projects", len(all_projects))
with c2:
    st.metric("Total Runs", len(all_runs))
with c3:
    st.metric("Filtered", len(filtered))
with c4:
    scored = [r for r in all_runs if r.get("score") is not None]
    avg = sum(r["score"] for r in scored) / len(scored) if scored else 0
    st.metric("Avg Score", f"{avg:.1f}/10" if scored else "N/A")

if not filtered:
    st.markdown("""
    <div class="glass-panel" style="padding: 48px; text-align: center; margin-top: 32px;">
        <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 600; color: #e0e0e0; margin-bottom: 8px;">No Runs Found</div>
        <div style="color: rgba(255,255,255,0.4); font-size: 14px;">
            No runs match your filters. Try adjusting the search term or score range.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for run in filtered:
        score = run.get("score")
        score_str = f"{score}/10" if score is not None else "N/A"
        score_color = "#00ff41" if score and score >= 8 else "#f0ff00" if score and score >= 6 else "#ff00ff"
        summary = run.get("summary", "") or ""
        proj_name = run.get("project_name", "Unknown")
        ts = run.get("timestamp", 0)
        try:
            ts_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
        except Exception:
            ts_str = ""

        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 14px; margin-bottom: 10px; border-left: 3px solid {score_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #666;">📁 {proj_name}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #444; margin-left: 12px;">{run['run_id']}</span>
                </div>
                <div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #888;">{ts_str}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: {score_color}; margin-left: 16px; font-weight: 600;">{score_str}</span>
                </div>
            </div>
            <div style="font-size: 13px; color: rgba(255,255,255,0.7); margin-top: 6px; line-height: 1.4;">
                {summary[:250]}{'...' if len(summary) > 250 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 View full output", expanded=False):
            run_dir = ProjectStore.PROJECTS_DIR / run["project_id"] / "runs" / run["run_id"]
            result_path = run_dir / "result.json"
            if result_path.exists():
                try:
                    with open(result_path) as f:
                        result_data = json.load(f)
                    code = result_data.get("final_code", "")
                    if code:
                        st.code(code, language="python")
                    else:
                        st.info("No code output in this run.")
                except Exception:
                    st.error("Could not load run output.")
            else:
                st.info("Run data file not found.")
