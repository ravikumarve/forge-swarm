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
    "planner": {
        "icon": "🗺️",
        "role": "Strategic Engineering Lead",
        "goal": "Decompose any coding request into a precise, dependency-ordered execution plan with clear acceptance criteria per subtask.",
        "backstory": (
            "15 years shipping production systems across fintech, healthcare, and SaaS. "
            "Has a pathological hatred of ambiguity. Every plan you write must answer: "
            "What are we building? What does done look like? What can go wrong? "
            "You think in trees — break the root problem into branches, branches into leaves. "
            "Output format: numbered tasks, each with input, output, and acceptance criteria."
        ),
        "color": "#4fc3f7",
    },
    "researcher": {
        "icon": "🔍",
        "role": "Principal Technical Researcher",
        "goal": "Produce a concise, high-signal research brief covering the best implementation patterns, known pitfalls, and idiomatic approaches for the task.",
        "backstory": (
            "Obsessive reader of RFCs, PEPs, source code, and engineering blogs. "
            "Knows when to use a library vs roll your own. Hates cargo-culting. "
            "Every research brief must include: recommended approach, alternatives considered, "
            "top 3 gotchas, and one non-obvious insight the coder would miss."
        ),
        "color": "#81c784",
    },
    "coder": {
        "icon": "⚙️",
        "role": "Senior Software Craftsperson",
        "goal": "Write complete, production-grade, immediately runnable code based on the plan and research brief. No placeholders. No TODOs without tracking. No magic numbers.",
        "backstory": (
            "Treats code like prose. Every function has one job. Every variable name "
            "tells a story. Uses type hints everywhere. Writes comments that explain "
            "WHY, not WHAT. Has strong opinions: explicit > implicit, simple > clever, "
            "boring > exciting. Will refuse to ship code that 'works but is embarrassing.'"
        ),
        "color": "#ffb74d",
    },
    "tester": {
        "icon": "🧪",
        "role": "Adversarial QA Engineer",
        "goal": "Write a complete test suite that tries to break the code before production does.",
        "backstory": (
            "Broke prod 3 times early in career. Now sees failure modes everywhere. "
            "Writes tests in three categories: "
            "1. Happy path — does it work when everything is correct? "
            "2. Sad path — does it fail gracefully when inputs are wrong? "
            "3. Evil path — what happens with None, empty strings, huge numbers, unicode? "
            "Uses pytest. Aims for 80%+ coverage. Names tests like documentation."
        ),
        "color": "#ce93d8",
    },
    "critic": {
        "icon": "🎯",
        "role": "Principal Engineer & Gatekeeper",
        "goal": "Score the complete output (code + tests) on a scale of 1-10 with surgical specificity. Approve if score >= 8. Request targeted revisions if below.",
        "backstory": (
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
        "color": "#e57373",
    },
}

# ── Session state ────────────────────────────────────────────────────
if "playground_messages" not in st.session_state:
    st.session_state.playground_messages = []
if "playground_agent" not in st.session_state:
    st.session_state.playground_agent = "coder"
if "custom_backstory" not in st.session_state:
    st.session_state.custom_backstory = ""
if "custom_goal" not in st.session_state:
    st.session_state.custom_goal = ""

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    provider, model = render_sidebar(config)

    st.markdown("---")
    st.markdown("### 🧪 PLAYGROUND")

    # Temperature slider
    temperature = st.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1,
        help="Lower = more deterministic, Higher = more creative",
    )

    # Max tokens
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
    <p style="color: rgba(255,255,255,0.6); font-size: 1rem;">
        Select an agent, tweak its prompt, and test responses instantly — no full pipeline needed.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Agent selector tabs ─────────────────────────────────────────────
agent_keys = list(AGENT_DEFS.keys())
agent_tabs = st.tabs([f"{AGENT_DEFS[k]['icon']} {AGENT_DEFS[k]['role'].split(' ')[0]}" for k in agent_keys])

for idx, key in enumerate(agent_keys):
    with agent_tabs[idx]:
        if st.button(f"Select {AGENT_DEFS[key]['role']}", key=f"sel_{key}", use_container_width=True):
            st.session_state.playground_agent = key
            st.rerun()

