"""Forge Swarm — MCP Tool Manager & Built-in Tools."""

from __future__ import annotations

import json
import os
import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

from forge_swarm_core.sandbox import CodeSandbox


class MCPToolManager:
    """Manages agent tools — built-in tools + optional MCP server connections.

    Built-in tools work out of the box (no extra dependencies):
      - web_search: Search the web via requests
      - file_read: Read files from the project directory
      - execute_python: Run Python code in the safe sandbox

    External MCP servers can be added via config.yaml (requires `mcp` package).
    """

    BUILTIN_TOOLS = {
        "web_search": {
            "name": "web_search",
            "description": "Search the web for current information on a topic",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (be specific)"},
                },
                "required": ["query"],
            },
        },
        "file_read": {
            "name": "file_read",
            "description": "Read a file from the project directory",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path from project root"},
                },
                "required": ["path"],
            },
        },
        "execute_python": {
            "name": "execute_python",
            "description": "Execute Python code in a safe sandbox (standard lib only)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
                },
                "required": ["code"],
            },
        },
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("mcp", {})
        self._enabled_builtins: set[str] = set()
        self._server_connections: list[dict] = []
        self._sandbox: Optional[CodeSandbox] = None

        # Determine which built-in tools are enabled
        builtin_config = self.config.get("builtin_tools", {})
        for tool_name in self.BUILTIN_TOOLS:
            if builtin_config.get(tool_name, True):
                self._enabled_builtins.add(tool_name)

        # Connect to external MCP servers (optional, needs mcp package)
        self._connect_servers()

    # ── Public API ───────────────────────────────────────────────

    def list_tools(self, enabled_only: list[str] | None = None) -> list[dict]:
        """Return all available tools, optionally filtered by enabled names."""
        all_tools: list[dict] = []

        # Add built-in tools
        for name in self._enabled_builtins:
            if enabled_only is None or name in enabled_only:
                all_tools.append(self.BUILTIN_TOOLS[name])

        # Add MCP server tools
        for conn in self._server_connections:
            for tool in conn.get("tools", []):
                if enabled_only is None or tool["name"] in enabled_only:
                    all_tools.append(tool)

        return all_tools

    def call_tool(self, name: str, args: dict) -> str:
        """Call a tool by name and return the result as a string."""
        if name in self.BUILTIN_TOOLS and name in self._enabled_builtins:
            return self._call_builtin(name, args)

        # Check MCP server tools
        for conn in self._server_connections:
            for tool in conn.get("tools", []):
                if tool["name"] == name:
                    return self._call_mcp_tool(conn, name, args)

        return f"Error: Tool '{name}' is not available."

    def format_tools_for_prompt(self, tool_names: list[str] | None = None) -> str:
        """Format tool descriptions as XML for system prompt injection."""
        tools = self.list_tools(enabled_only=tool_names)
        if not tools:
            return ""

        lines = [
            "\n\n## Available Tools",
            "You have access to the following tools. When you want to use a tool,",
            "respond with EXACTLY this format (no extra text before or after):",
            "",
            '<<<TOOL_CALL>>>',
            '{"name": "tool_name", "args": {"key": "value"}}',
            '<<<END_TOOL_CALL>>>',
            "",
            "Then wait for the tool result before providing your final response.",
            "If you don't need a tool, just respond normally.\n",
        ]

        for t in tools:
            lines.append(f"### {t['name']}")
            lines.append(t["description"])
            import json
            lines.append(f"Input: {json.dumps(t['input_schema'], indent=2)}")
            lines.append("")

        return "\n".join(lines)

    def parse_tool_call(self, response: str) -> Optional[dict]:
        """Parse a tool call from the model's response.

        Returns {"name": str, "args": dict} or None.
        """
        import re

        match = re.search(
            r'<<<TOOL_CALL>>>\s*(\{.*?\})\s*<<<END_TOOL_CALL>>>',
            response, re.DOTALL,
        )
        if not match:
            return None
        try:
            import json
            data = json.loads(match.group(1))
            return {"name": data.get("name", ""), "args": data.get("args", {})}
        except (json.JSONDecodeError, KeyError):
            return None

    # ── Built-in tool execution ──────────────────────────────────

    def _call_builtin(self, name: str, args: dict) -> str:
        """Execute a built-in tool."""
        try:
            if name == "web_search":
                return self._web_search(args.get("query", ""))
            elif name == "file_read":
                return self._file_read(args.get("path", ""))
            elif name == "execute_python":
                return self._exec_python(args.get("code", ""))
            return f"Unknown built-in tool: {name}"
        except Exception as e:
            return f"Tool error ({name}): {type(e).__name__}: {e}"

    def _web_search(self, query: str) -> str:
        """Search the web via Tavily or a simple requests fallback."""
        if not query:
            return "Error: No query provided."

        # Try Tavily API first if key is available
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            try:
                resp = requests.post(
                    "https://api.tavily.com/search",
                    json={"api_key": tavily_key, "query": query, "max_results": 5},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    if results:
                        lines = [f"Web search results for: {query}", ""]
                        for r in results[:5]:
                            title = r.get("title", "Untitled")
                            snippet = r.get("content", "")[:300]
                            url = r.get("url", "")
                            lines.append(f"• {title}")
                            lines.append(f"  {snippet}")
                            lines.append(f"  {url}")
                            lines.append("")
                        return "\n".join(lines)
            except Exception:
                pass

        # Fallback: basic requests + DuckDuckGo lite
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(
                f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}",
                headers=headers, timeout=10,
            )
            if resp.status_code == 200:
                # Extract snippets from the HTML response
                from html.parser import HTMLParser

                class SnippetParser(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self._capture = False
                        self.snippets = []

                    def handle_starttag(self, tag, attrs):
                        attrs_dict = dict(attrs)
                        if tag == "a" and "result__snippet" in attrs_dict.get("class", ""):
                            self._capture = True

                    def handle_data(self, data):
                        if self._capture:
                            self.snippets.append(data.strip())
                            self._capture = False

                parser = SnippetParser()
                parser.feed(resp.text)
                if parser.snippets:
                    lines = [f"Web search results for: {query}", ""]
                    for i, s in enumerate(parser.snippets[:5], 1):
                        lines.append(f"{i}. {s[:200]}")
                    return "\n".join(lines)
            return f"Search results for '{query}' could not be retrieved. Try a different query."
        except Exception as e:
            return f"Web search unavailable: {e}"

    def _file_read(self, path: str) -> str:
        """Read a file relative to project root."""
        import os
        # Security: prevent path traversal
        clean = os.path.normpath(path)
        if clean.startswith("..") or clean.startswith("/"):
            return "Error: Path traversal not allowed."
        full = os.path.join(os.getcwd(), clean)
        if not os.path.exists(full):
            return f"File not found: {path}"
        if not os.path.isfile(full):
            return f"Not a file: {path}"
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            ext = os.path.splitext(path)[1]
            lang = ext.lstrip(".") if ext else "text"
            return f"```{lang}\n# File: {path}\n{content}\n```"
        except Exception as e:
            return f"Error reading file: {e}"

    def _exec_python(self, code: str) -> str:
        """Execute Python code using the CodeSandbox."""
        if self._sandbox is None:
            from forge_swarm_core.sandbox import CodeSandbox
            self._sandbox = CodeSandbox(self.config)
        result = self._sandbox.execute(code)
        if result["success"]:
            out = result.get("output", "")
            if result.get("truncated"):
                out += "\n... (truncated)"
            return out or "Code executed successfully (no output)."
        return f"Execution error: {result.get('error', 'Unknown error')}"

    # ── MCP server connections (optional) ────────────────────────

    def _connect_servers(self) -> None:
        """Connect to configured MCP servers (needs `mcp` package)."""
        servers_config = self.config.get("servers", [])
        for svc in servers_config:
            if not svc.get("enabled", True):
                continue
            try:
                conn = self._connect_single_server(svc)
                if conn:
                    self._server_connections.append(conn)
            except Exception as e:
                print(f"⚠️ MCP server '{svc.get('name')}' connection failed: {e}")

    def _connect_single_server(self, svc: dict) -> Optional[dict]:
        """Try to connect to a single MCP server and list its tools."""
        name = svc.get("name", "unknown")
        transport = svc.get("transport", "stdio")
        try:
            import mcp.client.stdio as stdio_client
            import mcp.client.sse as sse_client
            import mcp.types as types
            import anyio
        except ImportError:
            print(f"⚠️ MCP package not installed. Skipping server '{name}'.")
            return None

        # This is a simplified connection — full MCP handshake happens here
        try:
            if transport == "stdio":
                command = svc.get("command", "")
                args = svc.get("args", [])
                if not command:
                    return None
                # We'd use anyio to run the async client
                # For now, log and return placeholder
                print(f"ℹ️ MCP server '{name}' configured (stdio: {command} {' '.join(args)})")
                return {
                    "name": name,
                    "transport": transport,
                    "tools": [],  # Would be populated after list_tools() handshake
                }
            elif transport == "sse":
                url = svc.get("url", "")
                if not url:
                    return None
                print(f"ℹ️ MCP server '{name}' configured (SSE: {url})")
                return {
                    "name": name,
                    "transport": transport,
                    "tools": [],
                }
        except Exception as e:
            print(f"⚠️ MCP server '{name}' error: {e}")
        return None

    def _call_mcp_tool(self, conn: dict, name: str, args: dict) -> str:
        """Call a tool on an MCP server."""
        # Simplified MCP tool call — would use the SDK's call_tool method
        return f"MCP tool '{name}' on server '{conn.get('name')}' called with args: {args}"