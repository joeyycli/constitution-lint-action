#!/usr/bin/env python3
"""Stdio MCP server exposing the constitution linter as a `lint_constitution` tool.

Zero-dependency, like the rest of this repo: speaks JSON-RPC 2.0 over
stdin/stdout per the MCP stdio transport (one JSON message per line), so it
runs anywhere Python 3.9+ runs.

Usage:
    python3 constitution_lint_mcp.py            # or: constitution-lint-mcp
    docker run -i --rm ghcr.io/... (see Dockerfile)

Claude Desktop / any MCP client config:
    {"command": "python3", "args": ["/path/to/constitution_lint_mcp.py"]}

The tool takes the constitution file's full markdown text as `content`.
The referenced-state-files-exist check needs a filesystem to look at, so on
content-only input it reports which files are referenced without verifying
they exist.
"""

from __future__ import annotations

import json
import re
import sys

from constitution_lint import CHECKS

PROTOCOL_VERSIONS = {"2024-11-05", "2025-03-26", "2025-06-18"}
SERVER_INFO = {"name": "constitution-lint", "version": "1.2.1"}

TOOL = {
    "name": "lint_constitution",
    "description": (
        "Heuristic checker for CLAUDE.md-style autonomous-agent constitution "
        "files — 10 checks against operational-guardrail patterns (authority "
        "order, spend limit, injection defense, secrets handling, escalation, "
        "ledger discipline, self-modification guard, honest reporting, session "
        "ritual, referenced-state-files). Pattern-matching, not comprehension."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The full markdown text of a CLAUDE.md-style constitution file",
            }
        },
        "required": ["content"],
    },
}


def run_checks(content: str) -> str:
    results = []
    for name, fn in CHECKS:
        if name == "referenced-state-files-exist":
            referenced = sorted(set(re.findall(r"\b([A-Z][A-Z0-9_]*\.md)\b", content)))
            if referenced:
                status, reason = "WARN", (
                    "content-only input, cannot verify files exist on disk; "
                    f"referenced: {', '.join(referenced)}"
                )
            else:
                status, reason = "WARN", "no *.md state files referenced by name — nothing to verify"
        else:
            status, reason = fn(content, None)
        results.append((name, status, reason))

    width = max(len(name) for name, _, _ in results)
    fails = sum(1 for _, s, _ in results if s == "FAIL")
    warns = sum(1 for _, s, _ in results if s == "WARN")
    lines = [f"[{status:4}] {name.ljust(width)}  {reason}" for name, status, reason in results]
    lines.append("")
    lines.append(f"{len(results)} checks: {len(results) - fails - warns} pass, {warns} warn, {fails} fail")
    if fails:
        lines.append(
            "This is a heuristic pattern-matcher, not a guarantee — a FAIL means "
            "the pattern wasn't found, not that the file is unsafe. Read it yourself."
        )
    return "\n".join(lines)


def handle(msg: dict):
    method = msg.get("method")
    msg_id = msg.get("id")
    is_notification = "id" not in msg

    if method == "initialize":
        requested = (msg.get("params") or {}).get("protocolVersion")
        version = requested if requested in PROTOCOL_VERSIONS else "2025-06-18"
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        }, None
    if method == "ping":
        return {}, None
    if method == "tools/list":
        return {"tools": [TOOL]}, None
    if method == "tools/call":
        params = msg.get("params") or {}
        if params.get("name") != "lint_constitution":
            return None, {"code": -32602, "message": f"unknown tool: {params.get('name')!r}"}
        content = (params.get("arguments") or {}).get("content")
        if not isinstance(content, str) or not content.strip():
            return {
                "content": [{"type": "text", "text": "error: `content` must be a non-empty string"}],
                "isError": True,
            }, None
        return {"content": [{"type": "text", "text": run_checks(content)}], "isError": False}, None
    if is_notification:
        return None, None  # notifications/initialized etc. — no response
    return None, {"code": -32601, "message": f"method not found: {method}"}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
            print(json.dumps(reply), flush=True)
            continue
        result, error = handle(msg)
        if "id" not in msg:
            continue
        reply = {"jsonrpc": "2.0", "id": msg.get("id")}
        if error is not None:
            reply["error"] = error
        else:
            reply["result"] = result
        print(json.dumps(reply), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
