---
name: seeker-status
description: >
  Show the status of SEEKER pipeline runs. Triggers when the user asks "what runs do I have",
  "show run status", "what's the status of run <ID>", or "list my research runs".
---

# SEEKER Pipeline — Status

Show the current state of pipeline runs.

## With a run ID
```bash
python scripts/run_status.py <RUN_ID>
```
This shows which agents have completed, which breaks are done, and lists artifacts generated.

## Without a run ID
```bash
python scripts/run_status.py
```
Lists all recent runs with their status and problem statements.

Present the output clearly, highlighting:
- Which phase the run is currently in
- What step is blocked on (e.g. waiting for Break 1 instructions)
- What artifacts are ready to read
