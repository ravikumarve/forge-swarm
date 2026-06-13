"""
Forge Swarm — Agent Playground (Page 4)
=========================================
Chat with individual agents in isolation. Tweak prompts, test responses,
and debug agent behavior without running the full 5-agent pipeline.
"""

from __future__ import annotations

import os
import time
from datetime import datetime

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy-ollama-only")

import streamlit as st

from forge_swarm_core import (
    Config, DARK_THEME_CSS, LLMProvider, SystemChecker,
    render_sidebar,
)

st.set_page_config(page_title="Playground - Forge Swarm", page_icon="🧪", layout="wide")
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
config = Config.load()

# ── Agent definitions ────────────────────────────────────────────────
AGENT_DEFS = {
    "planner":   {"icon": "🗺️", "short": "Planner",   "role": "Strategic Engineering Lead",
                  "color": "#4fc3f7",
                  "goal": "Decompose any coding request into a precise, dependency-ordered execution plan with clear acceptance criteria per subtask.",
                  "backstory": "15 years shipping production systems across fintech, healthcare, and SaaS. Has a pathological hatred of ambiguity. Every plan you write must answer: What are we building? What does done look like? What can go wrong? You think in trees — break the root problem into branches, branches into leaves. Output format: numbered tasks, each with input, output, and acceptance criteria."},
    "researcher":{"icon": "🔍", "short": "Researcher","role": "Principal Technical Researcher",
                  "color": "#81c784",
                  "goal": "Produce a concise, high-signal research brief covering the best implementation patterns, known pitfalls, and idiomatic approaches for the task.",
                  "backstory": "Obsessive reader of RFCs, PEPs, source code, and engineering blogs. Knows when to use a library vs roll your own. Hates cargo-culting. Every research brief must include: recommended approach, alternatives considered, top 3 gotchas, and one non-obvious insight the coder would miss."},
    "coder":     {"icon": "⚙️", "short": "Coder",     "role": "Senior Software Craftsperson",
                  "color": "#ffb74d",
                  "goal": "Write complete, production-grade, immediately runnable code based on the plan and research brief. No placeholders. No TODOs without tracking. No magic numbers.",
                  "backstory": "Treats code like prose. Every function has one job. Every variable name tells a story. Uses type hints everywhere. Writes comments that explain WHY, not WHAT. Has strong opinions: explicit > implicit, simple > clever, boring > exciting. Will refuse to ship code that 'works but is embarrassing.'"},
    "tester":    {"icon": "🧪", "short": "Tester",    "role": "Adversarial QA Engineer",
                  "color": "#ce93d8",
                  "goal": "Write a complete test suite that tries to break the code before production does.",
                  "backstory": "Broke prod 3 times early in career. Now sees failure modes everywhere. Writes tests in three categories: 1. Happy path — does it work when everything is correct? 2. Sad path — does it fail gracefully when inputs are wrong? 3. Evil path — what happens with None, empty strings, huge numbers, unicode? Uses pytest. Aims for 80%+ coverage. Names tests like documentation."},
    "critic":    {"icon": "🎯", "short": "Critic",    "role": "Principal Engineer & Gatekeeper",
                  "color": "#e57373",
                  "goal": "Score the complete output (code + tests) on a scale of 1-10 with surgical specificity. Approve if score >= 8. Request targeted revisions if below.",
                  "backstory": "Zero tolerance for mediocrity. Has reviewed 10,000+ PRs. Scores on: - Correctness (does it actually work?) - Readability (can a junior follow it?) - Robustness (does it handle edge cases?) - Idiomatic style (is it Pythonic?) - Test coverage (are the tests meaningful?) Output format MUST be: SCORE: X/10  VERDICT: APPROVED / REVISION REQUIRED  ISSUES: [bulleted list]  REQUIRED CHANGES: [if REVISION REQUIRED]"},
}

AGENT_KEYS = list(AGENT_DEFS.keys())

# ── Session state ────────────────────────────────────────────────────
for key in ["playground_messages", "playground_agent", "custom_prompt"]:
    if key not in st.session_state:
        if key == "playground_messages":
            st.session_state.playground_messages = []
        elif key == "playground_agent":
            st.session_state.playground_agent = "coder"
        elif key == "custom_prompt":
            st.session_state.custom_prompt = ""

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    provider, model = render_sidebar(config)

    st.markdown("---")
    st.markdown("### 🧪 PLAYGROUND")

    temperature = st.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1,
        help="Lower = more deterministic, Higher = more creative",
    )
    max_tokens = st.slider(
        "Max tokens", min_value=128, max_value=8192, value=2048, step=128,
    )

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.playground_messages = []
        st.rerun()

# ── Main Area ────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 16px;">
    <div class="section-tag">AGENT PLAYGROUND</div>
    <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; margin-top: 8px;">
        🧪 Chat with Individual Agents
    </h1>
