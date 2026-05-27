# Workflow Test Report — RUN-TML7SC2X
**Topic:** TinyML on Smart Cities  
**Date:** 2026-05-27  
**Branch:** claude/code-agent-framework-redesign-d6aaF  
**Environment:** Claude Code on the web (remote container, linux/amd64)

---

## Purpose

End-to-end test of the redesigned SEEKER pipeline to validate:
1. All 10 scripts execute correctly
2. Subagents (grounder, historian, gaper, vision, theorist, rude, synthesizer, thinker, scribe) run in isolated contexts
3. Break flow (Break 0/1/2) works correctly
4. Artifacts are written to `artifacts/`
5. DB stays consistent throughout

---

## Environment Issues Found

### Missing API Keys (not bugs — configuration gap)

| Service | Status | Impact |
|---|---|---|
| `OPENALEX_API_KEY` | Not set | OpenAlex required key since Feb 2026; all requests → 403 |
| `SEMANTIC_SCHOLAR_API_KEY` | Not set | Unauthenticated requests → 403 |
| `ANTHROPIC_API_KEY` | Not set | LLM synthesis in concept_mapper falls back to Ollama then fails |
| Ollama | Not available | llama3.2:3b not found |

**Workaround:** Used MCP search tools (Consensus/scite) to collect 15 seminal papers manually,
pre-populated `context/RUN-TML7SC2X/grounder_search.md` and `historian_search.md` before
launching reasoning agents. Reasoning agents (Claude Code itself) ran successfully.

---

## Bugs Found and Fixed

### Bug 1: `scripts/breaks.py` — wrong import names from `core.concept_mapper`

**File:** `scripts/breaks.py` line 43  
**Error:** `ImportError: cannot import name 'concept_expand' from 'core.concept_mapper'`  
**Root cause:** Script imported `concept_expand` and `match_themes_to_problem`, but the actual
function in `core/concept_mapper.py` is named `expand` (no `concept_` prefix), and
`match_themes_to_problem` does not exist at all in that module.  
**Fix:** Changed import to `from core.concept_mapper import expand as concept_expand`
and replaced the missing `match_themes_to_problem` fallback with an inline keyword-matching
lambda over `config.get("themes", [])`.

### Bug 2: `scripts/social_search.py` — wrong argument type to `match_themes_to_problem`

**File:** `scripts/social_search.py` line 40  
**Error:** `AttributeError: 'str' object has no attribute 'get'`  
**Root cause:** `match_themes_to_problem(problem, config)` was called with the full `config`
dict as the second argument. `core.utils.match_themes_to_problem` signature is
`(problem: str, themes: list[dict])` — it expects the themes list, not the config.  
**Fix:** Changed call to `match_themes_to_problem(problem, config.get("themes", []))`
and unpacked the returned tuple: `selected, _ = ...`.

### Bug 3: `save_grounder.py` — sub-questions key mismatch (minor, non-blocking)

**File:** `scripts/save_grounder.py` line 105  
**Issue:** Script reads `data.get("decomposition_data", {}).get("sub_questions")` to build
tree nodes, but the SYNTHESIS prompt schema in `prompts/grounder.md` does not include
`decomposition_data` as a key — sub_questions come from the separate DECOMPOSE prompt.
The Grounder agent, which uses only the SYNTHESIS prompt, produces top-level keys only.  
**Impact:** Sub-questions are never automatically inserted into the argument tree from
the SYNTHESIS JSON. The grounder agent worked around this in its implementation by
calling `TreeBuilder.add_question()` directly.  
**Recommended fix:** Rename key in `save_grounder.py` from `decomposition_data.sub_questions`
to top-level `sub_questions`, matching the SYNTHESIS prompt schema.

---

## Pipeline Execution Trace

| Step | Status | Notes |
|---|---|---|
| `init_run.py` | ✓ | Run initialized, tree root created |
| `breaks.py write0` | ✓ (after fix) | Concept mapper ran without LLM; keyword fallback activated |
| Break 0 instructions | ✓ | Added `artificial_intelligence`, `complexity_systems` themes; removed irrelevant humanities themes |
| `social_search.py` | ✓ (after fix) | 0 sources collected — all APIs 403 |
| `grounder_search.py` | ✓ | 0 results — all APIs 403. Pre-populated context manually via MCP |
| `@grounder` agent | ✓ | 15 seminal works saved; foundations artifact written |
| `historian_search.py` | Skipped | Would overwrite pre-populated context with empty results |
| `@historian` agent | In progress | Reading historian_search.md pre-populated via MCP |
| `gaper_structural.py` | ✓ | 10 structural gaps identified (all sub-questions unanswered) |
| `@gaper` agent | In progress | Running 2-pass gap analysis |
| `breaks.py write1` | Pending | |
| Vision/Theorist/Rude/Synthesizer | Pending | |
| `breaks.py write2` | Pending | |
| Thinker/Scribe | Pending | |

---

## Agent Outputs

### Grounder (completed)

**Seminal works saved:** 15  
**Sub-questions in tree:** 10  
**Artifact:** `artifacts/RUN-TML7SC2X_grounder_foundations.md`

Key themes extracted: TinyML on MCUs, Smart City Sensing, Model Compression,
Federated Learning, Privacy-Preserving Edge AI, Urban Monitoring Applications,
SDG Alignment, LPWAN Connectivity

Intellectual genealogy: Two independent traditions converge — embedded systems engineering
(Han et al. 2015 deep compression) and urban informatics (Jiang 2020 federated city sensing)
— intersecting sharply around 2019–2020 when TF Lite Micro enabled ARM Cortex-M inference.

---

*This document is updated as the pipeline progresses.*
