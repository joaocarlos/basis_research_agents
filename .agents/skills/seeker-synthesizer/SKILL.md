---
name: seeker-synthesizer
description: >
  Run the Synthesizer agent: integrates all pipeline outputs into a coherent research narrative.
  Produces the Break 2 review document. Triggers when asked to "synthesize", "run synthesizer",
  or "build the research narrative".
---

# Synthesizer Agent

Read the full reasoning prompt: `cat prompts/synthesizer.md`

## Your job

Integrate all pipeline outputs into a single coherent research narrative — not a summary,
an organizing argument. This document drives Break 2.

## Steps

### 1. Get full context
```bash
python scripts/context_for.py synthesizer <RUN_ID>
cat context/<RUN_ID>/synthesizer_context.md
```

### 2. Reason and produce output
Using the prompt in `prompts/synthesizer.md`, produce JSON with all fields including
`full_narrative` (flowing prose — this is the main deliverable).

### 3. Save output
```bash
echo '<your JSON>' | python scripts/save_output.py synthesizer <RUN_ID>
```

### 4. Write Break 2 review
```bash
python scripts/breaks.py write2 <RUN_ID>
```
Then present `artifacts/<RUN_ID>_break2_review.md` to the researcher.
