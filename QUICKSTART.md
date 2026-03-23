# 🚀 Forge Swarm - Quick Start Guide

Get up and running in under 10 minutes!

## Prerequisites Check

✅ Python 3.10+ installed?  
```bash
python --version
```

✅ At least 8GB RAM available?  
✅ 10GB free disk space?

## Installation (5 steps)

### 1. Install Ollama (2 minutes)

```bash
# Copy and paste this command:
curl https://ollama.ai/install.sh | sh
```

### 2. Start Ollama

```bash
ollama serve
```

**Keep this terminal open!** Open a new terminal for the next steps.

### 3. Download Models (5-10 minutes)

```bash
# This will download ~5GB
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

☕ Grab a coffee while it downloads...

### 4. Install Forge Swarm

```bash
# Create a folder
mkdir forge-swarm
cd forge-swarm

# Download the files (or git clone if you have the repo)
# You need: forge_swarm_with_ui.py, config.yaml, requirements.txt

# Install Python dependencies
pip install streamlit crewai==0.28.8 crewai-tools langchain-ollama chromadb pyyaml
```

### 5. Run!

```bash
streamlit run forge_swarm_with_ui.py
```

Your browser should open automatically to http://localhost:8501

## First Task (Try This!)

In the chat input, type:

```
Create a simple Python calculator that can add, subtract, multiply, and divide two numbers with error handling
```

Watch as the swarm:
1. 📋 Plans the implementation
2. 🔍 Researches best practices  
3. 💻 Writes the code
4. 🧪 Creates tests
5. ⚖️ Reviews and scores the output

## Templates (Even Faster!)

1. Click the sidebar (arrow on top-left)
2. Select a template from the dropdown
3. Click "Use This Template"
4. Hit Enter

Available templates:
- FastAPI CRUD App
- Data Pipeline
- Discord Bot
- Web Scraper
- CLI Tool

## Understanding the Output

The swarm will show you:

```
### 🎯 Final Result (Iteration 1, Score: 8/10)

#### 📋 Plan
[Step-by-step plan]

#### 💻 Code  
[Complete implementation]

#### 🧪 Tests
[Test cases]

#### ⚖️ Quality Review
[Critique with score and suggestions]
```

**Score Meaning**:
- 8-10 = Excellent, production-ready
- 6-7 = Good, minor improvements needed
- 4-5 = Functional, but has issues
- 1-3 = Needs major rework

## Settings (Optional)

In the sidebar:

**Max Retry Attempts**: How many times to retry if score < 8
- 1 = Fast but may not be perfect
- 3 = Balanced (recommended)
- 5 = Best quality but slower

**Enable Web Search**: Check this if you want the swarm to search the web for information (requires SERPER_API_KEY)

## Common Issues

### "Connection refused"
→ Ollama isn't running. In a terminal: `ollama serve`

### "Model not found"
→ Model not downloaded. Run: `ollama pull llama3.1:8b`

### Slow/hanging
→ First run is always slow as models load. Be patient!

### Out of memory
→ Close other apps or use a smaller model:
```bash
ollama pull mistral:7b
```
Then edit config.yaml to use `mistral:7b` instead.

## Next Steps

1. **Try the templates** - Fastest way to see what it can do
2. **Experiment with prompts** - Be specific about what you want
3. **Check the sidebar** - See how many lessons it has learned
4. **Review the critique** - Learn from the feedback
5. **Iterate on outputs** - Copy the code, ask for improvements

## Tips for Best Results

✅ **DO**:
- Be specific about what you want
- Mention the language/framework
- Include requirements (error handling, tests, etc.)
- Use templates as starting points

❌ **DON'T**:
- Give vague requests like "make me an app"
- Expect it to work perfectly on first try
- Run code without reviewing it first
- Ask for extremely complex projects (break them down)

## Example Prompts

**Good Prompts** ✅:
```
Create a FastAPI endpoint that accepts JSON, validates it with Pydantic, 
saves to SQLite, and returns a 201 response with error handling

Build a Python script that scrapes product prices from Amazon, 
saves to CSV, and sends an email if price drops below $50

Write a Discord bot with /weather command that uses OpenWeatherMap API,
includes rate limiting, and has proper error messages
```

**Vague Prompts** ❌:
```
Make me a web app
Create something cool
Build a bot
```

## Memory & Learning

The swarm gets smarter over time!

- **Lessons Learned**: See count in sidebar
- **Auto-applied**: Past lessons are used for similar tasks
- **Export**: Click "Export Memory" to backup your lessons

## Getting Help

1. **Check README.md** - Full documentation
2. **Check config.yaml** - Adjust settings
3. **Read the critique** - It tells you what went wrong
4. **Try again** - Increase max iterations

## What's Next?

Once comfortable, explore:
- Custom configuration in `config.yaml`
- Different models (llama3.1:70b for better quality)
- Web search integration
- Exporting and analyzing memory

---

**Congratulations!** 🎉 You're now running a local AI agent swarm!

**Time to complete setup**: ~10 minutes  
**First result**: ~2-5 minutes  
**Total**: Under 15 minutes from zero to working swarm
