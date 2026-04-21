"""Forge Swarm v3.0 — Installation Verification"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

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
check("chromadb", lambda: __import__("chromadb"))
check("pydantic", lambda: __import__("pydantic"))
check("yaml", lambda: __import__("yaml"))
check("requests", lambda: __import__("requests"))
check("langchain_ollama", lambda: __import__("langchain_ollama"))

print("\n📦 CrewAI")
check("crewai module", lambda: __import__("crewai"))

print("\n📦 New Dependencies")
check("pygments", lambda: __import__("pygments"))
check("RestrictedPython", lambda: __import__("RestrictedPython"))

print("\n⚙️  Configuration")
check("config.yaml exists", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("config.yaml").exists() else None)
check("config.yaml valid", lambda: __import__("yaml").safe_load(open("config.yaml")))

print("\n📋 Templates")
for t in ["fastapi_crud", "data_pipeline", "discord_bot", "web_scraper", "cli_tool"]:
    check(f"templates/{t}.md", lambda t=t: (_ for _ in ()).throw(FileNotFoundError()) if not Path(f"templates/{t}.md").exists() else None)

print("\n📄 Documentation")
check("README.md", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("README.md").exists() else None)
check("LICENSE file", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("LICENSE").exists() else None)
check("install.sh script", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("install.sh").exists() else None)
check("install.ps1 script", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("install.ps1").exists() else None)
check("CONTRIBUTING.md", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("CONTRIBUTING.md").exists() else None)
check("CODE_OF_CONDUCT.md", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("CODE_OF_CONDUCT.md").exists() else None)
check("docs/screenshots directory", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("docs/screenshots").exists() else None)
check("GitHub issue templates", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path(".github/ISSUE_TEMPLATE").exists() else None)

print("\n🌐 Connectivity")
import requests
check("Ollama reachable", lambda: requests.get("http://localhost:11434/api/tags", timeout=5).raise_for_status())

print("\n💾 ChromaDB")
check("ChromaDB module", lambda: __import__("chromadb"))

print("\n🚀 Application")
check("main file exists", lambda: (_ for _ in ()).throw(FileNotFoundError()) if not Path("forge_swarm_with_ui.py").exists() else None)
check("main file compiles", lambda: __import__("py_compile").compile("forge_swarm_with_ui.py"))

print("\n" + "═" * 42)
if not FAIL:
    print(f"  ⚡ ALL {len(PASS)} CHECKS PASSED — FORGE SWARM v3.0 GUMROAD READY")
else:
    print(f"  ✅ {len(PASS)} passed   ❌ {len(FAIL)} failed")
    print(f"  Fix: {', '.join(FAIL)}")
print("═" * 42 + "\n")
sys.exit(0 if not FAIL else 1)
