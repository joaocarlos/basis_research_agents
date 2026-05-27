# SEEKER — Multi-Agent Research Pipeline (Gemini CLI)

## Project overview

SEEKER is a 10-agent research intelligence system that conducts deep, traceable academic research.
It builds a persistent argument tree where every claim traces to verifiable evidence.

**You are the LLM.** Scripts handle data (API searches, DB writes, context assembly).
You handle reasoning (decomposition, gap analysis, proposals, narrative).

## How to use

Skills are in `.agents/skills/` — each has a `SKILL.md` with full instructions.
Hooks are configured in `.gemini/settings.json`.
Reasoning prompts (read before each agent step) are in `prompts/<agent>.md`.

### Start a new run
```bash
python scripts/init_run.py <RUN_ID> "<your research question>"
```

### Check status
```bash
python scripts/run_status.py
python scripts/run_status.py <RUN_ID>
```

## Pipeline sequence

Follow the same sequence as in `AGENTS.md`. The agent reasoning steps use the
prompts in `prompts/<agent>.md` and the context files written by `scripts/context_for.py`.

### Agent → prompt mapping

| Agent | Prompt file | Save command |
|---|---|---|
| Grounder | `prompts/grounder.md` (SYNTHESIS section) | `python scripts/save_grounder.py <RUN_ID> --file /tmp/out.json` |
| Historian | `prompts/historian.md` | `python scripts/save_output.py historian <RUN_ID>` |
| Gaper | `prompts/gaper.md` (PASS 1 then PASS 2) | `python scripts/save_output.py gaper <RUN_ID>` |
| Vision | `prompts/vision.md` | `python scripts/save_output.py vision <RUN_ID>` |
| Theorist | `prompts/theorist.md` (OVERVIEW then DETAIL × N) | `python scripts/save_output.py theorist <RUN_ID>` |
| Rude | `prompts/rude.md` | `python scripts/save_output.py rude <RUN_ID>` |
| Synthesizer | `prompts/synthesizer.md` | `python scripts/save_output.py synthesizer <RUN_ID>` |
| Thinker | `prompts/thinker.md` | `python scripts/save_output.py thinker <RUN_ID>` |
| Scribe | `prompts/scribe.md` (section matching output type) | `python scripts/save_output.py scribe <RUN_ID> --output-type <type>` |

## Break flow

Breaks are file-based:
1. `python scripts/breaks.py write<N> <RUN_ID>` — writes review to `artifacts/`
2. Researcher reads and writes instructions to `artifacts/<RUN_ID>_break<N>_instructions.md`
3. `python scripts/breaks.py check<N> <RUN_ID>` — returns instructions text when ready

## Key rules

- Never delete or overwrite `db/pipeline.db`
- Structural gaps from `gaper_structural.py` are proven facts — never dismiss them
- Scripts in `scripts/` have no LLM calls — they are pure data tools
- All reasoning lives in `prompts/`
