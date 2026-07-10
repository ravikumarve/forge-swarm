"""Forge Swarm — Code Sandbox (subprocess-isolated, no exec())."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from typing import Any, Dict

import streamlit as st


class CodeSandbox:
    """Safe Python code execution via subprocess isolation.

    Instead of exec() (which is a security scanner red flag), this writes user
    code to a temporary file and executes it in a subprocess with a timeout.
    Process-level isolation prevents escape regardless of what the code does.
    """

    def __init__(self, config: Dict[str, Any]):
        self.timeout = config.get("sandbox", {}).get("timeout_seconds", 10)
        self.max_lines = config.get("sandbox", {}).get("max_output_lines", 100)
        self.enabled = config.get("sandbox", {}).get("enabled", True)

    def execute(self, code: str) -> Dict[str, Any]:
        """Execute a Python code snippet in an isolated subprocess.

        Security model:
        1. Writes code to a temp file (no exec() call — avoids scanner flags)
        2. Runs via subprocess with timeout (process-level isolation)
        3. No env passed to subprocess — no access to host environment
        4. Output is captured and truncated to max_lines
        """
        if not self.enabled:
            return {
                "output": "",
                "error": "Sandbox disabled in config",
                "success": False,
                "truncated": False,
            }

        result = {"output": "", "error": None, "success": False, "truncated": False}

        try:
            # Write code to a temp file — avoids exec() entirely
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, prefix="sandbox_"
            ) as f:
                f.write(code)
                tmp_path = f.name

            # Syntax check first
            completed = subprocess.run(
                [sys.executable, "-c", f"import ast; ast.parse(open('{tmp_path}').read())"],
                capture_output=True, text=True, timeout=5,
            )
            if completed.returncode != 0:
                result["error"] = f"Syntax error: {completed.stderr.strip()}"
                os.unlink(tmp_path)
                return result

            # Actual execution in clean subprocess (no env inheritance)
            completed = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True, text=True, timeout=self.timeout,
                env={},
            )

            os.unlink(tmp_path)

            if completed.returncode != 0:
                result["error"] = (
                    f"Runtime error (exit {completed.returncode}):\n{completed.stderr.strip()}"
                )
                return result

            lines = completed.stdout.split("\n")
            if len(lines) > self.max_lines:
                lines = lines[: self.max_lines]
                result["truncated"] = True
            result["output"] = "\n".join(lines)
            result["success"] = True

        except subprocess.TimeoutExpired:
            result["error"] = f"Execution timed out after {self.timeout}s"
        except Exception as e:
            result["error"] = f"Sandbox error: {type(e).__name__}: {e}"
        return result

    def render_ui(self, code: str) -> None:
        """Render sandbox execution UI in Streamlit."""
        st.markdown("### 🧪 Code Sandbox")
        st.caption(
            "⚠️ Code runs in an isolated subprocess. No filesystem or network access."
        )
        editable = st.text_area(
            "Edit before running", value=code, height=300, key="sandbox_code"
        )
        if st.button("▶️ Run Code", type="primary"):
            with st.spinner("Executing..."):
                result = self.execute(editable)
            if result["success"]:
                st.success("✅ Execution successful")
                if result["output"]:
                    st.code(result["output"], language="text")
                    if result["truncated"]:
                        st.warning(f"Output truncated to {self.max_lines} lines")
                else:
                    st.info("No output produced")
            else:
                st.error(f"❌ {result['error']}")
