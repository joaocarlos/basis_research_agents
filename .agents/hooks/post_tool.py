#!/usr/bin/env python3
"""
PostToolUse / AfterTool hook — runs after Write tool calls.

Logs artifact writes to a session log so the researcher has a record
of everything produced during the session.

Hook input (stdin):
  {"tool_name": "Write", "tool_input": {"file_path": "..."}, "tool_result": {...}}
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone


LOG_PATH = Path(__file__).parent.parent.parent / "artifacts" / ".session_writes.log"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "write"):
        return

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    # Only log writes to artifacts/ or context/
    p = Path(file_path)
    if not any(part in ("artifacts", "context") for part in p.parts):
        return

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        with open(LOG_PATH, "a") as f:
            f.write(f"{ts} | WRITE | {file_path}\n")
    except Exception:
        pass


if __name__ == "__main__":
    main()
