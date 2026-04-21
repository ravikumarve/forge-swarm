# Forge Swarm — Gumroad Product Description

## Product Overview

Forge Swarm is a revolutionary 100% local, privacy-first multi-agent AI platform for autonomous code generation. Unlike single-prompt code generators that require cloud subscriptions and send your code to external servers, Forge Swarm runs entirely on your machine using a sophisticated pipeline of 5 specialized AI agents that collaborate, challenge each other's output, and continuously improve through persistent vector memory.

The platform features a Planner agent that breaks down complex tasks, a Researcher agent that finds best practices and patterns, a Coder agent that writes production-grade code, a Tester agent that creates comprehensive test suites, and a Critic agent that scores output quality and triggers automatic retries when quality falls below threshold. This multi-agent approach ensures higher quality output, better error handling, and more robust implementations than any single-agent solution.

Forge Swarm includes a beautiful dark-themed Streamlit dashboard with real-time agent pipeline visualization, a code sandbox for safe execution, file upload capabilities for context injection, and a semantic memory system that learns from every completed task. With 5 pre-built quick-start templates for common projects like FastAPI CRUD apps, data pipelines, Discord bots, web scrapers, and CLI tools, you can be productive from day one.

## Key Features

### 🤖 Multi-Agent Pipeline
- **5 Specialized Agents**: Planner, Researcher, Coder, Tester, and Critic work sequentially
- **Self-Improvement Loop**: Critic scores output 1-10, auto-retries below 8/10 threshold
- **Collaborative Intelligence**: Agents challenge each other's output for better quality

### 🧠 Persistent Vector Memory
- **ChromaDB Integration**: Stores lessons from every completed task
- **Semantic Search**: Retrieve relevant past lessons via vector similarity
- **Smart Context Injection**: Past lessons automatically inform new tasks
- **Score-Based Storage**: Only high-quality lessons (7+/10) are retained

### 🔒 100% Local & Private
- **Zero Cloud Calls**: All inference runs on your machine via Ollama
- **No Telemetry**: No usage tracking or data collection
- **No API Keys Required**: Works fully offline after initial setup
- **Your Code Stays Yours**: Nothing leaves your computer

### ⚡ Beautiful Dashboard
- **Dark Theme UI**: Professional, easy-on-the-eyes interface
- **Real-Time Agent Status**: Visual pipeline monitoring with live updates
- **4-Tab Output Layout**: Final Code, Agent Log, Memory Context, Code Sandbox
- **Responsive Design**: Works on desktop, tablet, and mobile

### 🧪 Code Sandbox
- **Restricted Execution**: Safe Python environment with limited imports
- **No Filesystem Access**: Code cannot read/write files
- **No Network Access**: Code cannot make HTTP requests
- **Output Limits**: Truncated after 100 lines, 10-second timeout

### 📋 Quick-Start Templates
- **FastAPI CRUD**: REST API with SQLite, Pydantic v2, pytest
- **Data Pipeline**: CSV processing, statistics, JSON export
- **Discord Bot**: Slash commands, error handling, structured logging
- **Web Scraper**: httpx, BeautifulSoup, rate limiting, robots.txt
- **CLI Tool**: Typer, Rich output, YAML config, shell completion

### 📁 File Upload & Context
- **Upload Files**: Add existing code, error logs, or documentation
- **Paste Context**: Include background information for better results
- **Multiple Formats**: Support for .py, .txt, .md, .json, .yaml, .js, .ts

### 🔍 Memory Management
- **Search Lessons**: Find past tasks by keywords or semantic similarity
- **Export Backup**: Download all lessons as JSON
- **Clear Memory**: Wipe clean with confirmation dialog
- **View Stats**: Track lesson count and quality distribution

## Pricing Tiers

### Starter — $29
- Full Forge Swarm v3.0 with all 5 agents
- Complete memory system with ChromaDB
- Code sandbox for safe execution
- All 5 quick-start templates
- Dark theme dashboard
- Lifetime updates
- Email support

### Pro — $49
- Everything in Starter
- Priority email support (24-hour response)
- Custom agent configuration templates
- Advanced template pack (10 additional templates)
- Early access to new features
- Discord community access

### Enterprise — $99
- Everything in Pro
- Team license (up to 5 users)
- White-label option
- Custom integrations
- Dedicated support channel
- Onboarding session
- Custom training materials

## System Requirements

### Minimum Requirements
- **RAM**: 8 GB
- **CPU**: 4 cores
- **Storage**: 10 GB free space
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher

### Recommended Requirements
- **RAM**: 16 GB
- **CPU**: 8+ cores
- **Storage**: 20 GB free space
- **OS**: macOS, Linux (native performance)
- **Python**: 3.11 or higher

### Software Dependencies
- **Ollama**: 0.1.0+ (for local LLM inference)
- **Models**: llama3.1:8b (recommended) or mistral:7b, nomic-embed-text

### Model Requirements
- **llama3.1:8b**: 8 GB RAM (recommended for most users)
- **mistral:7b**: 6 GB RAM (faster, slightly lower quality)
- **llama3.1:70b**: 40+ GB RAM (best quality, slower)

## Support & Contact