</div>
""", unsafe_allow_html=True)

# ── Agent selector: compact clickable cards ──────────────────────────
current = st.session_state.playground_agent
cols = st.columns(len(AGENT_KEYS))
for i, key in enumerate(AGENT_KEYS):
    a = AGENT_DEFS[key]
    active = key == current
    border_color = a["color"] if active else "rgba(255,255,255,0.08)"
    bg = f"rgba({int(a['color'][1:3], 16)}, {int(a['color'][3:5], 16)}, {int(a['color'][5:7], 16)}, 0.12)" if active else "rgba(255,255,255,0.02)"
    with cols[i]:
        st.markdown(f"""
        <div style="background: {bg}; border: 1px solid {border_color}; border-radius: 8px;
                    padding: 10px 4px; text-align: center; cursor: pointer;
                    {'box-shadow: 0 0 12px ' + a['color'] + '40;' if active else ''}
                    transition: all 0.2s;">
            <div style="font-size: 22px;">{a['icon']}</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: {'700' if active else '400'};
                        color: {'#e0e0e0' if active else 'rgba(255,255,255,0.5)'}; margin-top: 4px;">
                {a['short']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Column-button to select
        if st.button("▸", key=f"sel_{key}", help=f"Select {a['role']}"):
            if key != current:
                st.session_state.playground_agent = key
                st.rerun()

# ── Active agent bar (compact) ──────────────────────────────────────
agent_key = st.session_state.playground_agent
agent = AGENT_DEFS[agent_key]
ac = agent["color"]

st.markdown(f"""
<div style="background: rgba({int(ac[1:3], 16)}, {int(ac[3:5], 16)}, {int(ac[5:7], 16)}, 0.06);
            border: 1px solid {ac}30; border-radius: 6px; padding: 12px 16px; margin: 16px 0;">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 28px;">{agent['icon']}</span>
        <div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 600; color: #e0e0e0;">
                {agent['role']}
            </div>
            <div style="font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 2px;">
                {agent['goal'][:120]}{'…' if len(agent['goal']) > 120 else ''}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Prompt editor (collapsible) ─────────────────────────────────────
with st.expander("📝 Edit agent prompt", expanded=False):
    default_prompt = st.session_state.get("custom_prompt", "") or (
        f"You are {agent['role']}.\n\n"
        f"Goal: {agent['goal']}\n\n"
        f"Backstory: {agent['backstory']}\n\n"
        f"Respond as this agent. Be concise, direct, and true to your role."
    )
    edited = st.text_area(
        "System prompt", value=default_prompt, height=200,
        help="This prompt is sent to the LLM before your message. Edit it to change agent behavior.",
        label_visibility="collapsed",
    )
    st.session_state.custom_prompt = edited

    col_r1, col_r2 = st.columns([1, 5])
    with col_r1:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.custom_prompt = ""
            st.rerun()

# ── Chat interface ──────────────────────────────────────────────────
st.markdown("### 💬 Chat")
st.markdown(f"""
<div style="margin-bottom: 8px; font-size: 12px; color: rgba(255,255,255,0.4);">
    Model: {model} · Temp: {temperature} · Max tokens: {max_tokens}
</div>
""", unsafe_allow_html=True)

# Chat message container with fixed max height + scroll
chat_container = st.container()

# Display message history inside scrollable container
with chat_container:
    if not st.session_state.playground_messages:
        st.markdown("""
        <div style="text-align: center; padding: 40px 0; color: rgba(255,255,255,0.3);">
            <div style="font-size: 32px; margin-bottom: 8px;">💬</div>
            <div style="font-size: 13px;">Send a message to start chatting with the agent.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.playground_messages:
            is_user = msg["role"] == "user"
            justify = "flex-end" if is_user else "flex-start"
            bubble_bg = "rgba(0, 243, 255, 0.08)" if is_user else f"rgba({int(ac[1:3], 16)}, {int(ac[3:5], 16)}, {int(ac[5:7], 16)}, 0.08)"
            bubble_border = "1px solid rgba(0, 243, 255, 0.2)" if is_user else f"1px solid {ac}30"
            label_color = "#00f3ff" if is_user else ac
            label_text = "🧑 You" if is_user else f"{agent['icon']} {agent['short']}"

            st.markdown(f"""
            <div style="display: flex; justify-content: {justify}; margin-bottom: 10px;">
                <div style="background: {bubble_bg}; border: {bubble_border}; border-radius: 10px;
                            padding: 10px 14px; max-width: 78%; min-width: 120px;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px;
                                color: {label_color}; margin-bottom: 3px; letter-spacing: 0.05em;">
                        {label_text}
                    </div>
                    <div style="font-size: 13px; color: #d0d0d0; line-height: 1.5; white-space: pre-wrap;
                                font-family: 'JetBrains Mono', monospace;">
                        {msg['content']}
                    </div>
                    <div style="font-size: 9px; color: rgba(255,255,255,0.2); margin-top: 4px; text-align: right;">
                        {msg.get('time', '')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Input
prompt = st.chat_input(f"Message {agent['short']}...")
if prompt and prompt.strip():
    st.session_state.playground_messages.append({
        "role": "user",
        "content": prompt.strip(),
        "time": datetime.now().strftime("%H:%M:%S"),
    })

    system_prompt = st.session_state.get("custom_prompt", "").strip() or (
        f"You are {agent['role']}.\n\n"
        f"Goal: {agent['goal']}\n\n"
        f"Backstory: {agent['backstory']}\n\n"
        f"Respond as this agent. Be concise, direct, and true to your role."
    )

    try:
        llm = LLMProvider(
            provider=provider,
            model=model,
            base_url=config["llm"]["base_url"],
            temperature=temperature,
            num_ctx=max_tokens,
        )

        with st.spinner(f"{agent['icon']} {agent['short']} is thinking..."):
            start_t = time.time()
            response = llm.call([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt.strip()},
            ])
            elapsed = time.time() - start_t

        st.session_state.playground_messages.append({
            "role": "assistant",
            "content": response,
            "time": f"{elapsed:.1f}s",
        })
    except Exception as e:
        st.session_state.playground_messages.append({
            "role": "assistant",
            "content": f"❌ Error: {str(e)}",
            "time": "",
        })

    st.rerun()
