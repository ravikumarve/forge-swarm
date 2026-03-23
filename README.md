<div align="center">

```
███████╗ ██████╗ ██████╗  ██████╗ ███████╗    ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║
█████╗  ██║   ██║██████╔╝██║  ███╗█████╗      ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║
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
[![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=flat-square)]()

<br/>

> *Five agents. One mission. Your code, never leaving your machine.*

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
| 🤖 | **5 Specialized Agents** | Planner, Researcher, Coder, Tester, Critic — each with a distinct role and persona |
| 🔁 | **Self-Improvement Loop** | Critic scores output 1–10. Below 8? Agents retry automatically |
| 🧠 | **Persistent Vector Memory** | ChromaDB stores lessons from past tasks. Gets smarter over time |
| 🔒 | **100% Local & Private** | Zero cloud calls. No telemetry. Your code never leaves your machine |
| ⚡ | **Streamlit Dashboard** | Real-time agent progress, tabbed output (Code · Log · Memory) |
| 📋 | **Quick-Start Templates** | 5 pre-built templates: FastAPI CRUD, Data Pipeline, Discord Bot, Scraper, CLI |
| 🔧 | **Zero Config to Start** | Works out of the box with `llama3.1:8b` and `nomic-embed-text` |

---

## Architecture

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
│                  │  │ Critic  │ ← self-improvement   │  │
│                  │  └─────────┘                      │  │
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
ollama pull llama3.1:70b       # Best quality (40+ GB RAM)

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
streamlit run forge_swarm_with_ui.py
```

Open **http://localhost:8501** in your browser.

---

## Quick Start

1. Launch: `streamlit run forge_swarm_with_ui.py`
2. Open: `http://localhost:8501`
3. Describe what you want to build in the text area
4. Hit **🚀 Run Forge Swarm**
5. Watch agents work in real time across 3 output tabs:
   - **Final Code** — the generated implementation
   - **Agent Log** — full reasoning chain from all 5 agents
   - **Memory Context** — past lessons that influenced this run

### Built-In Templates

| Template | What It Builds |
|---|---|
| FastAPI CRUD App | REST API · SQLite · Pydantic · pytest |
| Data Pipeline | CSV ingestion · statistical analysis · JSON export |
| Discord Bot | `/hello` `/joke` `/weather` with error handling |
| Web Scraper | Product extraction · CSV output · rate limiting |
| CLI Tool | Click/Typer interface · config support |

---

## Configuration

Edit `config.yaml` to tune behavior:

```yaml
llm:
  model: "llama3.1:8b"
  base_url: "http://localhost:11434"
  temperature: 0.7          # 0.0 = deterministic · 1.0 = creative
  num_ctx: 8192             # Context window size
  timeout: 120              # Seconds before request timeout

embeddings:
  model: "nomic-embed-text"
  base_url: "http://localhost:11434"

memory:
  db_path: "./forge_swarm_memory"
  collection_name: "improvement_lessons"
  max_lessons: 100

agents:
  max_iterations: 3         # Max retry attempts per task
  verbose: true
  allow_delegation: false
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
     ├── Score ≥ 7 → Lesson stored in ChromaDB
     │
     └── Score < 7 → Agents retry (up to max_iterations)

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
| View stats | Sidebar → memory item count + collection name |
| Export backup | Click **Export Memory** → downloads JSON |
| Wipe clean | Click **Clear Memory** → confirmation required |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused localhost:11434` | Run `ollama serve` |
| `Model not found: llama3.1:8b` | Run `ollama pull llama3.1:8b` |
| Out of memory errors | Switch to a smaller model or set `num_ctx: 4096` |
| Slow generation | Reduce `num_ctx` to 2048 |
| Setup wizard loops | Confirm both Ollama is running AND models are pulled |

---

## Project Structure

```
forge-swarm/
├── forge_swarm_with_ui.py    ← Main application
├── config.yaml               ← Runtime configuration
├── requirements.txt          ← Pinned dependencies
├── test_installation.py      ← Smoke test
├── .env.example              ← Environment template
├── .gitignore
├── forge_swarm_memory/       ← Auto-created ChromaDB storage
└── README.md
```

---

## Security

- **Zero external calls** — nothing leaves your machine
- **No telemetry** — no usage tracking of any kind
- **No API keys required** — works fully offline
- **No cloud model calls** — 100% Ollama inference

> ⚠️ **Note:** Forge Swarm does not sandbox generated code execution. Do not run untrusted code in production environments without additional isolation.

---

## Tech Stack

| Technology | Role |
|---|---|
| [Ollama](https://ollama.ai) | Local LLM inference |
| [CrewAI](https://crewai.com) | Multi-agent orchestration |
| [ChromaDB](https://trychroma.com) | Vector memory & embeddings |
| [Streamlit](https://streamlit.io) | Interactive web dashboard |
| [LangChain](https://langchain.com) | LLM application framework |

---

## License

[MIT License](LICENSE) — free to use, modify, and distribute.

---

<div align="center">

**Version 1.0** · March 2026 · Built by [@ravikumarve](https://github.com/ravikumarve)

*Local AI. Full control. Zero compromise.*

</div>
