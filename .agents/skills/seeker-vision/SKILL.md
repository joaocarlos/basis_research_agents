---
name: seeker-vision
description: >
  Run the Vision agent: extracts logical consequences, implications, and inferences
  from accumulated knowledge. First inferential agent — runs after Break 1.
  Triggers when asked to "extract implications", "run vision", or "draw logical consequences".
---

# Vision Agent

Read the full reasoning prompt: `cat prompts/vision.md`

## Your job

Extract what logically follows from the established foundations, historical map, and gaps.
Every implication must be traceable and strength-rated.

## Steps

### 1. Get context (includes Break 1 instructions if available)
```bash
python scripts/context_for.py vision <RUN_ID> --break1 "<break1 instructions text>"
cat context/<RUN_ID>/vision_context.md
```

### 2. Reason and produce output
Using the prompt in `prompts/vision.md`, produce JSON with `implications` array.
Write Strong implications first, then Moderate, then Speculative.

### 3. Save output
```bash
echo '<your JSON>' | python scripts/save_output.py vision <RUN_ID>
```
