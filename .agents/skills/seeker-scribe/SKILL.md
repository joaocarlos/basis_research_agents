---
name: seeker-scribe
description: >
  Run the Scribe agent: formats pipeline outputs into audience-ready artifacts.
  Supported types: understanding_map (always), blog_post, research_brief, internal_memo,
  literature_review (LaTeX), paper_section (LaTeX), grant_background (LaTeX).
  Triggers when asked to "write a blog post", "generate a research brief", "run scribe",
  or "produce the understanding map".
---

# Scribe Agent

Read the full reasoning prompt: `cat prompts/scribe.md`

## Your job

Format the pipeline's accumulated knowledge into clean, audience-ready artifacts.
The understanding map is ALWAYS generated first. Additional outputs are per researcher request.

## Steps

### 1. Determine output types
Ask the researcher which formats they need if not already specified from Break 2 instructions.
Always include `understanding_map`.

### 2. For each output type

#### Understanding Map (always first)
```bash
python scripts/context_for.py understanding_map <RUN_ID>
cat context/<RUN_ID>/understanding_map_context.md
```
Use the UNDERSTANDING MAP prompt in `prompts/scribe.md`.
Save content to `/tmp/understanding_map.md` then:
```bash
echo '{"content": "<markdown content>"}' | python scripts/save_output.py scribe <RUN_ID> --output-type understanding_map
```

#### Other formats
```bash
python scripts/context_for.py scribe <RUN_ID> --output-type <type> --audience "<audience>" --break2 "<instructions>"
cat context/<RUN_ID>/scribe_context.md
```
Use the matching prompt section in `prompts/scribe.md`.
```bash
echo '{"content": "<output content>"}' | python scripts/save_output.py scribe <RUN_ID> --output-type <type>
```

### 3. Confirm all artifacts
```bash
python scripts/run_status.py <RUN_ID>
```
List all generated artifact paths to the researcher.