# ── Active agent display ─────────────────────────────────────────────
agent_key = st.session_state.playground_agent
agent = AGENT_DEFS[agent_key]

st.markdown("---")
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown(f"""
    <div style="background: rgba({','.join(str(int(agent['color'][i:i+2], 16)) for i in (1, 3, 5))}, 0.15);
                border: 1px solid {agent['color']}; border-radius: 12px; padding: 20px; text-align: center;">
        <div style="font-size: 48px;">{agent['icon']}</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 600; color: #e0e0e0; margin-top: 8px;">
            {agent['role']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"### {agent['icon']} {agent['role']}")

    # Editable goal
    goal_label = "**Goal**"
    custom_goal = st.session_state.get("custom_goal", "")
    goal_value = custom_goal if custom_goal else agent["goal"]
    edited_goal = st.text_area("Goal", value=goal_value, height=60, label_visibility="collapsed")
    if edited_goal != agent["goal"]:
        st.session_state.custom_goal = edited_goal
    elif st.session_state.get("custom_goal"):
        st.session_state.custom_goal = ""

    # Editable backstory (collapsed by default)
    with st.expander("📝 Edit Backstory / System Prompt", expanded=False):
        backstory_label = "**Backstory**"
        custom_backstory = st.session_state.get("custom_backstory", "")
        bs_value = custom_backstory if custom_backstory else agent["backstory"]
        edited_bs = st.text_area("Backstory", value=bs_value, height=200, label_visibility="collapsed")
        if edited_bs != agent["backstory"]:
            st.session_state.custom_backstory = edited_bs
        elif st.session_state.get("custom_backstory"):
            st.session_state.custom_backstory = ""

        if st.button("🔄 Reset to default", use_container_width=True):
            st.session_state.custom_backstory = ""
            st.session_state.custom_goal = ""
            st.rerun()

# ── Chat interface ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💬 Chat")

# Display message history
for msg in st.session_state.playground_messages:
    is_user = msg["role"] == "user"
    align = "right" if is_user else "left"
    bg = "rgba(0, 243, 255, 0.1)" if is_user else "rgba(255,255,255,0.03)"
    border = "1px solid rgba(0, 243, 255, 0.2)" if is_user else f"1px solid {agent['color']}40"
    st.markdown(f"""
    <div style="display: flex; justify-content: {align}; margin-bottom: 12px;">
        <div style="background: {bg}; border: {border}; border-radius: 12px;
                    padding: 12px 16px; max-width: 80%;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px;
                        color: {'#00f3ff' if is_user else agent['color']}; margin-bottom: 4px;">
                {'🧑 You' if is_user else f'{agent["icon"]} {agent["role"]}'}
            </div>
            <div style="font-size: 14px; color: #e0e0e0; line-height: 1.5; white-space: pre-wrap;">
                {msg['content']}
            </div>
            <div style="font-size: 9px; color: rgba(255,255,255,0.3); margin-top: 4px; text-align: right;">
                {msg.get('time', '')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Input area
prompt = st.chat_input(f"Message {agent['role']}...")
if prompt and prompt.strip():
    # Add user message
    st.session_state.playground_messages.append({
        "role": "user",
        "content": prompt.strip(),
        "time": datetime.now().strftime("%H:%M:%S"),
    })

    # Build system prompt
    goal_text = st.session_state.get("custom_goal", "") or agent["goal"]
    backstory_text = st.session_state.get("custom_backstory", "") or agent["backstory"]
    system_prompt = f"""You are {agent['role']}.

Goal: {goal_text}

Backstory: {backstory_text}

Respond as this agent. Be concise, direct, and true to your role."""

    # Call LLM
    try:
        llm = LLMProvider(
            provider=provider,
            model=model,
            base_url=config["llm"]["base_url"],
            temperature=temperature,
            num_ctx=max_tokens,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt.strip()},
        ]

        with st.spinner(f"{agent['icon']} {agent['role']} is thinking..."):
            start_time = time.time()
            response = llm.call(messages)
            elapsed = time.time() - start_time

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
