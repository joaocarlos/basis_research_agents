---
name: seeker-resume
description: >
  Resume a SEEKER pipeline run that was interrupted at a break or mid-agent.
  Triggers when the user says "resume run", "continue run <ID>", or "pick up where we left off".
---

# SEEKER Pipeline — Resume

Resume an existing run from wherever it stopped.

## Steps

1. Get the run ID (ask if not provided)
2. Check status:
```bash
python scripts/run_status.py <RUN_ID>
```
3. Read the status output to determine which phase was last completed.
4. Check for any pending break instruction files:
```bash
python scripts/breaks.py check0 <RUN_ID>
python scripts/breaks.py check1 <RUN_ID>
python scripts/breaks.py check2 <RUN_ID>
```
5. Resume from the first incomplete step — skip any agents already marked done.
6. Follow the same sequence as `/seeker-run` from that point onward.

If a break review file exists but no instructions file, re-present the review to the researcher
and collect their response before continuing.
