#!/usr/bin/env python3
"""
Forge Swarm - Installation Test Script
Run this to verify your installation is correct.

Usage: python test_installation.py
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.10+)")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} installed")
        return True
    except ImportError:
        print(f"❌ {package_name} NOT installed")
        return False

def check_ollama():
    """Check if Ollama is running"""
    print("Checking Ollama...")
    
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:11434/api/tags'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Ollama is running")
            return True
        else:
            print("❌ Ollama is not responding")
            return False
    except FileNotFoundError:
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                print("✅ Ollama is running")
                return True
            else:
                print("❌ Ollama is not responding")
                return False
        except Exception:
            print("❌ Ollama is not running")
            print("   Start it with: ollama serve")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def check_ollama_models():
    """Check if required models are available"""
    print("Checking Ollama models...")
    
    required_models = ['llama3.1:8b', 'nomic-embed-text']
    all_ok = True
    
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        for model in required_models:
            if model in result.stdout:
                print(f"✅ {model} available")
            else:
                print(f"❌ {model} NOT available")
                print(f"   Pull it with: ollama pull {model}")
                all_ok = False
                
        return all_ok
        
    except Exception as e:
        print(f"❌ Could not check models: {e}")
        return False

def check_files():
    """Check if required files exist"""
    print("Checking required files...")
    
    required_files = [
        'forge_swarm_with_ui.py',
        'config.yaml',
        'requirements.txt',
        '.env.example',
        '.gitignore'
    ]
    
    all_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} NOT found")
            all_ok = False
    
    return all_ok

def check_config_methods():
    """Check if Config class has required methods"""
    print("Checking Config class methods...")
    
    try:
        sys.path.insert(0, '.')
        from forge_swarm_with_ui import Config
        
        has_load = hasattr(Config, 'load') and callable(getattr(Config, 'load'))
        has_ollama = hasattr(Config, 'get_ollama_config') and callable(getattr(Config, 'get_ollama_config'))
        has_agent = hasattr(Config, 'get_agent_config') and callable(getattr(Config, 'get_agent_config'))
        
        if has_load:
            print("✅ Config.load() exists")
        else:
            print("❌ Config.load() missing")
        
        if has_ollama:
            print("✅ Config.get_ollama_config() exists")
        else:
            print("❌ Config.get_ollama_config() missing")
        
        if has_agent:
            print("✅ Config.get_agent_config() exists")
        else:
            print("❌ Config.get_agent_config() missing")
        
        return has_load and has_ollama and has_agent
        
    except Exception as e:
        print(f"❌ Error checking Config methods: {e}")
        return False

def check_system_checker():
    """Check if SystemChecker class has required methods"""
    print("Checking SystemChecker class methods...")
    
    try:
        sys.path.insert(0, '.')
        from forge_swarm_with_ui import SystemChecker
        
        has_ollama = hasattr(SystemChecker, 'check_ollama') and callable(getattr(SystemChecker, 'check_ollama'))
        has_model = hasattr(SystemChecker, 'check_model') and callable(getattr(SystemChecker, 'check_model'))
        has_chromadb = hasattr(SystemChecker, 'check_chromadb') and callable(getattr(SystemChecker, 'check_chromadb'))
        has_run_all = hasattr(SystemChecker, 'run_all_checks') and callable(getattr(SystemChecker, 'run_all_checks'))
        
        if has_ollama:
            print("✅ SystemChecker.check_ollama() exists")
        else:
            print("❌ SystemChecker.check_ollama() missing")
        
        if has_model:
            print("✅ SystemChecker.check_model() exists")
        else:
            print("❌ SystemChecker.check_model() missing")
        
        if has_chromadb:
            print("✅ SystemChecker.check_chromadb() exists")
        else:
            print("❌ SystemChecker.check_chromadb() missing")
        
        if has_run_all:
            print("✅ SystemChecker.run_all_checks() exists")
        else:
            print("❌ SystemChecker.run_all_checks() missing")
        
        return has_ollama and has_model and has_chromadb and has_run_all
        
    except Exception as e:
        print(f"❌ Error checking SystemChecker methods: {e}")
        return False

def check_chromadb():
    """Check if ChromaDB can be initialized"""
    print("Checking ChromaDB...")
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        test_path = Path('./test_chromadb_temp')
        test_path.mkdir(exist_ok=True)
        
        client = chromadb.PersistentClient(
            path=str(test_path),
            settings=Settings(anonymized_telemetry=False)
        )
        collection = client.get_or_create_collection("test_collection")
        count = collection.count()
        client.delete_collection("test_collection")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_path, ignore_errors=True)
        
        print(f"✅ ChromaDB initialized (test collection count: {count})")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB initialization failed: {e}")
        return False

def main():
    """Run all checks"""
    print_header("Forge Swarm Installation Test")
    
    results = {}
    
    # Python version
    print_header("1. Python Version")
    results['python'] = check_python_version()
    
    # Required files
    print_header("2. Required Files")
    results['files'] = check_files()
    
    # Python packages
    print_header("3. Python Packages")
    packages = {
        'streamlit': 'streamlit',
        'crewai': 'crewai',
        'langchain-ollama': 'langchain_ollama',
        'chromadb': 'chromadb',
        'pyyaml': 'yaml',
        'python-dotenv': 'dotenv'
    }
    
    package_results = []
    for pkg, import_name in packages.items():
        package_results.append(check_package(pkg, import_name))
    
    results['packages'] = all(package_results)
    
    # Ollama
    print_header("4. Ollama Server")
    results['ollama'] = check_ollama()
    
    # Models
    print_header("5. Ollama Models")
    results['models'] = check_ollama_models()
    
    # ChromaDB
    print_header("6. ChromaDB")
    results['chromadb'] = check_chromadb()
    
    # Config methods
    print_header("7. Config Class Methods")
    results['config_methods'] = check_config_methods()
    
    # SystemChecker methods
    print_header("8. SystemChecker Class Methods")
    results['system_checker_methods'] = check_system_checker()
    
    # Summary
    print_header("Summary")
    
    all_checks = [
        ("Python Version", results['python']),
        ("Required Files", results['files']),
        ("Python Packages", results['packages']),
        ("Ollama Server", results['ollama']),
        ("Ollama Models", results['models']),
        ("ChromaDB", results['chromadb']),
        ("Config Methods", results.get('config_methods', False)),
        ("SystemChecker Methods", results.get('system_checker_methods', False))
    ]
    
    for name, status in all_checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    print()
    
    if all(status for _, status in all_checks):
        print("=" * 60)
        print("  FORGE SWARM — ALL SYSTEMS GO ✅")
        print("=" * 60)
        print("\n🎉 All checks passed! You're ready to run Forge Swarm!")
        print("\nRun the app with:")
        print("  streamlit run forge_swarm_with_ui.py")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        
        if not results['packages']:
            print("  Install packages: pip install -r requirements.txt")
        
        if not results['ollama']:
            print("  Start Ollama: ollama serve")
        
        if not results['models']:
            print("  Pull models: ollama pull llama3.1:8b")
            print("              ollama pull nomic-embed-text")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
