# AGENTS.md — Forge Swarm
> **OpenCode Agent Execution Spec** | Version 2.0 | Local-First Multi-Agent AI Platform

---

## 🧠 AGENT MISSION BRIEFING

You are an autonomous coding agent. Your mission is to **build Forge Swarm from zero to fully working** — a 100% local, privacy-first multi-agent AI platform. Read this entire document before writing a single line of code. This file is your single source of truth.

**Do not ask for clarification. Do not skip steps. Execute sequentially.**

---

## 📌 PROJECT SNAPSHOT

| Field | Value |
|---|---|
| **Project Name** | Forge Swarm |
| **Type** | Local-first Multi-Agent Code Generation Platform |
| **Stack** | Python 3.10+, CrewAI, Streamlit, ChromaDB, Ollama, LangChain |
| **AI Backend** | 100% local via Ollama (no external API keys required) |
| **Primary File** | `forge_swarm_with_ui.py` |
| **Config File** | `config.yaml` |
| **Entry Command** | `streamlit run forge_swarm_with_ui.py` |
| **Privacy** | All data stays on-device. No telemetry. No cloud calls. |

---

## 🎯 PRODUCT REQUIREMENTS DOCUMENT (PRD)

### Problem Statement
Developers waste hours on repetitive code generation, review cycles, and debugging. Existing tools either require cloud APIs (privacy risk + cost) or lack collaborative multi-agent reasoning. Forge Swarm solves this with a **fully local, self-improving 5-agent pipeline** that plans, researches, codes, tests, and critiques — all on your own machine.

### Core Value Proposition
- **Zero API cost** — runs entirely on Ollama (local LLM)
- **5-agent collaboration** — each agent has a distinct role and persona
- **Iterative improvement** — agents critique and refine each other's output
- **Persistent memory** — ChromaDB stores context across sessions
- **Clean UI** — Streamlit dashboard for real-time interaction

### Success Criteria (Definition of Done)
- [ ] `streamlit run forge_swarm_with_ui.py` launches without errors
- [ ] All 5 agents initialize and are visible in the UI
- [ ] A task submitted through the UI produces code output
- [ ] ChromaDB memory persists between sessions
- [ ] `python test_installation.py` exits with code 0
- [ ] No hardcoded secrets or API keys anywhere in code

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                    FORGE SWARM SYSTEM                    │
│                                                         │
│  ┌──────────┐    ┌───────────────────────────────────┐  │
│  │Streamlit │───▶│         CrewAI Orchestrator        │  │
│  │   UI     │    │                                   │  │
│  └──────────┘    │  ┌─────────┐    ┌─────────────┐  │  │
│                  │  │ Planner │───▶│  Researcher  │  │  │
│  ┌──────────┐    │  └─────────┘    └─────────────┘  │  │
│  │ChromaDB  │◀───│       │               │           │  │
│  │ Memory   │    │       ▼               ▼           │  │
│  └──────────┘    │  ┌─────────┐    ┌─────────────┐  │  │
│                  │  │  Coder  │◀───│   Tester    │  │  │
│  ┌──────────┐    │  └─────────┘    └─────────────┘  │  │
│  │  Ollama  │◀───│       │                           │  │
│  │ (Local)  │    │       ▼                           │  │
│  └──────────┘    │  ┌─────────┐                      │  │
│                  │  │ Critic  │ (self-improvement)   │  │
│                  │  └─────────┘                      │  │
│                  └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow
```
User Input (Streamlit)
    │
    ▼
Planner Agent → breaks task into subtasks
    │
    ▼
Researcher Agent → gathers context, patterns, best practices
    │
    ▼
Coder Agent → writes initial implementation
    │
    ▼
Tester Agent → writes tests, identifies edge cases
    │
    ▼
Critic Agent → reviews all output, scores quality, requests revisions
    │
    ▼
ChromaDB → stores result + embeddings for future context
    │
    ▼
Streamlit UI → displays final output to user
```

---

