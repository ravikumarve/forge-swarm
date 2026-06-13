<div align="center">

```
███████╗ ██████╗ ██████╗  ██████╗ ███████╗    ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║
████╗  ██║   ██║██████╔╝██║  ███╗█████╗      ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║
██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝      ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║
██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
```

**A 100% local, privacy-first multi-agent AI platform for autonomous code generation.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.28.8-FF4B4B?style=flat-square)](https://crewai.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=flat-square)](https://ollama.ai)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?style=flat-square)](https://trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-v3.0_Ready-brightgreen?style=flat-square)]()
[![Gumroad](https://img.shields.io/badge/Available_on-Gumroad-FF69B4?style=flat-square)](https://gumroad.com/l/forgeswarm)
[![Discord](https://img.shields.io/badge/Discord-Join-7289DA?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/forgeswarm)

<br/>

> *Five agents. One mission. Your code, never leaving your machine.*

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Clone and install
git clone https://github.com/ravikumarve/forge-swarm.git
cd forge-swarm
bash install.sh

# 2. Launch Forge Swarm
streamlit run Home.py

# 3. Open http://localhost:8501
```

> ⚡ **That's it!** Forge Swarm will auto-configure Ollama, pull required models, and launch the dashboard.

---

<!-- Social Preview Image -->
<div align="center">
  <img src="docs/social-preview.png" alt="Forge Swarm - Local Multi-Agent AI Coding" width="1200">
</div>

---

## What Is Forge Swarm?

Forge Swarm is a self-improving multi-agent pipeline that autonomously **plans, researches, codes, tests, and critiques** software — entirely on your local hardware. No cloud. No subscriptions. No data leaks.

Unlike single-prompt code generators, Forge Swarm runs a **sequential crew of 5 specialized agents** that challenge each other's output, retry below-threshold results, and learn from every completed task via persistent vector memory.

```
Your Request → Planner → Researcher → Coder → Tester → Critic → Refined Output
                                                              ↑          |
                                                              └──────────┘
                                                           (iterates until 8/10)
```

---

## Feature Overview

| | Feature | Detail |
|---|---|---|
| 🤖 | **5 Specialized Agents** | Planner, Researcher, Coder, Tester, Critic — each with distinct role and persona |
| 🔁 | **Self-Improvement Loop** | Critic scores output 1–10. Below 8? Agents retry automatically |
| 🧠 | **Persistent Vector Memory** | ChromaDB stores lessons from past tasks. Semantic search across all lessons |
| 🔒 | **100% Local & Private** | Zero cloud calls. No telemetry. Your code never leaves your machine |
| ⚡ | **Streamlit Dashboard** | Dark theme UI, real-time agent pipeline visualization, 4-tab output |
| 📋 | **Quick-Start Templates** | 5 pre-built templates: FastAPI CRUD, Data Pipeline, Discord Bot, Scraper, CLI |
| 🧪 | **Code Sandbox** | Execute generated Python code safely in a restricted environment |
| 📁 | **File Upload** | Upload existing code or context files for agent reference |
| 🔍 | **Memory Search** | Search through past lessons by keywords, view scores, and stored results |
| 🔧 | **Zero Config to Start** | Works out of the box with `llama3.1:8b` and `nomic-embed-text` |

---

## 💰 Pricing Tiers

<div align="center">

| Tier | Price | What You Get |
|---|---|---|
| **Starter** | $29 | Full Forge Swarm v3.0 · 5 agents · Memory system · Code sandbox · All templates |
| **Pro** | $49 | Everything in Starter + Priority support · Custom agent configs · Advanced templates |
| **Enterprise** | $99 | Everything in Pro + Team license · White-label option · Custom integrations · Dedicated support |

</div>

> 💡 **All tiers include lifetime updates.** No subscriptions. No hidden fees. Your code, your rules.
>
> 🛒 **[Get Forge Swarm on Gumroad](https://gumroad.com/l/forgeswarm)** · 30-day money-back guarantee

---

## 🎯 Why Choose Forge Swarm?

| Challenge | Forge Swarm Solution |
|---|---|
| **Single-prompt limitations** | 5 specialized agents that challenge each other's output |
| **No learning from mistakes** | Persistent vector memory stores lessons from every task |
| **Privacy concerns** | 100% local — your code never leaves your machine |
| **Recurring subscription fatigue** | One-time purchase with lifetime updates |
| **No quality control** | Critic agent scores output 1–10, auto-retries below 8/10 |
| **Limited context** | Upload files, paste code, search past lessons for context |

---

## 🆚 Feature Comparison

| Feature | Forge Swarm | Cursor | Windsurf | GitHub Copilot |
|---|---|---|---|---|
| **Multi-Agent Pipeline** | ✅ 5 specialized agents | ❌ Single agent | ❌ Single agent | ❌ Single agent |
| **Self-Improvement Loop** | ✅ Auto-retry on low scores | ❌ No retry | ❌ No retry | ❌ No retry |
| **Persistent Memory** | ✅ ChromaDB vector store | ❌ No memory | ❌ No memory | ❌ No memory |
| **100% Local & Private** | ✅ Zero cloud calls | ❌ Cloud required | ❌ Cloud required | ❌ Cloud required |
| **Code Sandbox** | ✅ Restricted execution | ❌ No sandbox | ❌ No sandbox | ❌ No sandbox |
| **File Upload Context** | ✅ Upload files for context | ❌ No upload | ❌ No upload | ❌ No upload |
| **Quick-Start Templates** | ✅ 5 pre-built templates | ❌ No templates | ❌ No templates | ❌ No templates |
| **Memory Search** | ✅ Semantic search across lessons | ❌ No search | ❌ No search | ❌ No search |
| **Real-Time Agent Status** | ✅ Visual pipeline monitoring | ❌ No status | ❌ No status | ❌ No status |
| **Dark Theme UI** | ✅ Built-in dark theme | ✅ Dark mode | ✅ Dark mode | ✅ Dark mode |
| **Pricing** | 💰 One-time purchase | 💰 $20/month | 💰 $15/month | 💰 $10/month |
| **Open Source** | ✅ MIT License | ❌ Proprietary | ❌ Proprietary | ❌ Proprietary |

---

## 💰 Pricing Tiers

| Tier | Price | What You Get |
|---|---|---|
| **Starter** | $29 | Full Forge Swarm v3.0 · 5 agents · Memory system · Code sandbox · All templates |
| **Pro** | $49 | Everything in Starter + Priority support · Custom agent configs · Advanced templates |
| **Enterprise** | $99 | Everything in Pro + Team license · White-label option · Custom integrations · Dedicated support |

> 💡 **All tiers include lifetime updates.** No subscriptions. No hidden fees. Your code, your rules.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FORGE SWARM v3.0                      │
│                                                         │
│  ┌──────────┐    ┌───────────────────────────────────┐  │
│  │Streamlit │───▶│         CrewAI Orchestrator          │  │
│  │   UI     │    │  Dark Theme · Agent Status Cards     │  │
│  │  Dark   │    │                                   │  │
│  └──────────┘    │  ┌─────────┐    ┌─────────────┐  │  │
│                  │  │ Planner │───▶│  Researcher  │  │  │
│  ┌──────────┐    │  └─────────┘    └─────────────┘  │  │
│  │ChromaDB  │◀───│       │               │           │  │
│  │ Memory   │    │       ▼               ▼           │  │
│  │ Semantic │    │  ┌─────────┐    ┌─────────────┐  │  │
│  │ Search   │    │  │  Coder  │◀───│   Tester    │  │  │
│  └──────────┘    │  └─────────┘    └─────────────┘  │  │
│                  │       │                           │  │
│  ┌──────────┐    │       ▼                           │  │
│  │  Code    │◀───│  ┌─────────┐                      │  │
│  │ Sandbox  │    │  │ Critic  │ ← self-improvement   │  │
│  └──────────┘    │  └─────────┘                      │  │
│                  └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Requirements

### System

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| CPU Cores | 4 | 8+ |
| Storage | 10 GB | 20 GB |
| OS | Linux · macOS · Windows (WSL2) | Linux · macOS |

### Software

- **Python** 3.10+
- **Ollama** 0.1.0+

---

## Installation

### 1 — Install Ollama

```bash
# Linux / macOS
curl https://ollama.ai/install.sh | sh

# Windows → https://ollama.ai/download
```

### 2 — Start Ollama

```bash
ollama serve
```

### 3 — Pull Required Models

```bash
# Language model — pick one based on available RAM
ollama pull llama3.1:8b        # ← Recommended (8 GB RAM)
ollama pull mistral:7b         # Alternative
ollama pull llama3.1:70b     # Best quality (40+ GB RAM)

# Embeddings model — required for memory
ollama pull nomic-embed-text
```

### 4 — Install Python Dependencies

```bash
git clone <repository-url>
cd forge-swarm

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 5 — Verify & Run

```bash
python test_installation.py     # All checks must pass
streamlit run Home.py
```

Open **http://localhost:8501** in your browser.

---

## Quick Start

1. Launch: `streamlit run Home.py`
2. Open: `http://localhost:8501`
3. Describe what you want to build in the text area
4. Optionally add context: paste code, errors, or upload files
5. Hit **🚀 Run Forge Swarm**
6. Watch agents work in real time across 4 output tabs:
   - **📄 Final Code** — the generated implementation
   - **📋 Agent Log** — full reasoning chain from all 5 agents
   - **🧠 Memory Context** — past lessons that influenced this run
   - **🧪 Run Code** — sandbox to test the generated code

### Built-In Templates

| Template | What It Builds |
|---|---|
| ⚡ FastAPI CRUD | REST API · SQLite · Pydantic v2 · pytest |
| 📊 Data Pipeline | CSV ingestion · pandas · statistics · JSON export |
| 🤖 Discord Bot | `/hello` `/help` `/ping` `/roll` with error handling |
| 🕷️ Web Scraper | httpx · BeautifulSoup · rate limiting · robots.txt |
| 🖥️ CLI Tool | Typer · Rich output · YAML config · shell completion |

---

## 📸 Screenshots

### Main Dashboard
![Main Dashboard](docs/screenshots/main-dashboard.png)
*Dark theme UI with real-time agent pipeline visualization*

### Agent Pipeline in Action
![Agent Pipeline](docs/screenshots/agent-pipeline.gif)
*Watch all 5 agents work sequentially with live status updates*

### Memory Search & Browse
![Memory System](docs/screenshots/memory-search.png)
*Search through past lessons with semantic similarity*

### Code Sandbox Execution
![Code Sandbox](docs/screenshots/code-sandbox.png)
*Safely execute generated Python code in restricted environment*

### Template Quick-Start
![Templates](docs/screenshots/templates.png)
*5 pre-built templates for instant productivity*

> 🎬 **Video Demo:** [Watch Forge Swarm in action](https://youtube.com/watch?v=forge-swarm-demo)

---

## Configuration

Edit `config.yaml` to tune behavior:

```yaml
llm:
  model: "llama3.1:8b"
  base_url: "http://localhost:11434"
  temperature: 0.7          # 0.0 = deterministic · 1.0 = creative
  num_ctx: 8192            # Context window size
  timeout: 120             # Seconds before request timeout

embeddings:
  model: "nomic-embed-text"
  base_url: "http://localhost:11434"

memory:
  db_path: "./forge_swarm_memory"
  collection_name: "improvement_lessons"
  max_lessons: 200         # Maximum lessons to store
  min_score_to_store: 7     # Only store lessons above this score
  max_context_results: 5    # Max past lessons to retrieve

agents:
  max_iterations: 5        # Max retry attempts per task
  verbose: true
  allow_delegation: false
  quality_threshold: 8       # Score needed to stop retrying
  retry_on_below_threshold: true

sandbox:
  enabled: true             # Enable code execution sandbox
  timeout_seconds: 10       # Max execution time
  max_output_lines: 100    # Truncate output after this many lines
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

### Environment Variables

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `SERPER_API_KEY` | Optional | Enables web search for the Researcher agent |

---

## Memory System

Forge Swarm gets smarter the more you use it. Here's how:

```
Task Completed
     │
     ▼
Critic scores output (1–10)
     │
     ├── Score ≥ 7 → Lesson stored in ChromaDB with full metadata
     │
     └── Score < 7 → Agents retry with feedback (up to max_iterations)

Next Task
     │
     ▼
Relevant past lessons retrieved via vector similarity
     │
     ▼
Context injected into current agent run
```

**Managing memory from the sidebar:**

| Action | How |
|---|---|
| View stats | Sidebar → memory item count |
| Search lessons | Sidebar → 🔍 Search Memory → enter keywords |
| Export backup | Click **📤 Export** → downloads JSON |
| Wipe clean | Click **🗑️ Clear** → confirmation required |

---

## Code Sandbox

The built-in sandbox lets you safely execute generated Python code:

- **RestrictedPython** — only safe imports allowed
- **No filesystem access** — code cannot read/write files
- **No network access** — code cannot make HTTP requests
- **Output limits** — truncated after 100 lines
- **Execution timeout** — killed after 10 seconds

Edit the code in the sandbox, click **▶️ Run Code**, and see results instantly.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused localhost:11434` | Run `ollama serve` |
| `Model not found: llama3.1:8b` | Run `ollama pull llama3.1:8b` |
| Out of memory errors | Switch to a smaller model or set `num_ctx: 4096` |
| Slow generation | Reduce `num_ctx` to 2048 |
| Setup wizard loops | Confirm both Ollama is running AND models are pulled |
| Sandbox errors | Check `config.yaml` → `sandbox.enabled: true` |

---

## ❓ Frequently Asked Questions

### General

**Q: Is Forge Swarm really 100% local?**
A: Yes. Forge Swarm runs entirely on your machine using Ollama for LLM inference. No data leaves your computer. No cloud calls. No telemetry.

**Q: What's the difference between Forge Swarm and Cursor/Windsurf?**
A: Forge Swarm uses a multi-agent pipeline with 5 specialized agents that challenge each other's output, retry below-threshold results, and learn from past tasks. Cursor and Windsurf are single-agent tools that require cloud subscriptions.

**Q: Can I use Forge Swarm offline?**
A: Yes! Once you've installed Ollama and pulled the models, Forge Swarm works completely offline. No internet connection required.

**Q: What models does Forge Swarm support?**
A: Forge Swarm works with any Ollama model. We recommend `llama3.1:8b` for best balance of speed and quality, but you can use `mistral:7b`, `llama3.1:70b`, or any other model you have installed.

### Technical

**Q: What are the system requirements?**
A: Minimum: 8 GB RAM, 4 CPU cores, 10 GB storage. Recommended: 16 GB RAM, 8+ CPU cores, 20 GB storage.

**Q: Can I run Forge Swarm on Windows?**
A: Yes! Forge Swarm works on Windows (via WSL2), Linux, and macOS. Use the provided `install.sh` (Linux/Mac) or `install.ps1` (Windows) scripts.

**Q: How does the memory system work?**
A: Forge Swarm uses ChromaDB to store lessons from completed tasks. When you start a new task, it retrieves relevant past lessons via vector similarity and injects them as context. Only lessons scoring 7+/10 are stored.

**Q: Is the code sandbox safe?**
A: The sandbox uses RestrictedPython to limit execution to safe imports only. It blocks filesystem access, network calls, and system commands. However, always review generated code before running in production.

**Q: Can I customize the agents?**
A: Yes! You can edit agent backstories in `Home.py` or modify `config.yaml` to adjust behavior, quality thresholds, retry logic, and more.

### Pricing & Support

**Q: Is this a subscription?**
A: No! Forge Swarm is a one-time purchase. All tiers include lifetime updates with no recurring fees.

**Q: What's included in each tier?**
A: All tiers include the full Forge Swarm v3.0 with 5 agents, memory system, code sandbox, and all templates. Pro and Enterprise tiers include priority support, custom configurations, and additional features.

**Q: Do you offer refunds?**
A: Yes! If Forge Swarm doesn't work on your system, we offer a 30-day money-back guarantee.

**Q: How do I get support?**
A: Email support@forgeswarm.com or join our Discord community at discord.gg/forgeswarm.

---

## Project Structure

```
forge-swarm/
├── Home.py    ← Main application
├── config.yaml               ← Runtime configuration
├── requirements.txt          ← Pinned dependencies
├── test_installation.py      ← Smoke test
├── .env.example              ← Environment template
├── .gitignore
├── templates/                ← Quick-start templates
│   ├── fastapi_crud.md
│   ├── data_pipeline.md
│   ├── discord_bot.md
│   ├── web_scraper.md
│   └── cli_tool.md
├── forge_swarm_memory/       ← Auto-created ChromaDB storage
└── README.md
```

---

## Security

- **Zero external calls** — nothing leaves your machine
- **No telemetry** — no usage tracking of any kind
- **No API keys required** — works fully offline
- **No cloud model calls** — 100% Ollama inference
- **Code sandbox** — restricted Python execution environment

> ⚠️ **Note:** While the code sandbox restricts execution, always review generated code before running in production environments.

---

## Tech Stack

| Technology | Role |
|---|---|
| [Ollama](https://ollama.ai) | Local LLM inference |
| [CrewAI](https://crewai.com) | Multi-agent orchestration |
| [ChromaDB](https://trychroma.com) | Vector memory & embeddings |
| [Streamlit](https://streamlit.io) | Interactive web dashboard |
| [LangChain](https://langchain.com) | LLM application framework |
| [RestrictedPython](https://pypi.org/project/RestrictedPython/) | Safe code execution sandbox |

---

## License

[MIT License](LICENSE) — free to use, modify, and distribute.

---

<div align="center">

**Version 3.0** · March 2026 · Built by [@ravikumarve](https://github.com/ravikumarve)

*Local AI. Full control. Zero compromise.*

</div>
