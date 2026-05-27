#!/usr/bin/env python3
"""
Save Grounder agent output to DB.
Usage: python scripts/save_grounder.py <run_id> [--file path.json]
       echo '{"seminal_works":[...]}' | python scripts/save_grounder.py <run_id>

Reads JSON from --file or stdin.
Saves seminal works to sources table and writes foundations artifact.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
import argparse
from datetime import datetime, timezone
from core import database as db
from core.utils import generate_id
from core.argument_tree import TreeBuilder


def _verify_link(url: str) -> str:
    if not url:
        return "dead"
    import requests
    try:
        resp = requests.head(url, timeout=8, allow_redirects=True,
                             headers={"User-Agent": "PipelineResearchBot/1.0"})
        return "active" if resp.status_code < 400 else "dead"
    except Exception:
        return "dead"


def _save_doc(run_id: str, problem: str, data: dict):
    from pathlib import Path
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_grounder_foundations.md"
    path.parent.mkdir(exist_ok=True)

    lines = [
        "# Foundations Document — Grounder",
        f"**Run:** {run_id}",
        f"**Problem:** {problem}",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "", "---", "",
    ]

    themes = data.get("themes_extracted", [])
    lines += ["## Themes Extracted", ""]
    for t in themes:
        lines.append(f"- **{t.get('theme', '')}**: {t.get('description', '')}")
    if not themes:
        lines.append("*(none extracted)*")
    lines.append("")

    lines += ["## Fundamental Whys", ""]
    lines.append(data.get("fundamental_whys", "*(not produced)*"))
    lines.append("")

    lines += ["## Intellectual Genealogy", ""]
    lines.append(data.get("intellectual_genealogy", "*(not produced)*"))
    lines.append("")

    defs = data.get("original_definitions", [])
    if defs:
        lines += ["## Original Definitions", ""]
        for d in defs:
            lines.append(f"- **{d.get('concept', '')}** ({d.get('defined_by', '')}, {d.get('year', '')}): {d.get('definition', '')}")
        lines.append("")

    works = data.get("seminal_works", [])
    books  = [w for w in works if w.get("material_type") == "book"]
    papers = [w for w in works if w.get("material_type") != "book"]
    lines += ["## Seminal Works", ""]
    if papers:
        lines += ["### Papers & Articles", ""]
        for w in sorted(papers, key=lambda x: x.get("year") or 9999):
            lines.append(f"- **[{w.get('year', 'n.d.')}] {w.get('title', '')}** — {', '.join(w.get('authors', [])[:3])}")
            lines.append(f"  *{w.get('seminal_reason', '')}*")
    if books:
        lines += ["### Books", ""]
        for w in sorted(books, key=lambda x: x.get("year") or 9999):
            lines.append(f"- **[{w.get('year', 'n.d.')}] {w.get('title', '')}** — {', '.join(w.get('authors', [])[:3])}")
            lines.append(f"  *{w.get('seminal_reason', '')}*")
    if not works:
        lines.append("*(none found)*")

    path.write_text("\n".join(lines))
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--file", help="JSON file path (default: stdin)")
    args = parser.parse_args()

    if args.file:
        raw = Path(args.file).read_text()
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    run = db.get_run(args.run_id)
    if not run:
        print(f"ERROR: Run not found: {args.run_id}", file=sys.stderr)
        sys.exit(1)
    problem = run.get("problem", "")

    saved = 0
    tree = TreeBuilder(args.run_id)

    for work in data.get("seminal_works", []):
        if not work.get("title"):
            continue
        link_status = _verify_link(work.get("active_link", ""))
        source_id = generate_id("SEM")
        ok = db.upsert_source({
            "source_id":         source_id,
            "title":             work.get("title", ""),
            "authors":           work.get("authors", []),
            "year":              work.get("year"),
            "source_name":       work.get("source", "grounder"),
            "doi":               work.get("doi", ""),
            "abstract":          work.get("abstract", ""),
            "active_link":       work.get("active_link", ""),
            "theme_tags":        work.get("theme_tags", []),
            "type":              "seminal",
            "seminal_reason":    work.get("seminal_reason", ""),
            "intersection_tags": work.get("intersection_tags", []),
            "added_by":          "Grounder",
            "date_collected":    datetime.now(timezone.utc).isoformat(),
            "last_checked":      datetime.now(timezone.utc).isoformat(),
            "link_status":       link_status,
            "run_id":            args.run_id,
        })
        if ok:
            saved += 1
        time.sleep(0.05)

    # Save proposed new themes
    for proposal in data.get("proposed_new_themes", []):
        if not proposal.get("theme_id"):
            continue
        db.insert_seminal_proposal({
            "bank_id":            generate_id("BANK"),
            "proposed_theme":     proposal.get("theme_id", ""),
            "problem_origin":     problem,
            "reason":             proposal.get("reason", ""),
            "suggested_keywords": proposal.get("suggested_keywords", []),
            "suggested_sources":  proposal.get("suggested_sources", []),
        })

    # Add sub-questions from decomposition_data if present
    decomp = data.get("decomposition_data", {})
    if decomp.get("sub_questions"):
        root_id = tree.get_root_id()
        if root_id:
            for sq in decomp["sub_questions"]:
                tree.add_question(root_id, sq.get("question", ""),
                                  question_level=sq.get("level", "foundational"),
                                  agent="grounder")

    tree.close()

    doc_path = _save_doc(args.run_id, problem, data)

    print(f"Saved {saved} seminal works to DB")
    print(f"Foundations document: {doc_path}")


if __name__ == "__main__":
    main()
