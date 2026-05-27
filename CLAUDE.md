# SEEKER — Multi-Agent Research Pipeline

## What this project does

SEEKER is a 10-agent research intelligence system that conducts deep, traceable academic research.
It builds a persistent **argument tree** where every claim traces to verifiable evidence.
The pipeline runs in three phases with three human-in-the-loop breaks.

## How to use with Claude Code

### Start a new research run
```
/seeker-run <your research question>
```

### Resume an interrupted run
```
/seeker-resume
```

### Check run status
```
/seeker-status
```

### Run a single agent
```
/seeker-grounder   /seeker-social   /seeker-historian  /seeker-gaper
/seeker-vision     /seeker-theorist /seeker-rude       /seeker-synthesizer
/seeker-thinker    /seeker-scribe
```

## Pipeline architecture

```
Break 0 → Social → Grounder → Historian → Gaper
Break 1 → Vision → Theorist → Rude → Synthesizer
Break 2 → Thinker → Scribe (understanding_map + requested formats)
```

## Key directories

| Path | Purpose |
|---|---|
| `prompts/` | Reasoning prompts for each agent (read by skills + subagents) |
| `scripts/` | Data tools — search, save, context assembly, breaks |
| `.agents/skills/` | SKILL.md files (shared across Claude Code, Codex, Gemini) |
| `.claude/agents/` | Claude Code native subagents (isolated context windows) |
| `.agents/hooks/` | Shared hook scripts (called by all platforms) |
| `agents/` | Legacy Python agents (search + DB logic without LLM calls) |
| `core/` | Infrastructure: DB, argument tree, context assembler, rate limiter |
| `artifacts/` | Pipeline outputs: break review files, scribe artifacts |
| `context/` | Runtime: assembled context files per run/agent |
| `db/` | SQLite database (`pipeline.db`) |

## Environment variables

Copy `.env.example` to `.env` and set:
- `ANTHROPIC_API_KEY` — required for Claude Code / Claude API
- `OPENAI_API_KEY` — required for Codex
- `GEMINI_API_KEY` — required for Gemini CLI
- `SEMANTIC_SCHOLAR_API_KEY` — optional, higher rate limits
- `SCOPUS_API_KEY` — optional, institutional access

## How agents work in this framework

**You are the LLM.** Scripts handle data; you handle reasoning.

For each agent the flow is:
1. Run the data script (`grounder_search.py`, `gaper_structural.py`, etc.) — searches APIs, builds context file
2. Read the prompt: `cat prompts/<agent>.md`
3. Read the assembled context: `cat context/<RUN_ID>/<agent>_context.md`
4. Reason and produce JSON output matching the schema in the prompt
5. Save: `echo '<json>' | python scripts/save_output.py <agent> <RUN_ID>`

Agents that need a dedicated context window should be invoked as `@<agent>` subagents
(e.g. `@grounder`, `@historian`). Each runs in isolation — verbose output stays out of
the main conversation.

## Script reference

| Script | Purpose |
|---|---|
| `scripts/init_run.py <id> "<problem>"` | Create run, init tree |
| `scripts/grounder_search.py <id>` | Search seminal sources → `context/<id>/grounder_search.md` |
| `scripts/social_search.py <id>` | Collect contemporary papers → DB |
| `scripts/historian_search.py <id>` | Search historical sources → `context/<id>/historian_search.md` |
| `scripts/gaper_structural.py <id>` | Extract structural gaps → `context/<id>/gaper_structural.md` |
| `scripts/context_for.py <agent> <id>` | Assemble DB context → `context/<id>/<agent>_context.md` |
| `scripts/save_grounder.py <id>` | Persist grounder JSON to DB + artifact |
| `scripts/save_output.py <agent> <id>` | Persist any agent's JSON to DB |
| `scripts/breaks.py <write\|check><0-2> <id>` | Write/check break review files |
| `scripts/run_status.py [<id>]` | Show pipeline state |

## Argument tree

Every claim in the pipeline traces to evidence in `db/pipeline.db`.
Node types: `root` → `question` → `claim` → `evidence` / `bridge` / `counter` / `historical`
The tree is the ground truth for Gaper's structural gap detection — never modify it directly.

## Development conventions

- **Never** delete or overwrite `db/pipeline.db` during a run
- Agent outputs are append-only; resume is always safe
- Scripts in `scripts/` have no LLM calls — they are pure data tools
- Reasoning lives in `prompts/` and `.claude/agents/` / `.agents/skills/`
- `core/llm.py` is retained for standalone/offline use only
