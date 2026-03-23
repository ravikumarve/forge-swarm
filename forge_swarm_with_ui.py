"""
Forge Swarm - Complete Production-Ready UI
Version: 1.0
Last updated: February 2026

A 100% local, offline, privacy-first multi-agent AI platform.
Fully refactored with proper error handling, configuration, and features.

Requirements:
    pip install streamlit crewai crewai-tools langchain-ollama chromadb python-dotenv pyyaml

Before running:
    1. Start Ollama: ollama serve
    2. Pull models: ollama pull llama3.1:8b && ollama pull nomic-embed-text
    3. Run: streamlit run forge_swarm_with_ui.py
"""

import os
import sys
import json
import subprocess
import traceback
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

# Disable telemetry BEFORE importing CrewAI
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy-ollama-only")

import streamlit as st
import yaml
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama, OllamaEmbeddings
from crewai_tools import SerperDevTool
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

class Config:
    """Centralized configuration management"""
    
    DEFAULT_CONFIG = {
        'llm': {
            'model': 'llama3.1:8b',
            'base_url': 'http://localhost:11434',
            'temperature': 0.7,
            'num_ctx': 8192,
            'timeout': 120
        },
        'embeddings': {
            'model': 'nomic-embed-text',
            'base_url': 'http://localhost:11434'
        },
        'memory': {
            'db_path': './forge_swarm_memory',
            'collection_name': 'improvement_lessons',
            'max_lessons': 100,
            'retention_days': 180
        },
        'agents': {
            'max_iterations': 3,
            'verbose': True,
            'allow_delegation': False
        },
        'ui': {
            'page_title': 'Forge Swarm',
            'page_icon': '🤖',
            'layout': 'wide'
        }
    }
    
    @classmethod
    def load(cls, config_path: str = 'config.yaml') -> Dict[str, Any]:
        """Load config from file or return defaults"""
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                # Merge with defaults
                config = cls.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except Exception as e:
                st.warning(f"Could not load config: {e}. Using defaults.")
        return cls.DEFAULT_CONFIG
    
    @classmethod
    def save(cls, config: Dict[str, Any], config_path: str = 'config.yaml'):
        """Save config to file"""
        try:
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            st.error(f"Could not save config: {e}")
            return False
    
    @classmethod
    def get_ollama_config(cls, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Return Ollama-specific config block (llm + embeddings)."""
        if config is None:
            config = cls.load()
        return {
            "base_url": config.get('llm', {}).get('base_url', 'http://localhost:11434'),
            "model": config.get('llm', {}).get('model', 'llama3.1:8b'),
            "embedding_model": config.get('embeddings', {}).get('model', 'nomic-embed-text'),
            "temperature": config.get('llm', {}).get('temperature', 0.7),
            "timeout": config.get('llm', {}).get('timeout', 120),
        }
    
    @classmethod
    def get_agent_config(cls, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Return agent-specific config block."""
        if config is None:
            config = cls.load()
        return {
            "max_iterations": config.get('agents', {}).get('max_iterations', 3),
            "verbose": config.get('agents', {}).get('verbose', True),
            "memory": True,
        }


# ============================================================================
# SYSTEM HEALTH CHECKS
# ============================================================================

class SystemChecker:
    """Check system dependencies and health"""
    
    @staticmethod
    def check_ollama() -> tuple[bool, str]:
        """Check if Ollama is running"""
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/tags'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "Ollama is running"
            return False, "Ollama is not responding"
        except subprocess.TimeoutExpired:
            return False, "Ollama connection timeout"
        except FileNotFoundError:
            # Try using Python requests as fallback
            try:
                import requests
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                if response.status_code == 200:
                    return True, "Ollama is running"
                return False, f"Ollama returned status {response.status_code}"
            except Exception:
                return False, "Ollama is not running. Start it with: ollama serve"
        except Exception as e:
            return False, f"Error checking Ollama: {str(e)}"
    
    @staticmethod
    def check_model(model_name: str) -> tuple[bool, str]:
        """Check if a model is available"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if model_name in result.stdout:
                return True, f"Model {model_name} is available"
            return False, f"Model {model_name} not found. Pull it with: ollama pull {model_name}"
        except Exception as e:
            return False, f"Could not check model: {str(e)}"
    
    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available Ollama models"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = [line.split()[0] for line in lines if line.strip()]
            return models
        except Exception:
            return []
    
    @staticmethod
    def check_chromadb(persist_dir: str) -> tuple[bool, str]:
        """Check if ChromaDB can be initialized at path."""
        try:
            db_path = Path(persist_dir)
            db_path.mkdir(parents=True, exist_ok=True)
            
            test_client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            test_collection = test_client.get_or_create_collection("test_check")
            test_client.delete_collection("test_check")
            return True, "ChromaDB is accessible"
        except Exception as e:
            return False, f"ChromaDB error: {str(e)}"
    
    @staticmethod
    def run_all_checks(config: Dict[str, Any]) -> Dict[str, tuple[bool, str]]:
        """Run all system checks, return dict of {check_name: (passed, message)}."""
        ollama_ok, ollama_msg = SystemChecker.check_ollama()
        model_name = config.get('llm', {}).get('model', 'llama3.1:8b')
        model_ok, model_msg = SystemChecker.check_model(model_name)
        emb_model = config.get('embeddings', {}).get('model', 'nomic-embed-text')
        emb_ok, emb_msg = SystemChecker.check_model(emb_model)
        chromadb_path = config.get('memory', {}).get('db_path', './forge_swarm_memory')
        chromadb_ok, chromadb_msg = SystemChecker.check_chromadb(chromadb_path)
        
        return {
            "ollama": (ollama_ok, ollama_msg),
            "model": (model_ok, model_msg),
            "embeddings": (emb_ok, emb_msg),
            "chromadb": (chromadb_ok, chromadb_msg),
        }


# ============================================================================
# LLM MANAGER
# ============================================================================

class LLMManager:
    """Manage LLM and embeddings initialization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._llm = None
        self._embedder = None
    
    @property
    def llm(self) -> ChatOllama:
        """Lazy-load LLM"""
        if self._llm is None:
            llm_config = self.config['llm']
            self._llm = ChatOllama(
                model=llm_config['model'],
                base_url=llm_config['base_url'],
                temperature=llm_config['temperature'],
                num_ctx=llm_config['num_ctx']
            )
        return self._llm
    
    @property
    def embedder(self) -> OllamaEmbeddings:
        """Lazy-load embeddings"""
        if self._embedder is None:
            emb_config = self.config['embeddings']
            self._embedder = OllamaEmbeddings(
                model=emb_config['model'],
                base_url=emb_config['base_url']
            )
        return self._embedder
    
    def test_connection(self) -> tuple[bool, str]:
        """Test LLM connection"""
        try:
            response = self.llm.invoke("Hello")
            return True, "LLM connection successful"
        except Exception as e:
            return False, f"LLM connection failed: {str(e)}"


# ============================================================================
# MEMORY MANAGER
# ============================================================================

class MemoryManager:
    """Manage long-term memory with ChromaDB"""
    
    def __init__(self, config: Dict[str, Any], embedder: OllamaEmbeddings):
        self.config = config['memory']
        self.embedder = embedder
        self.client = None
        self.collection = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize ChromaDB"""
        try:
            db_path = self.config['db_path']
            Path(db_path).mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.config['collection_name']
            )
        except Exception as e:
            st.error(f"Failed to initialize memory database: {e}")
            raise
    
    def save_lesson(self, task_desc: str, output: str, critic_feedback: str, score: float):
        """Save a lesson to memory"""
        try:
            text = f"Task: {task_desc}\nFeedback: {critic_feedback}"
            embedding = self.embedder.embed_documents([text])[0]
            
            lesson_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.collection.count()}"
            
            self.collection.add(
                documents=[critic_feedback],
                metadatas=[{
                    "task": task_desc[:200],
                    "output_summary": output[:200],
                    "score": score,
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[lesson_id],
                embeddings=[embedding]
            )
            
            # Prune old lessons if needed
            self._prune_old_lessons()
            
        except Exception as e:
            st.warning(f"Could not save lesson: {e}")
    
    def get_relevant_lessons(self, task_desc: str, n: int = 3) -> List[str]:
        """Retrieve similar past lessons"""
        try:
            if self.collection.count() == 0:
                return []
            
            query_emb = self.embedder.embed_documents([task_desc])[0]
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=min(n, self.collection.count())
            )
            
            if not results['metadatas'] or not results['metadatas'][0]:
                return []
            
            lessons = []
            for metadata, doc in zip(results['metadatas'][0], results['documents'][0]):
                score = metadata.get('score', 'N/A')
                task = metadata.get('task', 'Unknown task')
                lessons.append(f"[Score: {score}] {task}: {doc}")
            
            return lessons
            
        except Exception as e:
            st.warning(f"Could not retrieve lessons: {e}")
            return []
    
    def _prune_old_lessons(self):
        """Remove old lessons to stay within max_lessons limit"""
        try:
            max_lessons = self.config['max_lessons']
            current_count = self.collection.count()
            
            if current_count > max_lessons:
                # Get all items sorted by timestamp
                all_items = self.collection.get()
                if all_items['metadatas']:
                    # Sort by timestamp and remove oldest
                    items_with_time = [
                        (id_, meta.get('timestamp', ''))
                        for id_, meta in zip(all_items['ids'], all_items['metadatas'])
                    ]
                    items_with_time.sort(key=lambda x: x[1])
                    
                    # Remove oldest items
                    to_remove = items_with_time[:current_count - max_lessons]
                    ids_to_remove = [item[0] for item in to_remove]
                    
                    if ids_to_remove:
                        self.collection.delete(ids=ids_to_remove)
                        
        except Exception as e:
            st.warning(f"Could not prune old lessons: {e}")
    
    def export_memory(self) -> Dict[str, Any]:
        """Export all lessons for backup"""
        try:
            return {
                "version": "1.0",
                "export_date": datetime.now().isoformat(),
                "collection": self.collection.get()
            }
        except Exception as e:
            st.error(f"Could not export memory: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            return {
                "total_lessons": self.collection.count(),
                "collection_name": self.config['collection_name'],
                "max_lessons": self.config['max_lessons']
            }
        except Exception:
            return {"total_lessons": 0}
    
    def clear_memory(self) -> bool:
        """Delete all stored memories. Returns True on success."""
        try:
            self.collection.delete(where={})
            return True
        except Exception as e:
            st.error(f"Could not clear memory: {e}")
            return False
    
    def store_result(
        self,
        task_id: str,
        task_description: str,
        result: str
    ) -> None:
        """Store a completed task result (alias for save_lesson without score)."""
        self.save_lesson(
            task_desc=task_description,
            output=result,
            critic_feedback="",
            score=0.0
        )
    
    def query_similar(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict]:
        """Return top-n similar past results as dicts (alias for get_relevant_lessons)."""
        lessons = self.get_relevant_lessons(query, n_results)
        return [{"lesson": lesson} for lesson in lessons]
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Return count of stored items and collection size."""
        stats = self.get_stats()
        return {
            "items_stored": stats.get("total_lessons", 0),
            "collection_size": stats.get("total_lessons", 0),
        }


# ============================================================================
# AGENT FACTORY
# ============================================================================

class AgentFactory:
    """Create and manage agents"""
    
    def __init__(self, llm: ChatOllama, config: Dict[str, Any]):
        self.llm = llm
        self.config = config['agents']
    
    def create_planner(self) -> Agent:
        """Create planner agent"""
        return Agent(
            role="Strategic Planner",
            goal="Create clear, step-by-step plans for complex tasks",
            backstory=(
                "You are an experienced project manager and architect. "
                "You excel at breaking down big problems into actionable steps, "
                "identifying dependencies, and creating realistic timelines. "
                "You always consider past lessons and learnings."
            ),
            llm=self.llm,
            verbose=self.config['verbose'],
            allow_delegation=self.config['allow_delegation']
        )
    
    def create_researcher(self, enable_web_search: bool = False) -> Agent:
        """Create researcher agent"""
        tools = []
        if enable_web_search:
            try:
                tools.append(SerperDevTool())
            except Exception:
                st.warning("Web search tool not configured (SERPER_API_KEY missing)")
        
        return Agent(
            role="Senior Researcher",
            goal="Gather accurate, up-to-date information and documentation",
            backstory=(
                "You are a meticulous researcher who finds reliable facts, "
                "references, and best practices. You verify information from "
                "multiple sources and provide comprehensive research reports."
            ),
            tools=tools,
            llm=self.llm,
            verbose=self.config['verbose'],
            allow_delegation=self.config['allow_delegation']
        )
    
    def create_coder(self) -> Agent:
        """Create coder agent"""
        return Agent(
            role="Senior Full-Stack Developer",
            goal="Write clean, well-structured, functional, and tested code",
            backstory=(
                "You are an expert developer with 10+ years of experience. "
                "You write production-ready code following best practices, "
                "include proper error handling, add comments, and always "
                "consider security and performance. You write self-documenting "
                "code with clear variable names and structure."
            ),
            llm=self.llm,
            verbose=self.config['verbose'],
            allow_delegation=self.config['allow_delegation']
        )
    
    def create_tester(self) -> Agent:
        """Create tester agent"""
        return Agent(
            role="QA Engineer & Test Specialist",
            goal="Create comprehensive tests and identify edge cases",
            backstory=(
                "You are a quality assurance expert who thinks about what "
                "could go wrong. You write unit tests, integration tests, "
                "and suggest test scenarios. You're familiar with testing "
                "frameworks and best practices."
            ),
            llm=self.llm,
            verbose=self.config['verbose'],
            allow_delegation=self.config['allow_delegation']
        )
    
    def create_critic(self) -> Agent:
        """Create critic agent"""
        return Agent(
            role="Critical Reviewer & QA Lead",
            goal="Critically review outputs, score quality, and suggest improvements",
            backstory=(
                "You are a ruthless but fair code reviewer and QA lead. "
                "You score outputs on a scale of 1-10 based on: "
                "accuracy (3 pts), completeness (2 pts), code quality (2 pts), "
                "security (2 pts), and best practices (1 pt). "
                "You provide specific, actionable feedback. "
                "If code or APIs are involved, you suggest Keploy test commands. "
                "You're known for catching issues others miss."
            ),
            llm=self.llm,
            verbose=self.config['verbose'],
            allow_delegation=self.config['allow_delegation']
        )


# ============================================================================
# TASK FACTORY
# ============================================================================

class TaskFactory:
    """Create and manage tasks"""
    
    @staticmethod
    def create_plan_task(user_query: str, past_lessons: List[str], agent: Agent) -> Task:
        """Create planning task"""
        lessons_str = "\n".join(past_lessons) if past_lessons else "No previous lessons available."
        
        return Task(
            description=(
                f"Create a detailed step-by-step plan for the following request:\n\n"
                f"USER REQUEST: {user_query}\n\n"
                f"PAST LESSONS (apply if relevant):\n{lessons_str}\n\n"
                f"Your plan should:\n"
                f"1. Break the task into clear, numbered steps\n"
                f"2. Specify which agent should handle each step (Researcher, Coder, Tester)\n"
                f"3. Identify dependencies between steps\n"
                f"4. Consider potential challenges and mitigation strategies\n"
                f"5. Apply relevant lessons from past attempts\n\n"
                f"Output format: Numbered plan with clear agent assignments and rationale."
            ),
            expected_output="Detailed numbered plan with agent assignments and dependencies",
            agent=agent
        )
    
    @staticmethod
    def create_research_task(plan: str, agent: Agent) -> Task:
        """Create research task"""
        return Task(
            description=(
                f"Based on this plan:\n{plan}\n\n"
                f"Perform necessary research:\n"
                f"1. Identify what information is needed\n"
                f"2. Find relevant documentation, best practices, examples\n"
                f"3. Verify information from multiple sources when possible\n"
                f"4. Summarize key findings\n\n"
                f"If no research is needed, state: 'No research needed - sufficient context available'\n"
            ),
            expected_output="Research findings summary or 'No research needed'",
            agent=agent
        )
    
    @staticmethod
    def create_code_task(plan: str, research: str, agent: Agent) -> Task:
        """Create coding task"""
        return Task(
            description=(
                f"PLAN:\n{plan}\n\n"
                f"RESEARCH:\n{research}\n\n"
                f"Implement the solution:\n"
                f"1. Write clean, well-structured code\n"
                f"2. Include proper error handling\n"
                f"3. Add comments for complex logic\n"
                f"4. Follow language-specific best practices\n"
                f"5. Include usage examples if applicable\n"
                f"6. Consider security and performance\n\n"
                f"Provide:\n"
                f"- Complete, runnable code\n"
                f"- Brief explanation of key decisions\n"
                f"- Any assumptions made\n"
            ),
            expected_output="Complete code implementation with explanation",
            agent=agent
        )
    
    @staticmethod
    def create_test_task(code: str, agent: Agent) -> Task:
        """Create testing task"""
        return Task(
            description=(
                f"CODE TO TEST:\n{code}\n\n"
                f"Create comprehensive tests:\n"
                f"1. Write unit tests for key functions\n"
                f"2. Test edge cases and error conditions\n"
                f"3. Include integration test scenarios\n"
                f"4. Suggest manual testing steps\n"
                f"5. If APIs are involved, suggest Keploy recording commands\n\n"
                f"Provide:\n"
                f"- Test code (using appropriate framework)\n"
                f"- List of test scenarios covered\n"
                f"- Any additional testing recommendations\n"
            ),
            expected_output="Test code and testing recommendations",
            agent=agent
        )
    
    @staticmethod
    def create_critic_task(all_outputs: str, agent: Agent) -> Task:
        """Create critic/review task"""
        return Task(
            description=(
                f"REVIEW ALL OUTPUTS:\n{all_outputs}\n\n"
                f"Provide a critical review:\n\n"
                f"1. SCORE (1-10):\n"
                f"   - Accuracy (3 pts): Is the solution correct?\n"
                f"   - Completeness (2 pts): Does it fully address the request?\n"
                f"   - Code Quality (2 pts): Is it clean and maintainable?\n"
                f"   - Security (2 pts): Are there security concerns?\n"
                f"   - Best Practices (1 pt): Does it follow standards?\n\n"
                f"2. STRENGTHS: What was done well?\n\n"
                f"3. WEAKNESSES: What issues exist?\n\n"
                f"4. IMPROVEMENTS: Specific suggestions to fix issues\n\n"
                f"5. KEPLOY TESTING: If code/APIs are involved, provide specific commands:\n"
                f"   Example: keploy record --cmd 'python app.py' --port 8000\n\n"
                f"6. VERDICT: If score < 8, state 'REPLAN NEEDED' with reasons\n\n"
                f"Be thorough but fair. Focus on actionable feedback."
            ),
            expected_output="Structured critic report with score and specific feedback",
            agent=agent
        )


# ============================================================================
# SWARM ORCHESTRATOR
# ============================================================================

class SwarmOrchestrator:
    """Orchestrate the multi-agent workflow"""
    
    def __init__(
        self,
        llm_manager: LLMManager,
        memory_manager: MemoryManager,
        config: Dict[str, Any]
    ):
        self.llm_manager = llm_manager
        self.memory = memory_manager
        self.config = config
        self.agent_factory = AgentFactory(llm_manager.llm, config)
        
    def execute(
        self,
        user_query: str,
        enable_web_search: bool = False,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Execute the swarm workflow"""
        
        # Create agents
        planner = self.agent_factory.create_planner()
        researcher = self.agent_factory.create_researcher(enable_web_search)
        coder = self.agent_factory.create_coder()
        tester = self.agent_factory.create_tester()
        critic = self.agent_factory.create_critic()
        
        best_result = None
        best_score = 0
        
        for iteration in range(max_iterations):
            try:
                st.info(f"🔄 Iteration {iteration + 1}/{max_iterations}")
                
                # Get relevant lessons
                past_lessons = self.memory.get_relevant_lessons(user_query)
                
                # Create tasks
                plan_task = TaskFactory.create_plan_task(user_query, past_lessons, planner)
                
                # Execute planning first
                st.write("📋 Planning...")
                plan_crew = Crew(
                    agents=[planner],
                    tasks=[plan_task],
                    process=Process.sequential,
                    verbose=False
                )
                plan_result = plan_crew.kickoff()
                plan_output = str(plan_result)
                
                # Research
                st.write("🔍 Researching...")
                research_task = TaskFactory.create_research_task(plan_output, researcher)
                research_crew = Crew(
                    agents=[researcher],
                    tasks=[research_task],
                    process=Process.sequential,
                    verbose=False
                )
                research_result = research_crew.kickoff()
                research_output = str(research_result)
                
                # Code
                st.write("💻 Coding...")
                code_task = TaskFactory.create_code_task(plan_output, research_output, coder)
                code_crew = Crew(
                    agents=[coder],
                    tasks=[code_task],
                    process=Process.sequential,
                    verbose=False
                )
                code_result = code_crew.kickoff()
                code_output = str(code_result)
                
                # Test
                st.write("🧪 Testing...")
                test_task = TaskFactory.create_test_task(code_output, tester)
                test_crew = Crew(
                    agents=[tester],
                    tasks=[test_task],
                    process=Process.sequential,
                    verbose=False
                )
                test_result = test_crew.kickoff()
                test_output = str(test_result)
                
                # Critic review
                st.write("⚖️ Reviewing...")
                all_outputs = f"PLAN:\n{plan_output}\n\nRESEARCH:\n{research_output}\n\nCODE:\n{code_output}\n\nTESTS:\n{test_output}"
                critic_task = TaskFactory.create_critic_task(all_outputs, critic)
                critic_crew = Crew(
                    agents=[critic],
                    tasks=[critic_task],
                    process=Process.sequential,
                    verbose=False
                )
                critic_result = critic_crew.kickoff()
                critic_output = str(critic_result)
                
                # Extract score
                score = self._extract_score(critic_output)
                
                # Save to memory
                self.memory.save_lesson(user_query, all_outputs, critic_output, score)
                
                # Track best result
                if score > best_score:
                    best_score = score
                    best_result = {
                        'plan': plan_output,
                        'research': research_output,
                        'code': code_output,
                        'tests': test_output,
                        'critique': critic_output,
                        'score': score,
                        'iteration': iteration + 1
                    }
                
                # Check if we should stop
                if score >= 8:
                    st.success(f"✅ High quality output achieved (Score: {score}/10)")
                    break
                elif iteration < max_iterations - 1:
                    st.warning(f"⚠️ Score: {score}/10. Retrying with feedback...")
                
            except Exception as e:
                st.error(f"Error in iteration {iteration + 1}: {str(e)}")
                if best_result is None and iteration == max_iterations - 1:
                    raise
        
        return best_result or {
            'error': 'All iterations failed',
            'score': 0
        }
    
    def _extract_score(self, critic_output: str) -> float:
        """Extract numeric score from critic output"""
        try:
            # Look for patterns like "Score: 8/10" or "8/10" or "SCORE: 8"
            import re
            patterns = [
                r'score[:\s]+(\d+(?:\.\d+)?)\s*/\s*10',
                r'(\d+(?:\.\d+)?)\s*/\s*10',
                r'score[:\s]+(\d+(?:\.\d+)?)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, critic_output.lower())
                if match:
                    return float(match.group(1))
            
            return 5.0  # Default mid-score if not found
            
        except Exception:
            return 5.0


# ============================================================================
# SETUP WIZARD
# ============================================================================

def setup_wizard():
    """First-time setup wizard"""
    st.title("🛠️ Forge Swarm Setup Wizard")
    
    st.write("Let's check your system and get everything ready...")
    
    # Check Ollama
    with st.spinner("Checking Ollama..."):
        ollama_ok, ollama_msg = SystemChecker.check_ollama()
    
    if ollama_ok:
        st.success(f"✅ {ollama_msg}")
    else:
        st.error(f"❌ {ollama_msg}")
        st.code("# Start Ollama with:\nollama serve")
        return False
    
    # Check models
    config = Config.load()
    llm_model = config['llm']['model']
    emb_model = config['embeddings']['model']
    
    with st.spinner(f"Checking model: {llm_model}..."):
        llm_ok, llm_msg = SystemChecker.check_model(llm_model)
    
    if llm_ok:
        st.success(f"✅ {llm_msg}")
    else:
        st.error(f"❌ {llm_msg}")
        if st.button(f"Pull {llm_model} now (this may take a while)"):
            with st.spinner("Downloading model..."):
                try:
                    subprocess.run(['ollama', 'pull', llm_model], check=True)
                    st.success("Model downloaded!")
                    st.rerun()
                except Exception:
                    st.error("Failed to download model. Please run manually.")
        return False
    
    with st.spinner(f"Checking embeddings model: {emb_model}..."):
        emb_ok, emb_msg = SystemChecker.check_model(emb_model)
    
    if emb_ok:
        st.success(f"✅ {emb_msg}")
    else:
        st.error(f"❌ {emb_msg}")
        if st.button(f"Pull {emb_model} now"):
            with st.spinner("Downloading embeddings model..."):
                try:
                    subprocess.run(['ollama', 'pull', emb_model], check=True)
                    st.success("Embeddings model downloaded!")
                    st.rerun()
                except Exception:
                    st.error("Failed to download model. Please run manually.")
        return False
    
    # Test LLM connection
    with st.spinner("Testing LLM connection..."):
        try:
            llm_manager = LLMManager(config)
            test_ok, test_msg = llm_manager.test_connection()
            if test_ok:
                st.success(f"✅ {test_msg}")
            else:
                st.error(f"❌ {test_msg}")
                return False
        except Exception as e:
            st.error(f"❌ LLM test failed: {e}")
            return False
    
    st.success("🎉 All systems ready! Click 'Continue to App' below.")
    
    if st.button("Continue to App", type="primary"):
        st.session_state.setup_complete = True
        st.rerun()
    
    return True


# ============================================================================
# MAIN UI
# ============================================================================

def main():
    """Main application"""
    
    # Load config
    config = Config.load()
    
    # Page config
    st.set_page_config(
        page_title=config['ui']['page_title'],
        page_icon=config['ui']['page_icon'],
        layout=config['ui']['layout']
    )
    
    # Check if setup is needed
    if 'setup_complete' not in st.session_state:
        ollama_ok, _ = SystemChecker.check_ollama()
        llm_ok, _ = SystemChecker.check_model(config['llm']['model'])
        
        if not (ollama_ok and llm_ok):
            setup_wizard()
            return
        else:
            st.session_state.setup_complete = True
    
    # Initialize managers (cached)
    if 'llm_manager' not in st.session_state:
        st.session_state.llm_manager = LLMManager(config)
    
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = MemoryManager(
            config,
            st.session_state.llm_manager.embedder
        )
    
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = SwarmOrchestrator(
            st.session_state.llm_manager,
            st.session_state.memory_manager,
            config
        )
    
    # Header
    st.title("🤖 Forge Swarm")
    st.caption("100% Local • Privacy-First • Self-Improving Multi-Agent AI")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # System Status Panel
        st.subheader("🔍 System Status")
        checks = SystemChecker.run_all_checks(config)
        
        ollama_status = "✅" if checks["ollama"][0] else "❌"
        model_status = "✅" if checks["model"][0] else "❌"
        emb_status = "✅" if checks["embeddings"][0] else "❌"
        chromadb_status = "✅" if checks["chromadb"][0] else "❌"
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Ollama:** {ollama_status}")
            st.markdown(f"**Model:** {model_status}")
        with col2:
            st.markdown(f"**Embeddings:** {emb_status}")
            st.markdown(f"**ChromaDB:** {chromadb_status}")
        
        # Model selector
        st.divider()
        st.subheader("🤖 Model Settings")
        model_input = st.text_input(
            "LLM Model",
            value=config['llm']['model'],
            help="Ollama model to use"
        )
        if model_input != config['llm']['model']:
            config['llm']['model'] = model_input
            st.rerun()
        
        # Memory stats
        st.divider()
        st.subheader("💾 Memory")
        stats = st.session_state.memory_manager.get_stats()
        st.markdown(f"**Items Stored:** {stats.get('total_lessons', 0)}")
        st.markdown(f"**Collection:** {stats.get('collection_name', 'N/A')}")
        
        # Clear Memory with confirmation
        if st.button("🗑️ Clear Memory"):
            st.session_state.show_clear_confirm = True
        
        if st.session_state.get("show_clear_confirm", False):
            st.warning("Clear all memories? This cannot be undone.")
            col_y, col_n = st.columns(2)
            with col_y:
                if st.button("Yes, Clear", type="primary"):
                    st.session_state.memory_manager.clear_memory()
                    st.session_state.show_clear_confirm = False
                    st.success("Memory cleared!")
                    st.rerun()
            with col_n:
                if st.button("Cancel"):
                    st.session_state.show_clear_confirm = False
                    st.rerun()
        
        st.divider()
        
        # Settings
        st.subheader("⚡ Execution Settings")
        enable_web_search = st.checkbox("Enable Web Search", value=False)
        max_iterations = st.slider("Max Retry Attempts", 1, 5, 3)
        
        st.divider()
        
        # Templates
        st.subheader("📝 Quick Start Templates")
        
        templates = {
            "FastAPI CRUD App": "Create a FastAPI application with User CRUD operations, SQLite database, Pydantic validation, proper error handling, and pytest tests.",
            "Data Pipeline": "Build a data processing pipeline that reads CSV files, cleans missing values, performs statistical analysis, generates visualizations, and exports results to JSON.",
            "Discord Bot": "Create a Discord bot with /hello, /joke, and /weather commands using discord.py, with proper error handling and help documentation.",
            "Web Scraper": "Build a web scraper that extracts product information from an e-commerce site, saves to CSV, handles pagination, and includes rate limiting.",
            "CLI Tool": "Create a command-line tool using Click/Typer with multiple commands, configuration file support, and comprehensive help documentation."
        }
        
        selected_template = st.selectbox("Choose a template", ["Custom"] + list(templates.keys()))
        
        if selected_template != "Custom":
            if st.button("Use This Template"):
                st.session_state.template_text = templates[selected_template]
        
        st.divider()
        
        if st.button("🔧 Run Setup Again"):
            if 'setup_complete' in st.session_state:
                del st.session_state.setup_complete
            st.rerun()
        
        if st.button("💾 Export Memory"):
            memory_data = st.session_state.memory_manager.export_memory()
            st.download_button(
                "Download Backup",
                data=json.dumps(memory_data, indent=2),
                file_name=f"forge_swarm_memory_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        # About section
        st.divider()
        st.caption("**Forge Swarm v1.0**")
        st.caption("100% Local • Privacy-First")
        st.caption("Powered by Ollama + CrewAI")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    default_value = st.session_state.get('template_text', '')
    if 'template_text' in st.session_state:
        del st.session_state.template_text
    
    if prompt := st.chat_input("What should the swarm build?", key="user_input"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Execute swarm
        with st.chat_message("assistant"):
            with st.status("🔄 Swarm working...", expanded=True) as status:
                try:
                    result = st.session_state.orchestrator.execute(
                        prompt,
                        enable_web_search=enable_web_search,
                        max_iterations=max_iterations
                    )
                    
                    if 'error' in result:
                        status.update(label="❌ Failed", state="error")
                        response = f"**Error**: {result['error']}"
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        status.update(label="✅ Complete!", state="complete")
                        
                        # Get memory context used
                        memory_context = st.session_state.memory_manager.get_relevant_lessons(prompt)
                        memory_context_str = "\n".join(memory_context) if memory_context else "No prior context found."
                        
                        # Build agent log
                        agent_log = f"""## 📋 Plan (Iteration {result['iteration']})
{result['plan']}

## 🔍 Research
{result['research']}

## 🧪 Tests
{result['tests']}

## ⚖️ Quality Review (Score: {result['score']}/10)
{result['critique']}
"""
                        
                        # Tabbed output
                        tab1, tab2, tab3 = st.tabs(["💻 Final Code", "📊 Agent Log", "🧠 Memory Context"])
                        
                        with tab1:
                            st.markdown(f"### 🎯 Result (Score: {result['score']}/10)")
                            st.markdown("#### 💻 Code")
                            st.code(result['code'], language="python")
                            
                            # Copy to clipboard button
                            if st.button("📋 Copy Code", key=f"copy_code_{len(st.session_state.messages)}"):
                                st.code(result['code'])
                                st.success("Code displayed above - select and copy manually")
                        
                        with tab2:
                            st.markdown(agent_log)
                        
                        with tab3:
                            st.markdown("### 🧠 Memory Context Used")
                            st.markdown(memory_context_str)
                        
                        # Store formatted response for chat history
                        summary_response = f"### 🎯 Result (Iteration {result['iteration']}, Score: {result['score']}/10)\n\n**Code:**\n```python\n{result['code'][:500]}...\n```"
                        st.session_state.messages.append({"role": "assistant", "content": summary_response})
                    
                except Exception as e:
                    status.update(label="❌ Error", state="error")
                    error_msg = f"**Error occurred:**\n\n```\n{str(e)}\n```\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Show template value if set
    elif default_value:
        st.info(f"💡 Template loaded: {selected_template}")
        st.text_area("Template content (edit if needed):", value=default_value, height=150, key="template_display")
        if st.button("Submit Template"):
            st.session_state.template_text = st.session_state.template_display
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("💡 **Tips:** Start with small tasks first. Make sure Ollama is running. Check sidebar for templates.")


if __name__ == "__main__":
    main()