### Support Channels
- **Email**: support@forgeswarm.com
- **Discord**: https://discord.gg/forgeswarm
- **GitHub Issues**: https://github.com/ravikumarve/forge-swarm/issues
- **Documentation**: https://github.com/ravikumarve/forge-swarm/blob/main/README.md

### Response Times
- **Starter Tier**: 48-hour response time
- **Pro Tier**: 24-hour response time
- **Enterprise Tier**: 4-hour response time

### Refund Policy
- 30-day money-back guarantee
- No questions asked if Forge Swarm doesn't work on your system
- Contact support@forgeswarm.com for refunds

### Updates & Maintenance
- All tiers include lifetime updates
- Bug fixes released within 7 days of reporting
- New features rolled out quarterly
- Security patches released immediately

## Installation

### Quick Install (3 Commands)
```bash
git clone https://github.com/ravikumarve/forge-swarm.git
cd forge-swarm
bash install.sh  # Windows: install.ps1
```

### Manual Install
1. Install Python 3.10+
2. Install Ollama from https://ollama.ai
3. Pull models: `ollama pull llama3.1:8b` and `ollama pull nomic-embed-text`
4. Clone repository and run: `pip install -r requirements.txt`
5. Launch: `streamlit run forge_swarm_with_ui.py`

## What's Included

### Files
- `forge_swarm_with_ui.py` — Main application
- `config.yaml` — Runtime configuration
- `requirements.txt` — Python dependencies
- `test_installation.py` — Installation verification
- `install.sh` — Linux/macOS installer
- `install.ps1` — Windows installer
- `LICENSE` — MIT License
- `README.md` — Complete documentation
- `CONTRIBUTING.md` — Contribution guidelines
- `CODE_OF_CONDUCT.md` — Community standards

### Templates
- `templates/fastapi_crud.md` — FastAPI REST API template
- `templates/data_pipeline.md` — Data processing pipeline template
- `templates/discord_bot.md` — Discord bot template
- `templates/web_scraper.md` — Web scraper template
- `templates/cli_tool.md` — CLI application template

### Documentation
- Complete README with installation guide
- Troubleshooting section
- FAQ section
- Configuration reference
- Architecture diagrams

## Why Choose Forge Swarm?

### vs. Cursor
- **Multi-agent vs Single-agent**: 5 specialized agents vs 1 general agent
- **Local vs Cloud**: 100% local vs cloud-required
- **Memory vs No Memory**: Persistent learning vs no retention
- **One-time vs Subscription**: $29 one-time vs $20/month

### vs. Windsurf
- **Self-Improvement vs Static**: Auto-retry on low quality vs no retry
- **Privacy vs Data Collection**: Zero telemetry vs usage tracking
- **Templates vs Blank**: 5 pre-built templates vs start from scratch
- **One-time vs Subscription**: $29 one-time vs $15/month

### vs. GitHub Copilot
- **Autonomous vs Assistive**: Full code generation vs code completion
- **Local vs Cloud**: Your machine vs Microsoft servers
- **Multi-Agent vs Single**: Collaborative pipeline vs single model
- **One-time vs Subscription**: $29 one-time vs $10/month

## Testimonials

*"Forge Swarm has completely transformed my development workflow. The multi-agent approach catches edge cases I never would have thought of, and the memory system means it gets smarter with every project."* — Senior Developer, Tech Startup

*"Finally, an AI coding tool that respects my privacy. I can work on sensitive projects without worrying about my code leaving my machine. The quality is on par with cloud solutions, but I have full control."* — Freelance Developer

*"The templates alone are worth the price. I went from idea to deployed Discord bot in under an hour. The agents work together seamlessly, and the auto-retry feature ensures I always get production-ready code."* — Indie Hacker

## FAQ

**Q: Is Forge Swarm really 100% local?**
A: Yes. Forge Swarm runs entirely on your machine using Ollama for LLM inference. No data leaves your computer. No cloud calls. No telemetry.

**Q: What if it doesn't work on my system?**
A: We offer a 30-day money-back guarantee. If Forge Swarm doesn't work on your system, contact support@forgeswarm.com for a full refund.

**Q: Can I use Forge Swarm offline?**
A: Yes! Once you've installed Ollama and pulled the models, Forge Swarm works completely offline. No internet connection required.

**Q: How does the memory system work?**
A: Forge Swarm uses ChromaDB to store lessons from completed tasks. When you start a new task, it retrieves relevant past lessons via vector similarity and injects them as context. Only lessons scoring 7+/10 are stored.

**Q: Can I customize the agents?**
A: Yes! You can edit agent backstories in `forge_swarm_with_ui.py` or modify `config.yaml` to adjust behavior, quality thresholds, retry logic, and more.

**Q: What's the difference between tiers?**
A: All tiers include the full Forge Swarm v3.0. Pro and Enterprise tiers include priority support, custom configurations, additional templates, and team licensing.

## License

Forge Swarm is released under the MIT License, which means you're free to use, modify, and distribute it as you see fit. The MIT License is included in the repository.

## Version History

- **v3.0** (March 2026) — Full release with multi-agent pipeline, memory system, code sandbox
- **v2.0** (February 2026) — Beta with improved agent backstories and retry logic
- **v1.0** (January 2026) — Initial alpha release

---

*Forge Swarm — Local AI. Full control. Zero compromise.*
