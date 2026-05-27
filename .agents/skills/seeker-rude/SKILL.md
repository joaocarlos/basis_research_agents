---
name: seeker-rude
description: >
  Run the Rude agent: adversarial feasibility evaluation of all Theorist proposals
  strictly on empirical evidence. Does not care about logical elegance — only demonstrated facts.
  Triggers when asked to "evaluate proposals", "run rude", or "assess feasibility".
---

# Rude Agent

Read the full reasoning prompt: `cat prompts/rude.md`

## Your job

Evaluate every Theorist proposal on empirical evidence alone. Be brutal about failure modes.
Logic is NOT evidence.

## Steps

### 1. Get context (includes proposals)
```bash
python scripts/context_for.py rude <RUN_ID>
cat context/<RUN_ID>/rude_context.md
```

### 2. Reason and produce output
Using the prompt in `prompts/rude.md`, produce JSON with `evaluations`, `overall_ranking`,
and `feasibility_summary`. Every evaluation must reference specific studies or results.

### 3. Save output
```bash
echo '<your JSON>' | python scripts/save_output.py rude <RUN_ID>
```
