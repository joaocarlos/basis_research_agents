---
name: seeker-theorist
description: >
  Run the Theorist agent: proposes concrete research approaches, frameworks, and solutions
  anchored in all pipeline outputs. Two-pass design (overview then per-proposal detail).
  Triggers when asked to "propose approaches", "run theorist", or "generate proposals".
---

# Theorist Agent

Read the full reasoning prompt: `cat prompts/theorist.md`

## Your job

Propose 4-8 concrete research approaches, each anchored in gaps, implications, and foundations.

## Steps

### 1. Get context
```bash
python scripts/context_for.py theorist <RUN_ID> --break1 "<break1 instructions>"
cat context/<RUN_ID>/theorist_context.md
```

### 2. Pass 1 — Overview
Using OVERVIEW prompt in `prompts/theorist.md`, produce `proposals_summary` and
`proposals_index` (index of 4-8 proposals, one sentence each).
Save to `/tmp/theorist_overview.json`.

### 3. Pass 2 — Detail each proposal
For each proposal in the index, use the DETAIL prompt in `prompts/theorist.md`
to expand it fully. Collect all detailed proposals into a `"proposals": [...]` array.

### 4. Save output
```bash
echo '{"proposals": [...]}' | python scripts/save_output.py theorist <RUN_ID>
```
