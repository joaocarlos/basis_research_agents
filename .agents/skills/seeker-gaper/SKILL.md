---
name: seeker-gaper
description: >
  Run the Gaper agent: maps knowledge gaps using the argument tree as primary structure.
  Two-pass design — structural gaps (deterministic from tree) then analytical gaps (LLM).
  Triggers when asked to "find gaps", "run gaper", or "map what's missing".
---

# Gaper Agent

Read the full reasoning prompt: `cat prompts/gaper.md`

## Your job

Map absence. Use the argument tree structure as ground truth for what gaps provably exist,
then add analytical depth the tree can't detect mechanistically.

## Steps

### 1. Extract structural gaps (deterministic)
```bash
python scripts/gaper_structural.py <RUN_ID>
cat context/<RUN_ID>/gaper_structural.md
```
These are PROVEN gaps. You cannot dismiss or downgrade them.

### 2. Get full context
```bash
python scripts/context_for.py gaper <RUN_ID>
cat context/<RUN_ID>/gaper_context.md
```

### 3. Pass 1 — Analytical scan
Using PASS 1 prompt in `prompts/gaper.md`: identify gaps the tree CANNOT detect
(disciplinary silences, methodological blind spots, assumption gaps, contradictions,
dead-end revisit opportunities). Output JSON with `analytical_gaps` and `tree_observations`.

Save Pass 1 to `/tmp/gaper_pass1.json`, then:

### 4. Pass 2 — Full analysis
Using PASS 2 prompt in `prompts/gaper.md`: produce the final gap map combining
structural + analytical gaps. Every structural gap must appear, enhanced with your analysis.

### 5. Save output
```bash
echo '<pass2 JSON>' | python scripts/save_output.py gaper <RUN_ID>
```
