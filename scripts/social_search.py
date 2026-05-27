#!/usr/bin/env python3
"""
Collect contemporary papers for the run (Social agent data phase).
Usage: python scripts/social_search.py <run_id>

Reads activated themes from config, searches all configured sources,
saves results to DB (type='current'), writes summary to context/<run_id>/social_context.md.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import logging

from core import database as db
from core.utils import load_config, match_themes_to_problem

logging.basicConfig(level=logging.WARNING)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--themes", nargs="*", help="Theme IDs to collect (default: all activated)")
    args = parser.parse_args()

    run = db.get_run(args.run_id)
    if not run:
        print(f"ERROR: Run not found: {args.run_id}", file=sys.stderr)
        sys.exit(1)
    problem = run.get("problem", "")

    config = load_config()

    # Determine themes to search
    if args.themes:
        themes = [t for t in config.get("themes", []) if t["theme_id"] in args.themes]
    else:
        activated = match_themes_to_problem(problem, config)
        themes = [t for t in config.get("themes", []) if t["theme_id"] in activated]
        if not themes:
            themes = config.get("themes", [])[:5]

    print(f"Collecting for {len(themes)} themes...")

    from agents.social import _collect_for_theme
    collected = []
    for i, theme in enumerate(themes):
        sources_for_theme = theme.get("sources", config.get("default_sources", ["openalex"]))
        results = _collect_for_theme(
            theme, sources_for_theme, config,
            problem=problem, limit_per_source=6,
            run_id=args.run_id, theme_index=i, theme_total=len(themes)
        )
        collected.extend(results)
        print(f"  {theme.get('label', theme['theme_id'])}: {len(results)} sources")

    # Write context summary
    ctx_dir = Path(__file__).parent.parent / "context" / args.run_id
    ctx_dir.mkdir(parents=True, exist_ok=True)
    out_path = ctx_dir / "social_context.md"

    sources_in_db = db.get_sources_by_type("current", args.run_id)
    lines = [
        f"# Social Intelligence — Current Sources\n",
        f"**Run:** {args.run_id}",
        f"**Total current sources in DB:** {len(sources_in_db)}\n",
        "---\n",
    ]
    import json as _json
    for s in sources_in_db[:40]:
        authors = _json.loads(s.get("authors") or "[]") if s.get("authors") else []
        lines.append(
            f"- [{s.get('year', 'n.d.')}] **{s.get('title', 'Untitled')}** "
            f"— {', '.join(authors[:2])} | {s.get('source_name', '')} | "
            f"{s.get('relevance_reason', '')}"
        )
    out_path.write_text("\n".join(lines))

    print(f"\nTotal sources collected this run: {len(collected)}")
    print(f"Total in DB: {len(sources_in_db)}")
    print(f"Context written to: {out_path}")


if __name__ == "__main__":
    main()