## 📁 PROJECT STRUCTURE (BUILD THIS EXACTLY)

```
forge-swarm/
├── forge_swarm_with_ui.py    # Main application — ALL logic lives here
├── config.yaml               # Runtime configuration (no secrets)
├── requirements.txt          # Pinned dependencies
├── test_installation.py      # Smoke test — must pass
├── .env.example              # Template for environment variables
├── .gitignore                # Standard Python gitignore
└── forge_swarm_memory/       # Auto-created at runtime by ChromaDB
```

**Do not create additional files unless explicitly specified above.**

---

## 📦 DEPENDENCIES (requirements.txt)

Create `requirements.txt` with exactly these pinned versions:

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
```

---

## ⚙️ CONFIGURATION (config.yaml)

Create `config.yaml` with this exact structure:

```yaml
# Forge Swarm Configuration
# No secrets here — use .env for anything sensitive

ollama:
  base_url: "http://localhost:11434"
  model: "llama3"           # Change to any model you have pulled
  embedding_model: "nomic-embed-text"
  temperature: 0.7
  timeout: 120

chromadb:
  persist_directory: "./forge_swarm_memory"
  collection_name: "forge_swarm_context"

agents:
  max_iterations: 3
  verbose: true
  memory: true

ui:
  title: "⚡ Forge Swarm"
  page_icon: "⚡"
  layout: "wide"
  theme: "dark"

logging:
  level: "INFO"
  emoji_indicators: true
```

---

## 🤖 AGENT SPECIFICATIONS

Build exactly 5 agents. Each agent spec below defines its role, goal, backstory, and expected behavior.

### Agent 1: Planner
```
Role: Strategic Task Planner
Goal: Decompose complex coding requests into clear, actionable subtasks
Backstory: A senior engineering lead who has shipped 50+ production systems.
           Thinks in systems, breaks complexity into bite-sized work units,
           and writes plans that junior devs can follow without confusion.
Expected Output: Numbered list of subtasks with acceptance criteria per task
```

### Agent 2: Researcher
```
Role: Technical Researcher
Goal: Find patterns, best practices, and relevant context for the coding task
Backstory: A polyglot engineer obsessed with reading source code, RFCs, and
           documentation. Knows 12 languages, has strong opinions on design
           patterns, and always knows the idiomatic way to do something.
Expected Output: Bullet-point research brief with relevant patterns and gotchas
```

### Agent 3: Coder
```
Role: Implementation Engineer
Goal: Write clean, working, production-grade code based on the plan and research
Backstory: A craftsperson who treats code like prose. Every function has one job.
           Every variable name tells a story. Comments explain WHY, not WHAT.
           Never ships code with TODOs unless they're tracked.
Expected Output: Complete, runnable code with inline comments
```

### Agent 4: Tester
```
Role: QA Engineer
Goal: Write comprehensive tests and identify edge cases in the implementation
Backstory: Broke production three times early in their career. Now they see
           failure modes everywhere. Writes tests for the happy path, the
           sad path, and the "what were you thinking" path.
Expected Output: Test file with unit tests covering normal cases + edge cases
```

### Agent 5: Critic
```
Role: Code Critic & Quality Gatekeeper
Goal: Review all output, score quality 1–10, and request targeted revisions
Backstory: A principal engineer with strong opinions and no patience for
           mediocrity. Gives direct, actionable feedback. Scores work honestly.
           Will not approve code that doesn't meet the bar.
Expected Output: Quality score (X/10), specific issues found, revision requests
```

---

## 💻 MAIN APPLICATION SPEC (forge_swarm_with_ui.py)

Build the main application file with these exact classes and functions. Follow the structure precisely.

### Class: `Config`
```python
# Responsibilities:
# - Load config.yaml with sensible defaults
# - Provide typed access to all config values
# - Class method pattern (no instantiation required by callers)

