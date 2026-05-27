---
name: seeker-social
description: >
  Run the Social agent: collects contemporary papers across all activated themes
  from OpenAlex, arXiv, PubMed, Semantic Scholar, CORE, PhilPapers, and other sources.
  Triggers when asked to "collect current papers", "run social agent", or "gather literature".
---

# Social Agent

Read the reasoning prompt: `cat prompts/social.md`

## Your job

Collect contemporary papers relevant to the research problem across all activated themes.
These become the "current intelligence" layer that all downstream agents reference.

## Steps

### 1. Collect sources
```bash
python scripts/social_search.py <RUN_ID>
```

### 2. Review results
```bash
cat context/<RUN_ID>/social_context.md
```

### 3. Rate and filter (optional)
Using the RELEVANCE RATING prompt in `prompts/social.md`, assess borderline papers.
Remove clearly irrelevant results by updating their status in the DB if needed.

### 4. Confirm
```bash
python scripts/run_status.py <RUN_ID>
```
Current sources are now available to all downstream agents via `context_for.py`.
