"""Forge Swarm — Agent Factory & Definitions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from forge_swarm_core.core import Config
from forge_swarm_core.llm import LLMProvider


class AgentStatusDisplay:
    """Renders real-time agent pipeline status in Streamlit."""

    AGENTS = [
        ("01", "Planner", "System architecture and mission mapping"),
        ("02", "Researcher", "Deep documentation and web search analysis"),
        ("03", "Coder", "Production-ready implementation entirely offline"),
        ("04", "Tester", "Unit testing and logic verification"),
        ("05", "Critic", "Self-improvement loop scoring (8/10 threshold)"),
    ]

    @staticmethod
    def render_pipeline(current_agent_idx: int = -1) -> None:
        """Render all 5 agents as status cards."""
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div class="section-tag">COGNITIVE_PIPELINE</div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(5)
        for i, (num, name, desc) in enumerate(AgentStatusDisplay.AGENTS):
            with cols[i]:
                if current_agent_idx == -1:
                    dot_class, card_class = "idle", "state-idle"
                elif i < current_agent_idx:
                    dot_class, card_class = "done", "state-done"
                elif i == current_agent_idx:
                    dot_class, card_class = "active", "state-active"
                else:
                    dot_class, card_class = "idle", "state-idle"
                
                st.markdown(
                    f'<div class="glass-card {card_class}" style="text-align: center;">'
                    f'  <div style="font-family: JetBrains Mono, monospace; font-size: 9px; color: rgba(255,255,255,0.4); margin-bottom: 12px;">{num}_{name.upper()}</div>'
                    f'  <div class="status-dot {dot_class}" style="margin: 0 auto 8px auto;"></div>'
                    f'  <div style="font-family: Space Grotesk, sans-serif; font-size: 14px; font-weight: 700; margin-bottom: 4px;">{name}</div>'
                    f'  <div style="font-size: 10px; color: rgba(255,255,255,0.4); line-height: 1.4;">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    @staticmethod
    def render_score(score: int, verdict: str) -> None:
        """Render critic score badge with LP2 styling."""
        if score >= 8:
            color = "#00ff41"
            glow = "0 0 20px rgba(0, 255, 65, 0.3)"
        elif score >= 6:
            color = "#f0ff00"
            glow = "0 0 20px rgba(240, 255, 0, 0.2)"
        else:
            color = "#ff00ff"
            glow = "0 0 20px rgba(255, 0, 255, 0.3)"
        
        st.markdown(
            f'<div style="margin: 16px 0; padding: 16px; background: rgba(255,255,255,0.02); '
            f'border: 1px solid {color}; border-radius: 4px; text-align: center; box-shadow: {glow};">'
            f'  <div style="font-family: JetBrains Mono, monospace; font-size: 10px; color: rgba(255,255,255,0.4); margin-bottom: 8px; letter-spacing: 0.2em;">CRITIC SCORE</div>'
            f'  <div style="font-family: Space Grotesk, sans-serif; font-size: 48px; font-weight: 700; color: {color}; line-height: 1;">{score}<span style="font-size: 18px; opacity: 0.6;">/10</span></div>'
            f'  <div style="font-family: JetBrains Mono, monospace; font-size: 11px; color: {color}; margin-top: 8px; letter-spacing: 0.1em; text-transform: uppercase;">{verdict}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

class AgentFactory:
    """Create and manage agents"""

    def __init__(self, llm: LLMProvider, config: Dict[str, Any]):
        self.llm = llm
        self.config = config["agents"]

    def create_planner(self) -> "Agent":
        """Create planner agent - Strategic Engineering Lead"""
        _Agent, _, _, _ = _crewai()
        return _Agent(
            role="Strategic Engineering Lead",
            goal="Decompose any coding request into a precise, dependency-ordered execution plan with clear acceptance criteria per subtask.",
            backstory=(
                "15 years shipping production systems across fintech, healthcare, and SaaS. "
                "Has a pathological hatred of ambiguity. Every plan you write must answer: "
                "What are we building? What does done look like? What can go wrong? "
                "You think in trees — break the root problem into branches, branches into leaves. "
                "Output format: numbered tasks, each with input, output, and acceptance criteria."
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_researcher(self, enable_web_search: bool = False) -> "Agent":
        """Create researcher agent - Principal Technical Researcher"""
        _Agent, _, _, _ = _crewai()
        tools = []
        if enable_web_search:
            _SerperDevTool, _available = _crewai_tools()
            if _available:
                try:
                    tools.append(_SerperDevTool())
                except Exception:
                    pass

        return _Agent(
            role="Principal Technical Researcher",
            goal="Produce a concise, high-signal research brief covering the best implementation patterns, known pitfalls, and idiomatic approaches for the task.",
            backstory=(
                "Obsessive reader of RFCs, PEPs, source code, and engineering blogs. "
                "Knows when to use a library vs roll your own. Hates cargo-culting. "
                "Every research brief must include: recommended approach, alternatives considered, "
                "top 3 gotchas, and one non-obvious insight the coder would miss."
            ),
            tools=tools,
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_coder(self) -> "Agent":
        """Create coder agent - Senior Software Craftsperson"""
        _Agent, _, _, _ = _crewai()
        return _Agent(
            role="Senior Software Craftsperson",
            goal="Write complete, production-grade, immediately runnable code based on the plan and research brief. No placeholders. No TODOs without tracking. No magic numbers.",
            backstory=(
                "Treats code like prose. Every function has one job. Every variable name "
                "tells a story. Uses type hints everywhere. Writes comments that explain "
                "WHY, not WHAT. Has strong opinions: explicit > implicit, simple > clever, "
                "boring > exciting. Will refuse to ship code that 'works but is embarrassing.'"
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_tester(self) -> "Agent":
        """Create tester agent - Adversarial QA Engineer"""
        _Agent, _, _, _ = _crewai()
        return _Agent(
            role="Adversarial QA Engineer",
            goal="Write a complete test suite that tries to break the code before production does.",
            backstory=(
                "Broke prod 3 times early in career. Now sees failure modes everywhere. "
                "Writes tests in three categories: "
                "1. Happy path — does it work when everything is correct? "
                "2. Sad path — does it fail gracefully when inputs are wrong? "
                "3. Evil path — what happens with None, empty strings, huge numbers, unicode? "
                "Uses pytest. Aims for 80%+ coverage. Names tests like documentation."
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_critic(self) -> "Agent":
        """Create critic agent - Principal Engineer & Gatekeeper"""
        _Agent, _, _, _ = _crewai()
        return _Agent(
            role="Principal Engineer & Gatekeeper",
            goal="Score the complete output (code + tests) on a scale of 1-10 with surgical specificity. Approve if score >= 8. Request targeted revisions if below.",
            backstory=(
                "Zero tolerance for mediocrity. Has reviewed 10,000+ PRs. Scores on: "
                "- Correctness (does it actually work?) "
                "- Readability (can a junior follow it?) "
                "- Robustness (does it handle edge cases?) "
                "- Idiomatic style (is it Pythonic?) "
                "- Test coverage (are the tests meaningful?) "
                "Output format MUST be: "
                "SCORE: X/10 "
                "VERDICT: APPROVED / REVISION REQUIRED "
                "ISSUES: [bulleted list of specific line-level issues] "
                "REQUIRED CHANGES: [only if REVISION REQUIRED]"
            ),
            llm=self.llm,
            verbose=self.config["verbose"],
            allow_delegation=self.config["allow_delegation"],
        )

    def create_all(self) -> Dict[str, "Agent"]:
        """Create all agents, return as named dict."""
        return {
            "planner": self.create_planner(),
            "researcher": self.create_researcher(),
            "coder": self.create_coder(),
            "tester": self.create_tester(),
            "critic": self.create_critic(),
        }

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

class TaskFactory:
    """Create and manage tasks"""

    @staticmethod
    def create_plan_task(
        user_query: str, past_lessons: List[str], agent: Agent
    ) -> Task:
        """Create planning task"""
        lessons_str = (
            "\n".join(past_lessons)
            if past_lessons
            else "No previous lessons available."
        )

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
            agent=agent,
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
            agent=agent,
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
            agent=agent,
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
            agent=agent,
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
            agent=agent,
        )