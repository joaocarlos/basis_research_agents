---
name: seeker-historian
description: >
  Run the Historian agent: builds the chronological map of the problem from intellectual
  origins to current state. Tracks phases, turning points, dead ends, key actors, and
  methods evolution. Triggers when asked to "map the history", "run historian",
  or "build the timeline".
---

# Historian Agent

Read the full reasoning prompt: `cat prompts/historian.md`

## Your job

Build the complete chronological map of the problem — phases, turning points, dead ends,
and key actors. Begin from Grounder's seminal works and extend forward in time.

## Steps

### 1. Search historical sources
```bash
python scripts/historian_search.py <RUN_ID>
cat context/<RUN_ID>/historian_search.md
```

### 2. Get full context
```bash
python scripts/context_for.py historian <RUN_ID>
cat context/<RUN_ID>/historian_context.md
```

### 3. Reason and produce output
Using the prompt in `prompts/historian.md`, produce the full JSON output:
phases, historical_works, key_actors, dead_ends, recurring_patterns,
methods_evolution, trajectory_vs_current.

**CRITICAL**: Dead ends and failures are equal data to successes. Document them thoroughly.

### 4. Save output
```bash
echo '<your JSON>' | python scripts/save_output.py historian <RUN_ID>
```
