---
name: seeker-grounder
description: >
  Run the Grounder agent: excavates the intellectual origins of the research problem,
  decomposes it into sub-questions, searches seminal academic sources (OpenAlex, Semantic
  Scholar, Google Books, Open Library), and builds the argument tree foundations.
  Triggers when asked to "find foundational literature", "run grounder",
  "excavate intellectual origins", or at the start of a pipeline run.
---

# Grounder Agent

Read the full reasoning prompt: `cat prompts/grounder.md`

## Your job

You excavate the intellectual origins of a research problem — who first asked it, why, and how the foundational ideas connect.

## Steps

### 1. Get context
```bash
python scripts/context_for.py grounder <RUN_ID>
cat context/<RUN_ID>/grounder_context.md
```

### 2. Search for sources
```bash
python scripts/grounder_search.py <RUN_ID>
cat context/<RUN_ID>/grounder_search.md
```

### 3. Decompose the problem
Using the DECOMPOSE prompt in `prompts/grounder.md`, decompose the research problem
into 6-12 sub-questions. Work from fundamentals upward.

### 4. Generate search queries
For each sub-question, apply the QUERY_GEN prompt to produce `paper_query`, `book_query`,
and `web_query`. Note: grounder_search.py has already run basic searches; use the results
plus your query reasoning to inform synthesis.

### 5. Synthesize foundations
Using the SYNTHESIS prompt in `prompts/grounder.md` and all gathered sources,
produce the JSON output (themes, seminal_works, intellectual_genealogy, etc.)

### 6. Save output
```bash
echo '<your JSON output>' | python scripts/save_grounder.py <RUN_ID>
```
Or write JSON to a temp file first:
```bash
python scripts/save_grounder.py <RUN_ID> --file /tmp/grounder_out.json
```

### 7. Verify
```bash
python scripts/run_status.py <RUN_ID>
```
Confirm seminal works were saved.