class Config:
    """Centralized configuration management"""
    
    DEFAULTS = {
        "ollama": {"base_url": "http://localhost:11434", "model": "llama3", ...},
        ...
    }
    
    @classmethod
    def load(cls, config_path: str = 'config.yaml') -> Dict[str, Any]:
        """Load config from file or return defaults."""
    
    @classmethod
    def get_ollama_config(cls) -> Dict[str, Any]:
        """Return Ollama-specific config block."""
    
    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Return agent-specific config block."""
```

### Class: `SystemChecker`
```python
# Responsibilities:
# - Check if Ollama is running (GET /api/tags)
# - Check if required model is available
# - Check if ChromaDB can be initialized
# - Return structured health report

class SystemChecker:
    """Pre-flight system health checks"""
    
    @staticmethod
    def check_ollama(base_url: str, timeout: int = 5) -> bool:
        """Return True if Ollama is responding."""
    
    @staticmethod
    def check_model(base_url: str, model_name: str) -> bool:
        """Return True if model is pulled and available."""
    
    @staticmethod
    def check_chromadb(persist_dir: str) -> bool:
        """Return True if ChromaDB can be initialized at path."""
    
    @staticmethod
    def run_all_checks(config: Dict[str, Any]) -> Dict[str, bool]:
        """Run all checks, return dict of {check_name: passed}."""
```

### Class: `MemoryManager`
```python
# Responsibilities:
# - Initialize ChromaDB client with persistence
# - Store task results as embeddings
# - Query similar past tasks for context injection
# - Clear memory on user request

class MemoryManager:
    """Manages ChromaDB persistent memory for agent context"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ChromaDB client and collection."""
    
    def store_result(self, task_id: str, task_description: str, result: str) -> None:
        """Store a completed task result with embeddings."""
    
    def query_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """Return top-n similar past results for context."""
    
    def clear_memory(self) -> None:
        """Delete all stored memories (with confirmation)."""
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Return count of stored items and collection size."""
```

### Class: `AgentFactory`
```python
# Responsibilities:
# - Create all 5 agents with correct config
# - Inject LLM (ChatOllama) into each agent
# - Support verbose mode toggle
# - Return agents as named dict for easy access

class AgentFactory:
    """Creates and configures all Forge Swarm agents"""
    
    def __init__(self, llm: ChatOllama, config: Dict[str, Any]):
        """Store LLM and config references."""
    
    def create_planner(self) -> Agent:
        """Create and return the Planner agent."""
    
    def create_researcher(self) -> Agent:
        """Create and return the Researcher agent."""
    
    def create_coder(self) -> Agent:
        """Create and return the Coder agent."""
    
    def create_tester(self) -> Agent:
        """Create and return the Tester agent."""
    
    def create_critic(self) -> Agent:
        """Create and return the Critic agent."""
    
    def create_all(self) -> Dict[str, Agent]:
        """Create all agents, return as named dict."""
```

### Class: `TaskOrchestrator`
```python
# Responsibilities:
# - Build CrewAI Task objects from user input
# - Wire tasks in correct dependency order
# - Create and run the Crew
# - Return structured result

class TaskOrchestrator:
    """Orchestrates task creation and crew execution"""
    
    def __init__(self, agents: Dict[str, Agent], config: Dict[str, Any]):
        """Store agents and config."""
    
    def build_tasks(self, user_request: str, context: str = "") -> List[Task]:
        """Create ordered task list from user request."""
    
    def run(self, user_request: str, context: str = "") -> str:
        """Build tasks, create crew, execute, return result string."""
```

### Streamlit UI Requirements
Build the UI with these exact sections:

**Sidebar:**
- System status panel (Ollama: ✅/❌, Model: ✅/❌, ChromaDB: ✅/❌)
- Model selector (text input, pre-filled from config)
- Memory stats (items stored, collection size)
- "Clear Memory" button with confirmation
- About section with project description

**Main Area:**
- Title: `⚡ Forge Swarm` with subtitle
- Task input: `st.text_area` — "Describe what you want to build..."
- Optional context toggle: expandable `st.expander` for pasting existing code
- Submit button: "🚀 Run Forge Swarm"
- Progress area: `st.status` container showing which agent is running
- Results area: Tabbed output — Tab 1: Final Code, Tab 2: Agent Log, Tab 3: Memory Context Used
- Copy button for final output

---

## 🧪 TEST FILE SPEC (test_installation.py)

```python
# This file MUST:
# 1. Import all key dependencies and print success/failure per import
# 2. Check Ollama is reachable at localhost:11434
# 3. Attempt to initialize ChromaDB
# 4. Instantiate Config and SystemChecker
# 5. Print a clear PASS/FAIL summary
# 6. Exit with code 0 on all pass, code 1 on any fail

# Format output like:
# ✅ streamlit imported
# ✅ crewai imported  
# ✅ chromadb imported
# ✅ Ollama reachable
# ✅ ChromaDB initialized
# 
# ════════════════════════════
#   FORGE SWARM — ALL SYSTEMS GO ✅
# ════════════════════════════
```

---

## 📝 CODE STYLE RULES (ENFORCE STRICTLY)

### Python Version
- Python 3.10+ required
- Use type hints on all public functions and methods

### Import Order
```python
# 1. Standard library
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime

# 2. Third-party
import streamlit as st
import yaml
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama, OllamaEmbeddings
import chromadb

# 3. Local (none in this project)
```

### Naming Conventions
| Type | Convention | Example |
|---|---|---|
| Classes | PascalCase | `class ConfigManager` |
| Functions/Methods | snake_case | `def load_config()` |
| Variables | snake_case | `llm_config`, `task_list` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES = 3` |
| Private methods | `_` prefix | `def _initialize_db()` |

### Logging with Emoji Indicators
```python
# Use these consistently throughout the codebase:
# ✅ Success
# ❌ Error
# ⚠️  Warning
# 🔄 In progress / loading
# 🧠 Agent thinking
# 💾 Memory operation
# 🔍 Search / research
# ⚡ Execution start
# 📊 Stats / metrics
```

### Error Handling Rules
```python
# ALWAYS: Use specific exception types
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.ConnectionError:
    print("❌ Cannot reach Ollama. Is it running?")
    return False
except requests.exceptions.Timeout:
    print("❌ Request timed out after 5 seconds")
    return False

# NEVER: Bare except
except:
    pass  # This is forbidden
```

### File Operations
```python
# Always use pathlib.Path
from pathlib import Path

config_path = Path('config.yaml')
if config_path.exists():
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
else:
    config = DEFAULT_CONFIG
```

### No Hardcoded Secrets
```python
# FORBIDDEN anywhere in the codebase:
API_KEY = "sk-..."           # ❌ Never
PASSWORD = "admin123"        # ❌ Never
SECRET = "hardcoded_value"   # ❌ Never

# CORRECT — use environment variables:
import os
api_key = os.getenv("OPENAI_API_KEY", "")  # ✅ Fine (but not needed here)
```

### Line Length & Formatting
- Maximum line length: 100 characters
- 4 spaces indentation (never tabs)
- Blank lines between logical sections
- Whitespace around all operators: `x = 1 + 2`, not `x=1+2`

---

## 🚀 BUILD EXECUTION PLAN

Execute these phases in strict order. Complete each phase before starting the next.

### Phase 1: Scaffold (do first)
```
1. Create forge-swarm/ directory structure
2. Create .gitignore (standard Python)
3. Create .env.example with placeholder keys
4. Create requirements.txt (exact versions from spec above)
5. Create config.yaml (exact structure from spec above)
```

### Phase 2: Core Classes
```
6. Build Config class with all methods
7. Build SystemChecker class with all checks
8. Build MemoryManager class with ChromaDB integration
9. Build AgentFactory class with all 5 agents
10. Build TaskOrchestrator class
```

### Phase 3: Streamlit UI
```
11. Build sidebar with system status + controls
12. Build main task input area
13. Build agent execution flow with progress indicators
14. Build tabbed results display
15. Wire everything together in main() function
```

### Phase 4: Tests & Verification
```
16. Build test_installation.py
17. Verify all imports work
18. Verify config loads without errors
19. Verify Streamlit app starts (no import errors)
```

### Phase 5: Polish
```
20. Add docstrings to all public classes and methods
21. Verify no line exceeds 100 characters
22. Verify no hardcoded secrets exist
23. Run python -m py_compile forge_swarm_with_ui.py
24. Final review against this spec
```

---

## ✅ COMPLETION CHECKLIST

Before declaring the build complete, verify each item:

```
[ ] forge_swarm_with_ui.py exists and compiles cleanly
[ ] config.yaml exists with all required keys
[ ] requirements.txt exists with pinned versions
[ ] test_installation.py exists and runs
[ ] All 5 agent classes defined in AgentFactory
[ ] Config class has load(), get_ollama_config(), get_agent_config()
[ ] SystemChecker has check_ollama(), check_model(), check_chromadb(), run_all_checks()
[ ] MemoryManager has store_result(), query_similar(), clear_memory(), get_memory_stats()
[ ] TaskOrchestrator has build_tasks() and run()
[ ] Streamlit UI has sidebar status panel
[ ] Streamlit UI has task input + submit button
[ ] Streamlit UI has tabbed output (Code | Log | Memory)
[ ] No bare except clauses
[ ] No hardcoded API keys or secrets
[ ] All public methods have docstrings
[ ] All type hints present on public methods
[ ] Max line length 100 chars enforced
[ ] Emoji logging indicators used consistently
[ ] python -m py_compile passes with no errors
```

---

## 🐛 KNOWN GOTCHAS & AGENT NOTES

1. **crewai==0.28.8 is pinned** — do not upgrade. Newer versions have breaking API changes.
2. **langchain-ollama vs langchain-community** — use `langchain_ollama.ChatOllama`, not the community version.
3. **ChromaDB persist_directory** — create the directory if it doesn't exist before initializing the client.
4. **Ollama model names** — `llama3` not `llama-3`. Check with `ollama list` for exact names.
5. **Streamlit session state** — use `st.session_state` for storing agent results between reruns.
6. **CrewAI Process** — use `Process.sequential` for the agent pipeline, not `Process.hierarchical`.
7. **OllamaEmbeddings** — requires `nomic-embed-text` model to be pulled: `ollama pull nomic-embed-text`.

---

## 📚 REFERENCE: KEY API PATTERNS

### Initialize ChatOllama
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model=config["ollama"]["model"],
    base_url=config["ollama"]["base_url"],
    temperature=config["ollama"]["temperature"],
)
```

### Create a CrewAI Agent
```python
from crewai import Agent

planner = Agent(
    role="Strategic Task Planner",
    goal="Decompose complex coding requests into clear, actionable subtasks",
    backstory="A senior engineering lead who has shipped 50+ production systems...",
    llm=llm,
    verbose=config["agents"]["verbose"],
    memory=config["agents"]["memory"],
    max_iter=config["agents"]["max_iterations"],
)
```

### Create a CrewAI Task
```python
from crewai import Task

plan_task = Task(
    description=f"Break down this request into subtasks: {user_request}",
    expected_output="Numbered list of subtasks with acceptance criteria",
    agent=planner,
)
```

### Create and Run Crew
```python
from crewai import Crew, Process

crew = Crew(
    agents=[planner, researcher, coder, tester, critic],
    tasks=[plan_task, research_task, code_task, test_task, critic_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff()
```

### Initialize ChromaDB
```python
import chromadb
from pathlib import Path

persist_dir = Path(config["chromadb"]["persist_directory"])
persist_dir.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(persist_dir))
collection = client.get_or_create_collection(
    name=config["chromadb"]["collection_name"]
)
```

---

*End of AGENTS.md — Forge Swarm OpenCode Build Spec v2.0*
*Built for autonomous agent execution. No ambiguity. No hand-holding. Just build it.*
