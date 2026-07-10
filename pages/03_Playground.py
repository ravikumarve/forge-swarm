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
    render_sidebar, MCPToolManager,
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
for key in ["playground_messages", "playground_agent"]:
    if key not in st.session_state:
        if key == "playground_messages":
            st.session_state.playground_messages = []
        elif key == "playground_agent":
            st.session_state.playground_agent = "coder"

# Per-agent custom prompts — prevents prompt bleed when switching agents
for ak in AGENT_KEYS:
    key = f"custom_prompt_{ak}"
    if key not in st.session_state:
        st.session_state[key] = ""

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

    # ── Tool controls (per-agent) ─────────────────────────────────
    st.markdown("---")
    st.markdown("### 🛠️ TOOLS")
    agent_key_sidebar = st.session_state.playground_agent
    if "mcp_manager" not in st.session_state:
        st.session_state.mcp_manager = MCPToolManager(config)
    mcp_mgr = st.session_state.mcp_manager
    avail_tools = mcp_mgr.list_tools()
    # Per-agent enabled tool set
    et_key = f"enabled_tools_{agent_key_sidebar}"
    if et_key not in st.session_state:
        st.session_state[et_key] = []
    if avail_tools:
        selected = []
        for t in avail_tools:
            on = st.checkbox(
                f" {t['name']}",
                value=t["name"] in st.session_state[et_key],
                key=f"t_{agent_key_sidebar}_{t['name']}",
                help=t.get("description", ""),
            )
            if on:
                selected.append(t["name"])
        st.session_state[et_key] = selected
    else:
        st.caption("No tools available")

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

# ── Prompt editor (collapsible, per-agent) ─────────────────────────
with st.expander("📝 Edit agent prompt", expanded=False):
    custom_key = f"custom_prompt_{agent_key}"
    saved = st.session_state.get(custom_key, "")
    default_val = saved or (
        f"You are {agent['role']}.\n\n"
        f"Goal: {agent['goal']}\n\n"
        f"Backstory: {agent['backstory']}\n\n"
        f"Respond as this agent. Be concise, direct, and true to your role."
    )
    edited = st.text_area(
        "System prompt", value=default_val, height=200,
        help="This prompt is sent to the LLM before your message. Edit it to change agent behavior.",
        label_visibility="collapsed",
    )
    st.session_state[custom_key] = edited

    col_r1, col_r2 = st.columns([1, 5])
    with col_r1:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state[custom_key] = ""
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

# ── Recall hint: show last user message as clickable auto-send ─────
last_user_msg = None
for m in reversed(st.session_state.playground_messages):
    if m["role"] == "user":
        last_user_msg = m["content"]
        break

recall_cols = st.columns([10, 1])
with recall_cols[0]:
    show_recall = (
        last_user_msg is not None
        and st.button(
            f"↩ {last_user_msg[:80]}{'…' if last_user_msg and len(last_user_msg) > 80 else ''}",
            key="recall_btn",
            use_container_width=True,
            help="Resend your last message",
        )
    )
with recall_cols[1]:
    if last_user_msg:
        st.markdown(
            '<div style="font-size: 10px; color: rgba(255,255,255,0.15); padding-top: 6px; text-align: center;">'
            '↑ Recall</div>',
            unsafe_allow_html=True,
        )

# ── Chat input (native Enter-to-send, Shift+Enter for newline) ─────
prompt = st.chat_input(f"Message {agent['short']}...", key="playground_chat")

# ── Handle recall auto-send (triggered by recall button click) ─────
if show_recall and last_user_msg:
    prompt = last_user_msg

# ── Handle send with optional tool support ─────────────────────────
if prompt and prompt.strip():
    prompt = prompt.strip()

    st.session_state.playground_messages.append({
        "role": "user",
        "content": prompt,
        "time": datetime.now().strftime("%H:%M:%S"),
    })

    custom_key = f"custom_prompt_{agent_key}"
    system_prompt = st.session_state.get(custom_key, "").strip() or (
        f"You are {agent['role']}.\n\n"
        f"Goal: {agent['goal']}\n\n"
        f"Backstory: {agent['backstory']}\n\n"
        f"Respond as this agent. Be concise, direct, and true to your role."
    )

    # ── Append tool descriptions if tools are enabled for this agent ──
    et_key = f"enabled_tools_{agent_key}"
    enabled_tool_names = st.session_state.get(et_key, [])
    mcp_mgr = st.session_state.get("mcp_manager")
    if enabled_tool_names and mcp_mgr:
        system_prompt += mcp_mgr.format_tools_for_prompt(enabled_tool_names)
        tool_used = True
    else:
        tool_used = False

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

        # ── Multi-round tool loop ─────────────────────────────────────
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        max_tool_rounds = 3 if tool_used else 1
        final_response = ""
        elapsed = 0.0

        for round_i in range(max_tool_rounds):
            with st.spinner(f"{agent['icon']} {agent['short']} is thinking{' (tool round ' + str(round_i + 1) + ')' if round_i > 0 else ''}..."):
                start_t = time.time()
                raw = llm.call(messages)
                round_elapsed = time.time() - start_t
                elapsed += round_elapsed

            # Check for tool call
            tool_call = mcp_mgr.parse_tool_call(raw) if tool_used else None
            if tool_call and tool_call["name"] in enabled_tool_names:
                messages.append({"role": "assistant", "content": raw})
                with st.spinner(f"🔧 Running {tool_call['name']}..."):
                    tool_result = mcp_mgr.call_tool(tool_call["name"], tool_call["args"])
                messages.append({
                    "role": "user",
                    "content": f"Tool '{tool_call['name']}' returned:\n{tool_result}\n\n"
                               f"Please provide your final response based on this result.",
                })
                # Don't set final_response yet — wait for the next round
            else:
                # Clean the raw output: remove any stray TOOL_CALL markers
                import re
                final_response = re.sub(
                    r'<<<TOOL_CALL>>>.*?<<<END_TOOL_CALL>>>',
                    '', raw, flags=re.DOTALL,
                ).strip()
                if not final_response:
                    final_response = raw
                break

        if not final_response:
            final_response = raw if 'raw' in locals() else "(no response)"

        st.session_state.playground_messages.append({
            "role": "assistant",
            "content": final_response,
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
