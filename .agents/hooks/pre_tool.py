#!/usr/bin/env python3
"""
PreToolUse / BeforeTool hook — runs before each shell/file tool call.

For Bash: blocks destructive operations on the pipeline database.
Communicates via stdin (JSON from agent) and stdout (JSON response).

Hook input (stdin):
  {"tool_name": "Bash", "tool_input": {"command": "..."}}

Hook output (stdout):
  {"action": "allow"}          — proceed normally
  {"action": "block", "message": "reason"}  — block the tool call
"""
import sys
import json


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name in ("Bash", "bash"):
        command = tool_input.get("command", "")
        # Block destructive operations on the live pipeline database
        dangerous = [
            "rm db/pipeline.db",
            "rm -rf db/",
            "DROP TABLE",
            "> db/pipeline.db",
            "truncate db/pipeline.db",
        ]
        for pattern in dangerous:
            if pattern.lower() in command.lower():
                print(json.dumps({
                    "action": "block",
                    "message": f"Blocked: command matches dangerous pattern '{pattern}'. "
                               "Use `python scripts/run_status.py` to inspect state safely."
                }))
                return

    # Allow everything else
    print(json.dumps({"action": "allow"}))


if __name__ == "__main__":
    main()
