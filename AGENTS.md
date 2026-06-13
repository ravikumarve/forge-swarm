# AGENTS.md — Forge Swarm
> **OpenCode Agent Execution Spec** | Version 3.0 | Full Upgrade Build
> Upgrade tracks: Agent Intelligence · UI/UX · Memory System · New Features

---

## 💾 Session Memory Ledger (For context7 MCP)

### [2025-04-22 03:25] - Gumroad-Ready Sprint Completion
- **State**: Success
- **MCP Data Used**: None (local file operations only)
- **Agents Deployed**: @orchestrator (main execution), @docs (README enhancement), @git-ops (LICENSE and GitHub setup)
- **Architectural Decision**: No architectural changes - focused on documentation, installation scripts, and Gumroad preparation
- **Next Turn Directive**: Ready for public launch. Repository is Gumroad-ready with all documentation, installation scripts, and GitHub templates in place.
- **Commits Created**: 7 commits covering README enhancement, LICENSE, install scripts, GitHub templates, test updates, and Gumroad product description
- **Files Created**: LICENSE, install.sh, install.ps1, CONTRIBUTING.md, CODE_OF_CONDUCT.md, gumroad_product_description.md, .github/ISSUE_TEMPLATE/*, docs/*
- **Test Results**: All 28 installation checks passed - FORGE SWARM v3.0 GUMROAD READY

### [2026-06-13 14:30] - Tier 1 + Tier 2 Sprint (Part 1)
- **State**: Success
- **MCP Data Used**: None (local file operations only)
- **Agents Deployed**: @orchestrator (main execution)
- **Architectural Decision**:
  - Extracted forge_swarm_core.py with all shared classes
  - Multi-page app via Streamlit pages/ directory
  - ProjectStore persists to projects/ as JSON files
  - Sidebar extracted into shared render_sidebar() function
  - Lazy imports for crewai, chromadb, ollama, litellm (17s → 1.5s startup)
- **Next Turn Directive**: Implement Settings Editor page (in-app config.yaml editor)
- **Files Changed/Created**:
  - forge_swarm_core.py (core module)
  - Home.py (dashboard, was forge_swarm_with_ui.py)
  - pages/01_Projects.py (project CRUD)
  - pages/02_History.py (run history browser)
  - pages/03_Playground.py (agent chat)
- **Pending Tasks**: Settings Editor (Tier 2, item 6) — in-app config editor

---

## 🧠 AGENT MISSION BRIEFING

You are an autonomous coding agent executing a **full upgrade** of an existing Forge Swarm codebase. The base v1.0 is already built and working. Your job is to upgrade it across 4 tracks simultaneously without breaking existing functionality.

**Rules:**
- Read this entire file before touching any code
- Do not break existing working features
- Run `python -m py_compile Home.py` after every major change
- Commit-worthy state after each phase — no half-broken files

---

## 📌 UPGRADE SUMMARY

| Track | What Changes | Priority |
|---|---|---|
| **Track A** | Agent Intelligence — smarter prompts, structured scoring, retry logic | HIGH |
| **Track B** | UI/UX — dark theme, real-time agent status, better layout | HIGH |
| **Track C** | Memory System — export, search, lesson browser UI | MEDIUM |
| **Track D** | New Features — code sandbox, file upload, 5 templates | HIGH |

---

## 🏗️ UPDATED PROJECT STRUCTURE

```
forge-swarm/
├── Home.py     ← Main app (heavily modified)
├── config.yaml                ← Updated with new config keys
├── requirements.txt           ← Add: pygments, RestrictedPython
├── test_installation.py       ← Updated smoke tests
├── .env.example               ← No change
├── .gitignore                 ← No change
├── templates/                 ← NEW: task templates
│   ├── fastapi_crud.md
│   ├── data_pipeline.md
│   ├── discord_bot.md
│   ├── web_scraper.md
│   └── cli_tool.md
├── forge_swarm_memory/        ← Auto-created ChromaDB storage
└── README.md                  ← No change
```

---

## ⚙️ UPDATED config.yaml

Replace existing `config.yaml` with this expanded version:

```yaml
llm:
  model: "llama3.1:8b"
  base_url: "http://localhost:11434"
  temperature: 0.7
  num_ctx: 8192
  timeout: 120

embeddings:
  model: "nomic-embed-text"
  base_url: "http://localhost:11434"

memory:
  db_path: "./forge_swarm_memory"
  collection_name: "improvement_lessons"
  max_lessons: 200
  min_score_to_store: 7
  max_context_results: 5

agents:
  max_iterations: 5
  verbose: true
  allow_delegation: false
  quality_threshold: 8
  retry_on_below_threshold: true

sandbox:
  enabled: true
  timeout_seconds: 10
  max_output_lines: 100
  allowed_imports:
    - os.path
    - json
    - math
    - datetime
    - collections
    - itertools
    - re
    - string
    - typing

ui:
  page_title: "⚡ Forge Swarm"
  page_icon: "⚡"
  layout: "wide"
  theme: "dark"
  show_agent_avatars: true
  animate_progress: true
```

---

## 📦 UPDATED requirements.txt

```
streamlit>=1.32.0
crewai==0.28.8
crewai-tools>=0.1.0
langchain-ollama>=0.1.0
langchain-community>=0.2.0
chromadb>=0.4.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
requests>=2.31.0
pygments>=2.17.0
RestrictedPython>=7.0
```

---

## 🤖 TRACK A — AGENT INTELLIGENCE UPGRADES

### A1: Rewrite All 5 Agent Backstories

Replace existing agent backstories with these upgraded versions:

**Planner (upgraded):**
```
Role: Strategic Engineering Lead
Goal: Decompose any coding request into a precise, dependency-ordered execution plan
      with clear acceptance criteria per subtask.
Backstory: 15 years shipping production systems across fintech, healthcare, and SaaS.
           Has a pathological hatred of ambiguity. Every plan you write must answer:
           What are we building? What does done look like? What can go wrong?
           You think in trees — break the root problem into branches, branches into leaves.
           Output format: numbered tasks, each with input, output, and acceptance criteria.
```

**Researcher (upgraded):**
```
Role: Principal Technical Researcher
Goal: Produce a concise, high-signal research brief covering the best implementation
      patterns, known pitfalls, and idiomatic approaches for the task.
Backstory: Obsessive reader of RFCs, PEPs, source code, and engineering blogs.
           Knows when to use a library vs roll your own. Hates cargo-culting.
           Every research brief must include: recommended approach, alternatives considered,
           top 3 gotchas, and one non-obvious insight the coder would miss.
```

**Coder (upgraded):**
```
Role: Senior Software Craftsperson
Goal: Write complete, production-grade, immediately runnable code based on the plan
      and research brief. No placeholders. No TODOs without tracking. No magic numbers.
Backstory: Treats code like prose. Every function has one job. Every variable name
           tells a story. Uses type hints everywhere. Writes comments that explain
           WHY, not WHAT. Has strong opinions: explicit > implicit, simple > clever,
           boring > exciting. Will refuse to ship code that "works but is embarrassing."
```

**Tester (upgraded):**
```
Role: Adversarial QA Engineer
Goal: Write a complete test suite that tries to break the code before production does.
Backstory: Broke prod 3 times early in career. Now sees failure modes everywhere.
           Writes tests in three categories:
           1. Happy path — does it work when everything is correct?
           2. Sad path — does it fail gracefully when inputs are wrong?
           3. Evil path — what happens with None, empty strings, huge numbers, unicode?
           Uses pytest. Aims for 80%+ coverage. Names tests like documentation.
```

**Critic (upgraded):**
```
Role: Principal Engineer & Gatekeeper
Goal: Score the complete output (code + tests) on a scale of 1-10 with surgical
      specificity. Approve if score >= 8. Request targeted revisions if below.
Backstory: Zero tolerance for mediocrity. Has reviewed 10,000+ PRs. Scores on:
           - Correctness (does it actually work?)
           - Readability (can a junior follow it?)
           - Robustness (does it handle edge cases?)
           - Idiomatic style (is it Pythonic?)
           - Test coverage (are the tests meaningful?)
           Output format MUST be:
           SCORE: X/10
           VERDICT: APPROVED / REVISION REQUIRED
           ISSUES: [bulleted list of specific line-level issues]
           REQUIRED CHANGES: [only if REVISION REQUIRED]
```

### A2: Add CriticParser Class

Add this class to `Home.py`:

```python
class CriticParser:
    """Parses structured Critic agent output into typed fields."""

    @staticmethod
    def parse(critic_output: str) -> Dict[str, Any]:
        """
        Extract score, verdict, issues, and required changes from critic output.

        Returns:
            Dict with keys: score (int), verdict (str), issues (List[str]),
            required_changes (List[str]), approved (bool)
        """
        result = {
            "score": 0,
            "verdict": "UNKNOWN",
            "issues": [],
            "required_changes": [],
            "approved": False,
        }

        lines = critic_output.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    score_str = line.replace("SCORE:", "").strip()
                    result["score"] = int(score_str.split("/")[0])
                except (ValueError, IndexError):
                    result["score"] = 0
            elif line.startswith("VERDICT:"):
                result["verdict"] = line.replace("VERDICT:", "").strip()
                result["approved"] = "APPROVED" in result["verdict"].upper()
            elif line.startswith("ISSUES:"):
                current_section = "issues"
            elif line.startswith("REQUIRED CHANGES:"):
                current_section = "required_changes"
            elif line.startswith("- ") and current_section:
                result[current_section].append(line[2:])

        return result
```

### A3: Upgrade TaskOrchestrator with Retry Loop

Replace the existing `run()` method in `TaskOrchestrator` with:

```python
def run(self, user_request: str, context: str = "") -> Dict[str, Any]:
    """
    Execute the crew with retry loop based on Critic score.

    Returns:
        Dict with keys: final_code (str), critic_result (dict),
        iterations (int), agent_log (str)
    """
    quality_threshold = self.config["agents"]["quality_threshold"]
    max_iterations = self.config["agents"]["max_iterations"]
    retry = self.config["agents"]["retry_on_below_threshold"]

    iteration = 0
    last_result = None
    agent_log = []

    while iteration < max_iterations:
        iteration += 1
        agent_log.append(f"🔄 Iteration {iteration}/{max_iterations}")

        tasks = self.build_tasks(user_request, context)
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff()
        critic_data = CriticParser.parse(str(result))
        agent_log.append(f"📊 Critic score: {critic_data['score']}/10")

        last_result = {
            "final_code": str(result),
            "critic_result": critic_data,
            "iterations": iteration,
            "agent_log": "\n".join(agent_log),
        }

        if critic_data["approved"] or critic_data["score"] >= quality_threshold:
            agent_log.append(f"✅ Approved at iteration {iteration}")
            break

        if not retry:
            break

        context += f"\n\nPrevious attempt issues:\n" + "\n".join(
            critic_data["required_changes"]
        )
        agent_log.append("⚠️ Below threshold. Retrying with critic feedback.")

    return last_result
```

---

## 🎨 TRACK B — UI/UX UPGRADES

### B1: Dark Theme CSS

Add this constant at the top of `Home.py` after imports:

```python
DARK_THEME_CSS = """
<style>
    .stApp { background-color: #0d0d0d; color: #e0e0e0; }
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #222222;
    }
    [data-testid="stExpander"] {
        background-color: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333333 !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff4b4b, #ff6b35) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(255, 75, 75, 0.4) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111111;
        border-bottom: 1px solid #222222;
    }
    .stTabs [data-baseweb="tab"] { color: #888888; font-weight: 500; }
    .stTabs [aria-selected="true"] {
        color: #ff4b4b !important;
        border-bottom: 2px solid #ff4b4b !important;
    }
    .stCodeBlock {
        background-color: #0a0a0a !important;
        border: 1px solid #1e1e1e !important;
        border-radius: 8px !important;
    }
    .agent-card {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 4px 0;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .agent-card.active { border-color: #ff4b4b; box-shadow: 0 0 12px rgba(255,75,75,0.2); }
    .agent-card.done { border-color: #4caf50; opacity: 0.7; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #111111; }
    ::-webkit-scrollbar-thumb { background: #333333; border-radius: 3px; }
</style>
"""
```

### B2: AgentStatusDisplay Class

```python
class AgentStatusDisplay:
    """Renders real-time agent pipeline status in Streamlit."""

    AGENTS = [
        ("🗺️", "Planner", "Breaking down your request..."),
        ("🔍", "Researcher", "Gathering patterns and context..."),
        ("⚙️", "Coder", "Writing implementation..."),
        ("🧪", "Tester", "Writing test suite..."),
        ("🎯", "Critic", "Scoring output quality..."),
    ]

    @staticmethod
    def render_pipeline(current_agent_idx: int = -1) -> None:
        """
        Render all 5 agents as status cards.
        current_agent_idx: 0-4 = active, -1 = idle, 5 = complete
        """
        st.markdown("### 🤖 Agent Pipeline")
        cols = st.columns(5)
        for i, (icon, name, desc) in enumerate(AgentStatusDisplay.AGENTS):
            with cols[i]:
                if current_agent_idx == -1:
                    status, card_class = "⚪", ""
                elif i < current_agent_idx:
                    status, card_class = "✅", "done"
                elif i == current_agent_idx:
                    status, card_class = "🔄", "active"
                else:
                    status, card_class = "⏳", ""
                st.markdown(
                    f'<div class="agent-card {card_class}">'
                    f'{status} <strong>{icon} {name}</strong><br/>'
                    f'<small style="color:#666">{desc}</small></div>',
                    unsafe_allow_html=True,
                )

    @staticmethod
    def render_score(score: int, verdict: str) -> None:
        """Render critic score badge."""
        color = "#4caf50" if score >= 8 else "#ff9800" if score >= 6 else "#ff4b4b"
        st.markdown(
            f'<div style="margin:8px 0">'
            f'<span style="background:{color};color:white;border-radius:20px;'
            f'padding:4px 14px;font-weight:700;font-size:1rem">'
            f'Score: {score}/10</span>&nbsp;&nbsp;'
            f'<span style="color:{color};font-weight:600">{verdict}</span></div>',
            unsafe_allow_html=True,
        )
```

### B3: Rewrite main() with New Layout

Full `main()` function structure — implement exactly:

```python
def main() -> None:
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

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚡ Forge Swarm")
        st.caption("Local multi-agent code generation")
        st.markdown("---")

        # System status
        st.markdown("### 🖥️ System Status")
        checks = SystemChecker.run_all_checks(config)
        for name, passed in checks.items():
            st.markdown(f"{'✅' if passed else '❌'} **{name}**")

        st.markdown("---")

        # Model selector
        st.markdown("### ⚙️ Model")
        model = st.text_input("Ollama model", value=config["llm"]["model"])

        st.markdown("---")

        # Memory stats + controls
        st.markdown("### 🧠 Memory")
        memory_manager = MemoryManager(config)
        stats = memory_manager.get_memory_stats()
        st.metric("Lessons stored", stats.get("count", 0))
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Export", use_container_width=True):
                export_data = memory_manager.export_memory()
                st.download_button(
                    "⬇️ Download",
                    data=export_data,
                    file_name="forge_swarm_memory.json",
                    mime="application/json",
                )
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                if st.session_state.confirm_clear:
                    memory_manager.clear_memory()
                    st.success("Cleared")
                    st.session_state.confirm_clear = False
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again")

        # Memory browser
        st.markdown("---")
        st.markdown("### 🔍 Search Memory")
        search_query = st.text_input("Search lessons", placeholder="e.g. FastAPI")
        if search_query:
            results = memory_manager.search_memory(search_query, n_results=5)
            if results:
                for r in results:
                    dot = "🟢" if r["score"] >= 8 else "🟡" if r["score"] >= 6 else "🔴"
                    with st.expander(f"{dot} {r['task'][:35]}..."):
                        st.caption(f"Score: {r['score']}/10 · {r['stored_at'][:10]}")
                        st.text(r["result"][:250] + "...")
            else:
                st.caption("No matching lessons.")

        st.markdown("---")

        # Templates
        st.markdown("### 📋 Templates")
        TEMPLATES = {
            "⚡ FastAPI CRUD": "templates/fastapi_crud.md",
            "📊 Data Pipeline": "templates/data_pipeline.md",
            "🤖 Discord Bot": "templates/discord_bot.md",
            "🕷️ Web Scraper": "templates/web_scraper.md",
            "🖥️ CLI Tool": "templates/cli_tool.md",
        }
        for label, path in TEMPLATES.items():
            if st.button(label, use_container_width=True):
                p = Path(path)
                if p.exists():
                    st.session_state.template_loaded = p.read_text()
                    st.success(f"Loaded: {label}")
                else:
                    st.error(f"Missing: {path}")

    # ── MAIN AREA ─────────────────────────────────────────────
    st.markdown("# ⚡ Forge Swarm")
    st.markdown("*Local multi-agent code generation. Five agents. Zero cloud.*")
    st.markdown("---")

    AgentStatusDisplay.render_pipeline(current_agent_idx=-1)
    st.markdown("---")

    # Task input
    default_text = st.session_state.template_loaded or ""
    user_request = st.text_area(
        "**Describe what you want to build**",
        value=default_text,
        placeholder="e.g. Build a FastAPI REST API for a todo app with SQLite, Pydantic models, and pytest tests",
        height=130,
    )

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

    # ── EXECUTION ─────────────────────────────────────────────
    if submit and user_request.strip():
        llm = ChatOllama(
            model=model,
            base_url=config["llm"]["base_url"],
            temperature=config["llm"]["temperature"],
        )
        factory = AgentFactory(llm=llm, config=config)
        orchestrator = TaskOrchestrator(agents=factory.create_all(), config=config)

        with st.status("⚡ Running Forge Swarm...", expanded=True) as status:
            result = orchestrator.run(user_request, context_code)
            st.session_state.last_result = result

            score = result["critic_result"]["score"]
            memory_manager.store_result(
                task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                task_description=user_request,
                result=result["final_code"],
                quality_score=score,
                iterations=result["iterations"],
            )

            st.session_state.run_history.append({
                "request": user_request[:60] + "...",
                "score": score,
                "iterations": result["iterations"],
            })
            status.update(label="✅ Complete!", state="complete")

    # ── RESULTS ───────────────────────────────────────────────
    if st.session_state.last_result:
        result = st.session_state.last_result
        critic = result["critic_result"]

        AgentStatusDisplay.render_score(critic["score"], critic["verdict"])
        st.caption(f"Completed in {result['iterations']} iteration(s)")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["📄 Final Code", "📋 Agent Log", "🧠 Memory Context", "🧪 Run Code"]
        )

        with tab1:
            st.code(result["final_code"], language="python")

        with tab2:
            st.text(result["agent_log"])
            if critic["issues"]:
                st.markdown("**Issues found by Critic:**")
                for issue in critic["issues"]:
                    st.markdown(f"- {issue}")

        with tab3:
            similar = memory_manager.query_similar(
                st.session_state.run_history[-1]["request"] if st.session_state.run_history else ""
            )
            if similar:
                for item in similar:
                    with st.expander(f"📚 {item.get('task', 'Past task')[:60]}"):
                        st.text(item.get("result", "")[:400])
            else:
                st.info("No relevant past lessons found for this task.")

        with tab4:
            sandbox = CodeSandbox(config)
            sandbox.render_ui(result["final_code"])


if __name__ == "__main__":
    main()
```

---

## 🧠 TRACK C — MEMORY SYSTEM UPGRADES

### C1: Add export_memory() to MemoryManager

```python
def export_memory(self) -> str:
    """Export all stored lessons as JSON string for download."""
    try:
        results = self.collection.get(include=["documents", "metadatas"])
        export = {
            "exported_at": datetime.now().isoformat(),
            "collection": self.collection.name,
            "count": len(results["documents"]),
            "lessons": [
                {"document": doc, "metadata": meta}
                for doc, meta in zip(results["documents"], results["metadatas"])
            ],
        }
        return json.dumps(export, indent=2)
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return json.dumps({"error": str(e)})
```

### C2: Add search_memory() to MemoryManager

```python
def search_memory(self, query: str, n_results: int = 10) -> List[Dict]:
    """Search memory with text query, return ranked results."""
    try:
        count = self.collection.count()
        if count == 0:
            return []
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, count),
            include=["documents", "metadatas", "distances"],
        )
        return [
            {
                "task": meta.get("task_description", "Unknown"),
                "result": doc,
                "score": meta.get("quality_score", 0),
                "distance": round(dist, 4),
                "stored_at": meta.get("stored_at", "Unknown"),
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]
    except Exception as e:
        print(f"❌ Memory search failed: {e}")
        return []
```

### C3: Update store_result() with Score Threshold + Rich Metadata

```python
def store_result(
    self,
    task_id: str,
    task_description: str,
    result: str,
    quality_score: int = 0,
    iterations: int = 1,
) -> None:
    """Store a completed task result — only if score meets threshold."""
    min_score = self.config["memory"].get("min_score_to_store", 7)
    if quality_score < min_score:
        print(f"⚠️ Score {quality_score} below threshold {min_score}. Skipping storage.")
        return
    try:
        self.collection.add(
            documents=[result],
            metadatas=[{
                "task_id": task_id,
                "task_description": task_description[:500],
                "quality_score": quality_score,
                "iterations": iterations,
                "stored_at": datetime.now().isoformat(),
            }],
            ids=[task_id],
        )
        print(f"💾 Stored lesson (score: {quality_score}/10)")
    except Exception as e:
        print(f"❌ Failed to store result: {e}")
```

---

## 🚀 TRACK D — NEW FEATURES

### D1: CodeSandbox Class

```python
class CodeSandbox:
    """Safe, restricted Python code execution using RestrictedPython."""

    def __init__(self, config: Dict[str, Any]):
        self.timeout = config["sandbox"]["timeout_seconds"]
        self.max_lines = config["sandbox"]["max_output_lines"]
        self.enabled = config["sandbox"]["enabled"]

    def execute(self, code: str) -> Dict[str, Any]:
        """Execute a Python code snippet safely."""
        if not self.enabled:
            return {"output": "", "error": "Sandbox disabled in config", "success": False, "truncated": False}

        import io
        import contextlib
        from RestrictedPython import compile_restricted, safe_globals

        result = {"output": "", "error": None, "success": False, "truncated": False}
        try:
            byte_code = compile_restricted(code, "<sandbox>", "exec")
            output_buffer = io.StringIO()
            restricted_globals = {**safe_globals, "_print_": print}
            with contextlib.redirect_stdout(output_buffer):
                exec(byte_code, restricted_globals)  # noqa: S102
            lines = output_buffer.getvalue().split("\n")
            if len(lines) > self.max_lines:
                lines = lines[:self.max_lines]
                result["truncated"] = True
            result["output"] = "\n".join(lines)
            result["success"] = True
        except SyntaxError as e:
            result["error"] = f"Syntax error: {e}"
        except Exception as e:
            result["error"] = f"Runtime error: {type(e).__name__}: {e}"
        return result

    def render_ui(self, code: str) -> None:
        """Render sandbox execution UI in Streamlit."""
        st.markdown("### 🧪 Code Sandbox")
        st.caption("⚠️ Restricted execution — safe imports only. No filesystem or network access.")
        editable = st.text_area("Edit before running", value=code, height=300, key="sandbox_code")
        if st.button("▶️ Run Code", type="primary"):
            with st.spinner("Executing..."):
                result = self.execute(editable)
            if result["success"]:
                st.success("✅ Execution successful")
                if result["output"]:
                    st.code(result["output"], language="text")
                    if result["truncated"]:
                        st.warning(f"Output truncated to {self.max_lines} lines")
                else:
                    st.info("No output produced")
            else:
                st.error(f"❌ {result['error']}")
```

### D2: FileUploadHandler Class

```python
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
            st.error(f"❌ File too large ({size_kb:.0f}KB). Max {FileUploadHandler.MAX_FILE_SIZE_KB}KB.")
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
```

### D3: Create 5 Template Files

Create `templates/` directory and these files:

**templates/fastapi_crud.md:**
```
Build a production-ready FastAPI REST API with:
- SQLite database via SQLAlchemy ORM (async)
- Pydantic v2 models for request/response validation
- Full CRUD: Create, Read, Update, Delete endpoints
- pytest test suite with httpx TestClient
- Proper HTTP status codes and error responses
- Health check at GET /health
- OpenAPI docs auto-generated at /docs

Entity: Todo with fields: id, title, description, completed, created_at
```

**templates/data_pipeline.md:**
```
Build a data processing pipeline that:
- Reads CSV files with pandas
- Validates schema, handles missing/null values
- Computes statistics: mean, median, std, percentiles, outliers
- Exports cleaned data as JSON
- Generates a plain-text summary report
- Handles all errors with informative messages
- Includes pytest tests for each transformation step
```

**templates/discord_bot.md:**
```
Build a Discord bot with discord.py that includes:
- Slash commands: /hello, /help, /ping, /roll (dice roller)
- Error handling for all commands
- DISCORD_TOKEN loaded from environment variable
- Structured logging with timestamps
- Graceful shutdown on KeyboardInterrupt
- pytest tests using mock Discord objects
```

**templates/web_scraper.md:**
```
Build an async web scraper with:
- httpx for async HTTP requests
- BeautifulSoup4 for HTML parsing
- Configurable rate limiting (delay between requests)
- Retry logic with exponential backoff
- Robots.txt compliance check
- CSV export of scraped data
- pytest tests with mocked HTTP responses
- Handles timeouts, 404s, and redirects gracefully
```

**templates/cli_tool.md:**
```
Build a CLI tool using Typer with:
- Subcommands: init, run, status, config
- YAML configuration file support (~/.toolname/config.yaml)
- Rich library for formatted terminal output (tables, progress bars)
- Logging with -v / -vv verbosity flags
- User-friendly error messages (no raw tracebacks)
- Shell completion support (typer install-completion)
- pytest tests for all subcommands
```

---

## 🧪 UPDATED test_installation.py

Replace existing file entirely:

```python
"""Forge Swarm v2.0 — Installation Verification"""

import sys
from pathlib import Path

PASS, FAIL = [], []


def check(name: str, fn) -> bool:
    try:
        fn()
        print(f"  ✅ {name}")
        PASS.append(name)
        return True
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        FAIL.append(name)
        return False


print("\n⚡ Forge Swarm — Installation Check\n" + "─" * 42)

print("\n📦 Core Dependencies")
check("streamlit", lambda: __import__("streamlit"))
check("crewai", lambda: __import__("crewai"))
check("langchain_ollama", lambda: __import__("langchain_ollama"))
check("chromadb", lambda: __import__("chromadb"))
check("pydantic", lambda: __import__("pydantic"))
check("yaml", lambda: __import__("yaml"))
check("requests", lambda: __import__("requests"))

print("\n📦 New Dependencies")
check("pygments", lambda: __import__("pygments"))
check("RestrictedPython", lambda: __import__("RestrictedPython"))

print("\n⚙️  Configuration")
check("config.yaml exists", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("config.yaml").exists() else None)
check("config.yaml valid", lambda: __import__("yaml").safe_load(open("config.yaml")))

print("\n📋 Templates")
for t in ["fastapi_crud", "data_pipeline", "discord_bot", "web_scraper", "cli_tool"]:
    check(f"templates/{t}.md", lambda t=t: (_ for _ in ()).throw(FileNotFoundError()) if not Path(f"templates/{t}.md").exists() else None)

print("\n🌐 Connectivity")
import requests
check("Ollama reachable", lambda: requests.get("http://localhost:11434/api/tags", timeout=5).raise_for_status())

print("\n💾 ChromaDB")
def _chroma():
    import chromadb
    chromadb.PersistentClient(path="./forge_swarm_memory_test").get_or_create_collection("test")
check("ChromaDB init", _chroma)

print("\n🚀 Application")
check("main file exists", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("Home.py").exists() else None)
check("main file compiles", lambda: __import__("py_compile").compile("Home.py"))

print("\n" + "═" * 42)
if not FAIL:
    print(f"  ⚡ ALL {len(PASS)} CHECKS PASSED — FORGE SWARM v2.0 READY")
else:
    print(f"  ✅ {len(PASS)} passed   ❌ {len(FAIL)} failed")
    print(f"  Fix: {', '.join(FAIL)}")
print("═" * 42 + "\n")
sys.exit(0 if not FAIL else 1)
```

---

## 📋 BUILD EXECUTION PLAN

Execute in strict order. Do not skip phases.

### Phase 1 — Dependencies & Config (3 tasks)
```
1. Update requirements.txt — add pygments, RestrictedPython
2. Replace config.yaml with expanded version (all new keys)
3. Create templates/ directory with all 5 .md files
```

### Phase 2 — Agent Intelligence — Track A (3 tasks)
```
4. Rewrite all 5 agent backstories in AgentFactory
5. Add CriticParser class
6. Replace TaskOrchestrator.run() with retry loop
```

### Phase 3 — Memory Upgrades — Track C (3 tasks)
```
7. Add export_memory() to MemoryManager
8. Add search_memory() to MemoryManager
9. Replace store_result() with score-threshold version
```

### Phase 4 — New Features — Track D (3 tasks)
```
10. Add CodeSandbox class
11. Add FileUploadHandler class
12. Create all 5 template files in templates/
```

### Phase 5 — UI/UX — Track B (3 tasks)
```
13. Add DARK_THEME_CSS constant after imports
14. Add AgentStatusDisplay class
15. Rewrite main() with full new layout
```

### Phase 6 — Verification (4 tasks)
```
16. python -m py_compile Home.py  ← must pass
17. Replace test_installation.py with upgraded version
18. python test_installation.py  ← must exit 0
19. Verify all 5 templates exist in templates/
```

---

## ✅ COMPLETION CHECKLIST

```
[ ] requirements.txt has pygments + RestrictedPython
[ ] config.yaml has sandbox, quality_threshold, min_score_to_store
[ ] templates/ has all 5 .md files
[ ] All 5 agent backstories rewritten per spec
[ ] CriticParser class exists with parse() method
[ ] TaskOrchestrator.run() has retry loop returning Dict
[ ] MemoryManager.export_memory() exists
[ ] MemoryManager.search_memory() exists
[ ] MemoryManager.store_result() checks min_score threshold
[ ] CodeSandbox class with execute() + render_ui()
[ ] FileUploadHandler class with render_upload_ui()
[ ] DARK_THEME_CSS constant defined
[ ] AgentStatusDisplay with render_pipeline() + render_score()
[ ] main() has 4-tab layout: Code · Log · Memory · Run Code
[ ] Sidebar has memory search browser
[ ] Sidebar has template buttons (all 5)
[ ] Sidebar has Export + Clear memory with confirmation
[ ] python -m py_compile passes with no errors
[ ] python test_installation.py exits with code 0
```

---

## 🐛 UPGRADE GOTCHAS

1. **crewai==0.28.8 stays pinned** — do not upgrade. `Crew.kickoff()` returns a string in this version.
2. **RestrictedPython exec()** — add `# noqa: S102` to suppress linter warning. It is intentional.
3. **st.session_state** — always guard with `if "key" not in st.session_state` to prevent reset on rerun.
4. **ChromaDB .count()** — call before `.query()` to avoid errors on empty collections.
5. **Dark theme CSS** — must be injected as first `st.markdown()` call in `main()`, before any UI elements.
6. **File upload decode** — always catch `UnicodeDecodeError` separately. Binary files will crash without it.
7. **Template paths** — use `Path()` everywhere. Always check `.exists()` before `.read_text()`.
8. **store_result() signature changed** — it now takes `quality_score` and `iterations` params. Update all call sites.

---

*End of AGENTS.md — Forge Swarm OpenCode Build Spec v3.0*
*4 upgrade tracks · 19 build steps · 20 checklist items · Zero ambiguity.*
*Drop this file, point OpenCode at it, watch it build.*
