---
name: seeker-run
description: >
  Run the full SEEKER research pipeline for a given research question.
  Triggers when the user says "run SEEKER", "start a new research run",
  "research [topic]", or provides a research question to investigate.
  Orchestrates all 10 agents in sequence with three human breaks.
---

# SEEKER Pipeline — Full Run

You are orchestrating the SEEKER multi-agent research pipeline. It runs 10 specialized
agents sequentially with three human-in-the-loop breaks.

## Before you start

1. Generate a run ID: `RUN-` followed by 8 uppercase alphanumeric characters (e.g. `RUN-A3F7K2X9`)
2. Initialize: `python scripts/init_run.py <RUN_ID> "<problem>"`
3. Confirm: "Run `<RUN_ID>` initialized. Starting pipeline..."

## Pipeline sequence

### Break 0 — Theme confirmation
```bash
python scripts/breaks.py write0 <RUN_ID>
```
Read `artifacts/<RUN_ID>_break0_review.md` and present the activated themes to the researcher.
Ask: "These themes will guide source collection. Confirm, add, or exclude any themes before continuing."
Write their response to `artifacts/<RUN_ID>_break0_instructions.md`.

### Discovery Phase
Run these in order (each depends on the previous):
```bash
python scripts/social_search.py <RUN_ID>
python scripts/grounder_search.py <RUN_ID>
```
Then invoke the @grounder subagent — it will read the search results and reason over them.
Then:
```bash
python scripts/historian_search.py <RUN_ID>
```
Invoke @historian. Then:
```bash
python scripts/gaper_structural.py <RUN_ID>
```
Invoke @gaper (two-pass: structural gaps then analytical).

### Break 1 — Foundations review
```bash
python scripts/breaks.py write1 <RUN_ID>
```
Read and present `artifacts/<RUN_ID>_break1_review.md` to the researcher.
Ask: "Review the foundations, historical map, and gaps. Override anything before inference begins."
Write their response to `artifacts/<RUN_ID>_break1_instructions.md`.

### Inference Phase
```bash
python scripts/context_for.py vision <RUN_ID> --break1 "<instructions>"
```
Invoke @vision, @theorist, @rude, @synthesizer in order, running `context_for.py` before each.

### Break 2 — Trajectory selection
```bash
python scripts/breaks.py write2 <RUN_ID>
```
Present `artifacts/<RUN_ID>_break2_review.md`. Ask which output formats are needed
(blog_post, research_brief, internal_memo, literature_review, paper_section, grant_background).
Write their response to `artifacts/<RUN_ID>_break2_instructions.md`.

### Output Phase
Invoke @thinker. Then for each requested output type, invoke @scribe.
The understanding map is always generated first:
```bash
python scripts/context_for.py understanding_map <RUN_ID>
```

## Completion
```bash
python scripts/run_status.py <RUN_ID>
```
Report all artifacts generated and their paths.
