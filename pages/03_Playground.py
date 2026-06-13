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
    st.markdown("### 🤖 SELECT AGENT")
    agent_cols = st.columns(len(AGENT_KEYS))
    for i, key in enumerate(AGENT_KEYS):
        a = AGENT_DEFS[key]
        active = key == st.session_state.playground_agent
        with agent_cols[i]:
            if st.button(
                a['icon'],
                key=f"agent_sel_{key}",
                use_container_width=True,
                type="primary" if active else "secondary",
                help=f"{a['role']}: {a['goal'][:80]}",
            ):
                if key != st.session_state.playground_agent:
                    st.session_state.playground_agent = key
                    st.rerun()

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
<div style="margin-bottom: 24px;">
    <div class="section-tag">AGENT PLAYGROUND</div>
    <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; margin-top: 8px;">
        🧪 Chat with Individual Agents
    </h1>
    <p style="color: rgba(255,255,255,0.6); font-size: 1rem;">
        Talk to each agent in isolation. Tweak system prompts and test responses without running the full 5-agent pipeline.
    </p>
</div>
""", unsafe_allow_html=True)

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
<div style="margin-bottom: 8px; font-size: 11px; color: rgba(255,255,255,0.3); font-family: 'JetBrains Mono', monospace;">
    Model: {model} · Temp: {temperature} · Max tokens: {max_tokens}
</div>
""", unsafe_allow_html=True)

# ── Chat message display ────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.playground_messages:
        st.markdown("""
        <div style="text-align: center; padding: 48px 0; color: rgba(255,255,255,0.2);">
            <div style="font-size: 28px; margin-bottom: 8px;">💬</div>
            <div style="font-size: 13px;">Type a message below and press <strong>Send</strong> to start.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, msg in enumerate(st.session_state.playground_messages):
            is_user = msg["role"] == "user"

            if is_user:
                # ── User message: right-aligned pill, no border ──
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
                    <div style="background: rgba(0, 243, 255, 0.06); border-radius: 14px 14px 4px 14px;
                                padding: 10px 16px; max-width: 78%; min-width: 80px;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px;
                                    color: #00f3ff; margin-bottom: 4px; letter-spacing: 0.05em;">
                            🧑 You
                        </div>
                        <div style="font-size: 13px; color: #d0d0d0; line-height: 1.5; white-space: pre-wrap;
                                    font-family: 'JetBrains Mono', monospace;">
                            {msg['content']}
                        </div>
                        <div style="font-size: 9px; color: rgba(255,255,255,0.15); margin-top: 4px; text-align: right;">
                            {msg.get('time', '')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # ── Agent message: left accent bar, glass bg, no border ──
                a_icon = msg.get("agent_icon", agent['icon'])
                a_name = msg.get("agent_name", agent['short'])
                a_color = msg.get("agent_color", ac)
                r, g, b = int(a_color[1:3], 16), int(a_color[3:5], 16), int(a_color[5:7], 16)
                msg_id = f"msg_{idx}"

                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 12px;">
                    <div style="border-left: 3px solid {a_color};
                                background: rgba({r}, {g}, {b}, 0.04);
                                border-radius: 4px 14px 14px 4px;
                                padding: 10px 16px; max-width: 78%; min-width: 80px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 9px;
                                        color: {a_color}; letter-spacing: 0.05em;">
                                {a_icon} {a_name}
                            </span>
                            <span style="font-size: 9px; color: rgba(255,255,255,0.15);">
                                {msg.get('time', '')}
                            </span>
                        </div>
                        <div style="font-size: 13px; color: #d0d0d0; line-height: 1.5; white-space: pre-wrap;
                                    font-family: 'JetBrains Mono', monospace;">
                            {msg['content']}
                        </div>
                        <div style="margin-top: 4px; text-align: right;">
                            <button onclick="navigator.clipboard.writeText(document.getElementById('{msg_id}').textContent)"
                                    style="background: none; border: none; color: rgba(255,255,255,0.2);
                                           font-size: 10px; cursor: pointer; padding: 0; font-family: 'JetBrains Mono', monospace;">
                                📋 copy
                            </button>
                        </div>
                    </div>
                </div>
                <div id="{msg_id}" style="display:none;">{msg['content']}</div>
                """, unsafe_allow_html=True)

# ── Input area ──────────────────────────────────────────────────────
st.markdown("---")

# Input row: text area + send + recall
recall_val = st.session_state.get("_recall_prompt", "")
input_text = st.text_area(
    "Message",
    value=recall_val,
    placeholder=f"Message {agent['short']}...",
    label_visibility="collapsed",
    height=70,
    key="playground_input",
)

col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
with col_i1:
    st.markdown(
        '<div style="font-size: 10px; color: rgba(255,255,255,0.2); font-family: JetBrains Mono, monospace; padding-top: 8px;">'
        'Ctrl+Enter or click Send</div>',
        unsafe_allow_html=True,
    )
with col_i2:
    send = st.button("📤 Send", type="primary", use_container_width=True)
with col_i3:
    recall = st.button("↩︎ Recall", use_container_width=True, help="Load your last sent message")

# ── Handle recall ───────────────────────────────────────────────────
if recall:
    for m in reversed(st.session_state.playground_messages):
        if m["role"] == "user":
            st.session_state._recall_prompt = m["content"]
            st.rerun()
            break

# ── Handle send ─────────────────────────────────────────────────────
if send and input_text and input_text.strip():
    prompt = input_text.strip()
    st.session_state._recall_prompt = ""

    st.session_state.playground_messages.append({
        "role": "user",
        "content": prompt,
        "time": datetime.now().strftime("%H:%M:%S"),
    })

    system_prompt = st.session_state.get("custom_prompt", "").strip() or (
        f"You are {agent['role']}.\n\n"
        f"Goal: {agent['goal']}\n\n"
        f"Backstory: {agent['backstory']}\n\n"
        f"Respond as this agent. Be concise, direct, and true to your role."
    )

    try:
        if provider == "nvidia_nim":
            nim_config = config.get("nvidia_nim", {})
            llm = LLMProvider(
                provider="nvidia_nim",
                model=model,
                base_url=nim_config.get("base_url", "https://integrate.api.nvidia.com/v1"),
                temperature=temperature,
                num_ctx=max_tokens,
                api_key=nim_config.get("api_key", ""),
            )
        else:
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
                {"role": "user", "content": prompt},
            ])
            elapsed = time.time() - start_t

        st.session_state.playground_messages.append({
            "role": "assistant",
            "content": response,
            "time": f"{elapsed:.1f}s",
            "agent_icon": agent['icon'],
            "agent_name": agent['short'],
            "agent_color": agent['color'],
        })
    except Exception as e:
        st.session_state.playground_messages.append({
            "role": "assistant",
            "content": f"❌ Error: {str(e)}",
            "time": "",
            "agent_icon": agent['icon'],
            "agent_name": agent['short'],
            "agent_color": agent['color'],
        })

    st.rerun()
