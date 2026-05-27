---
name: seeker-thinker
description: >
  Run the Thinker agent: opens new research directions from the synthesis. First agent
  explicitly allowed to look beyond the current frame. Triggers when asked to "open new
  directions", "run thinker", or "what comes next".
---

# Thinker Agent

Read the full reasoning prompt: `cat prompts/thinker.md`

## Your job

Open new directions from the synthesis — informed, disciplined speculation grounded in
what the pipeline established. NOT brainstorming.

## Steps

### 1. Get context (includes Break 2 instructions)
```bash
python scripts/context_for.py thinker <RUN_ID> --break2 "<break2 instructions>"
cat context/<RUN_ID>/thinker_context.md
```

### 2. Reason and produce output
Using the prompt in `prompts/thinker.md`, produce JSON with `directions`,
`challenged_assumptions`, `reconsidered_exclusions`, and `new_directions_summary`.

Every direction must be: grounded, genuinely new, scoped, and distance-rated (Near/Mid/Far).

### 3. Save output
```bash
echo '<your JSON>' | python scripts/save_output.py thinker <RUN_ID>
```
