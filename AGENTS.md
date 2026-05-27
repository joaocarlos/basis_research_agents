# SEEKER — Multi-Agent Research Pipeline (Codex)

## Project overview

SEEKER is a 10-agent research intelligence system that conducts deep, traceable academic research.
It builds a persistent argument tree where every claim traces to verifiable evidence.

**You are the LLM.** Scripts handle data (API searches, DB writes, context assembly).
You handle reasoning (decomposition, gap analysis, proposals, narrative).

## How to use

Skills are in `.agents/skills/` — each has a `SKILL.md` with full instructions.
Hooks are configured in `.codex/config.toml`.
Reasoning prompts (read before each agent step) are in `prompts/<agent>.md`.

### Start a new run
1. Generate a run ID: `RUN-` + 8 alphanumeric chars (e.g. `RUN-A3F7K2X9`)
2. `python scripts/init_run.py <RUN_ID> "<your research question>"`
3. Follow the pipeline sequence below

### Pipeline sequence

```
Break 0 — theme confirmation
  python scripts/breaks.py write0 <RUN_ID>
  [researcher reviews artifacts/<RUN_ID>_break0_review.md]
  [write response to artifacts/<RUN_ID>_break0_instructions.md]

Discovery Phase
  python scripts/social_search.py <RUN_ID>          ← Social agent data
  python scripts/grounder_search.py <RUN_ID>         ← Grounder data
  [Grounder reasoning — use prompts/grounder.md]
  python scripts/save_grounder.py <RUN_ID> --file /tmp/grounder.json

  python scripts/historian_search.py <RUN_ID>        ← Historian data
  [Historian reasoning — use prompts/historian.md]
  echo '<json>' | python scripts/save_output.py historian <RUN_ID>

  python scripts/gaper_structural.py <RUN_ID>        ← Structural gaps
  python scripts/context_for.py gaper <RUN_ID>
  [Gaper Pass 1 reasoning — use PASS 1 in prompts/gaper.md]
  [Gaper Pass 2 reasoning — use PASS 2 in prompts/gaper.md]
  echo '<json>' | python scripts/save_output.py gaper <RUN_ID>

Break 1 — foundations review
  python scripts/breaks.py write1 <RUN_ID>
  [researcher reviews and writes break1_instructions.md]
  BREAK1=$(python scripts/breaks.py check1 <RUN_ID>)

Inference Phase
  python scripts/context_for.py vision <RUN_ID> --break1 "$BREAK1"
  [Vision reasoning — use prompts/vision.md]
  echo '<json>' | python scripts/save_output.py vision <RUN_ID>

  python scripts/context_for.py theorist <RUN_ID> --break1 "$BREAK1"
  [Theorist Pass 1 + Pass 2 reasoning — use prompts/theorist.md]
  echo '<json>' | python scripts/save_output.py theorist <RUN_ID>

  python scripts/context_for.py rude <RUN_ID>
  [Rude reasoning — use prompts/rude.md]
  echo '<json>' | python scripts/save_output.py rude <RUN_ID>

  python scripts/context_for.py synthesizer <RUN_ID>
  [Synthesizer reasoning — use prompts/synthesizer.md]
  echo '<json>' | python scripts/save_output.py synthesizer <RUN_ID>

Break 2 — trajectory selection
  python scripts/breaks.py write2 <RUN_ID>
  [researcher reviews and writes break2_instructions.md]
  BREAK2=$(python scripts/breaks.py check2 <RUN_ID>)

Output Phase
  python scripts/context_for.py thinker <RUN_ID> --break2 "$BREAK2"
  [Thinker reasoning — use prompts/thinker.md]
  echo '<json>' | python scripts/save_output.py thinker <RUN_ID>

  python scripts/context_for.py understanding_map <RUN_ID>
  [Scribe understanding_map — use UNDERSTANDING MAP in prompts/scribe.md]
  echo '{"content":"<md>"}' | python scripts/save_output.py scribe <RUN_ID> --output-type understanding_map

  [Repeat scribe for each requested output type]
```

## Agent reasoning prompts

Each agent's reasoning prompt is in `prompts/<agent>.md`. When reasoning as an agent,
read the prompt, read the context file, produce JSON output matching the schema in the prompt.

## Key rules

- Never delete or overwrite `db/pipeline.db`
- Structural gaps from `gaper_structural.py` are facts — never dismiss them
- Scripts in `scripts/` have no LLM calls — they are pure data tools
- All reasoning prompts are in `prompts/`
- Check status at any time: `python scripts/run_status.py`
