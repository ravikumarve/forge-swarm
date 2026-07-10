"""Forge Swarm — Task Orchestrator & Swarm Coordinator."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st

from forge_swarm_core.core import Config
from forge_swarm_core.agents import AgentFactory, CriticParser, TaskFactory
from forge_swarm_core.memory import MemoryManager


class SwarmOrchestrator:
    """Orchestrate the multi-agent workflow"""

    def __init__(
        self,
        llm_manager: LLMManager,
        memory_manager: MemoryManager,
        config: Dict[str, Any],
    ):
        self.llm_manager = llm_manager
        self.memory = memory_manager
        self.config = config
        self.agent_factory = AgentFactory(llm_manager.llm, config)

    def execute(
        self, user_query: str, enable_web_search: bool = False, max_iterations: int = 3
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
                plan_task = TaskFactory.create_plan_task(
                    user_query, past_lessons, planner
                )

                # Execute planning first
                st.write("📋 Planning...")
                plan_crew = Crew(
                    agents=[planner],
                    tasks=[plan_task],
                    process=Process.sequential,
                    verbose=False,
                )
                plan_result = plan_crew.kickoff()
                plan_output = str(plan_result)

                # Research
                st.write("🔍 Researching...")
                research_task = TaskFactory.create_research_task(
                    plan_output, researcher
                )
                research_crew = Crew(
                    agents=[researcher],
                    tasks=[research_task],
                    process=Process.sequential,
                    verbose=False,
                )
                research_result = research_crew.kickoff()
                research_output = str(research_result)

                # Code
                st.write("💻 Coding...")
                code_task = TaskFactory.create_code_task(
                    plan_output, research_output, coder
                )
                code_crew = Crew(
                    agents=[coder],
                    tasks=[code_task],
                    process=Process.sequential,
                    verbose=False,
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
                    verbose=False,
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
                    verbose=False,
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
                        "plan": plan_output,
                        "research": research_output,
                        "code": code_output,
                        "tests": test_output,
                        "critique": critic_output,
                        "score": score,
                        "iteration": iteration + 1,
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

        return best_result or {"error": "All iterations failed", "score": 0}

    def _extract_score(self, critic_output: str) -> float:
        """Extract numeric score from critic output"""
        try:
            # Look for patterns like "Score: 8/10" or "8/10" or "SCORE: 8"
            import re

            patterns = [
                r"score[:\s]+(\d+(?:\.\d+)?)\s*/\s*10",
                r"(\d+(?:\.\d+)?)\s*/\s*10",
                r"score[:\s]+(\d+(?:\.\d+)?)",
            ]

            for pattern in patterns:
                match = re.search(pattern, critic_output.lower())
                if match:
                    return float(match.group(1))

            return 5.0  # Default mid-score if not found

        except Exception:
            return 5.0

def parse_multi_file_output(raw_output: str) -> Dict[str, str]:
    """Parse '=== FILE: <path> ===' markers from agent output into a dict.

    Returns {filename: content, ...}. Falls back to {"output.py": raw_output}
    if no FILE markers are found.
    """
    import re
    pattern = r'=== FILE:\s+(.+?)\s*===\s*\n(.*?)(?=\n=== FILE:\s|\Z)'
    matches = re.findall(pattern, raw_output, re.DOTALL)
    if matches:
        files = {}
        for filename, content in matches:
            files[filename.strip()] = content.strip()
        return files
    # Fallback: wrap entire output as a single file
    return {"output.py": raw_output.strip()}

class TaskOrchestrator:
    """Orchestrates task creation and crew execution with retry loop."""

    def __init__(self, agents: Dict[str, "Agent"], config: Dict[str, Any]):
        self.agents = agents
        self.config = config

    def build_tasks(self, user_request: str, context: str = "") -> "list[Any]":
        """Create ordered task list from user request."""
        _Agent, _Task, _Crew, _Process = _crewai()
        tasks = []

        # Planning task
        plan_task = _Task(
            description=(
                f"Create a detailed step-by-step plan for:\n\n{user_request}\n\n"
                f"Context:\n{context}\n\n"
                f"Output format: numbered tasks, each with input, output, and acceptance criteria."
            ),
            expected_output="Numbered plan with acceptance criteria",
            agent=self.agents["planner"],
        )
        tasks.append(plan_task)

        # Research task
        research_task = _Task(
            description=(
                f"Based on the plan, research implementation patterns.\n"
                f"Include: recommended approach, alternatives, top 3 gotchas, one non-obvious insight."
            ),
            expected_output="Research brief with patterns and pitfalls",
            agent=self.agents["researcher"],
        )
        tasks.append(research_task)

        # Coding task — multi-file output
        code_task = _Task(
            description=(
                f"Write complete, production-grade code for:\n\n{user_request}\n\n"
                f"No placeholders. No TODOs. No magic numbers. Use type hints.\n\n"
                f"IMPORTANT: Structure your output as MULTIPLE FILES using this exact format:\n"
                f"=== FILE: <filename> ===\n"
                f"<file content>\n\n"
                f"=== FILE: <another_filename> ===\n"
                f"<file content>\n\n"
                f"Separate each file with '=== FILE: filename ===' markers.\n"
                f"Include files like: main.py (or app.py), models.py, routes.py if applicable,\n"
                f"requirements.txt, README.md, .env.example, and any config files.\n"
                f"Make it a complete, runnable project."
            ),
            expected_output="Multi-file project code with === FILE: markers",
            agent=self.agents["coder"],
        )
        tasks.append(code_task)

        # Testing task
        test_task = _Task(
            description=(
                f"Write pytest test suite covering: happy path, sad path, evil path.\n"
                f"Include edge cases: None, empty strings, huge numbers, unicode."
            ),
            expected_output="Complete test suite",
            agent=self.agents["tester"],
        )
        tasks.append(test_task)

        # Critic task
        critic_task = _Task(
            description=(
                f"Review all output and score quality 1-10.\n"
                f"Output format MUST be:\n"
                f"SCORE: X/10\n"
                f"VERDICT: APPROVED / REVISION REQUIRED\n"
                f"ISSUES: [bulleted list]\n"
                f"REQUIRED CHANGES: [if REVISION REQUIRED]"
            ),
            expected_output="SCORE, VERDICT, ISSUES, REQUIRED CHANGES",
            agent=self.agents["critic"],
        )
        tasks.append(critic_task)

        return tasks

    def run(self, user_request: str, context: str = "") -> Dict[str, Any]:
        """
        Execute the crew with retry loop based on Critic score.

        Returns:
            Dict with keys: final_code (str), critic_result (dict),
            iterations (int), agent_log (str)
        """
        # ⚡ Lazy-import crewai runtime classes on first pipeline execution
        _Agent, _Task, _Crew, _Process = _crewai()

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
            crew = _Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=_Process.sequential,
                verbose=True,
            )

            try:
                result = crew.kickoff()
                raw_output = str(result)
                critic_data = CriticParser.parse(raw_output)
                agent_log.append(f"📊 Critic score: {critic_data['score']}/10")

                # Parse multi-file output
                files = parse_multi_file_output(raw_output)

                last_result = {
                    "final_code": raw_output,
                    "files": files,
                    "file_list": sorted(files.keys()) if files else [],
                    "critic_result": critic_data,
                    "iterations": iteration,
                    "agent_log": "\n".join(agent_log),
                }
            except Exception as e:
                agent_log.append(f"❌ Error: {str(e)}")
                last_result = {
                    "final_code": "",
                    "critic_result": {
                        "score": 0,
                        "verdict": "ERROR",
                        "approved": False,
                        "issues": [str(e)],
                    },
                    "iterations": iteration,
                    "agent_log": "\n".join(agent_log),
                }
                break

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