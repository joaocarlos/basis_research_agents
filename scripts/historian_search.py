#!/usr/bin/env python3
"""
Search historical sources and audit the argument tree (Historian data phase).
Usage: python scripts/historian_search.py <run_id>

Reads seminal works from DB, extends forward in time via OpenAlex,
audits existing tree claims, writes context/<run_id>/historian_search.md.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
import argparse
import logging
import requests

from core import database as db
from core.argument_tree import TreeBuilder
from core.utils import load_config

logging.basicConfig(level=logging.WARNING)


def _search_openalex_historical(query: str, year_from: int = None,
                                 year_to: int = None, limit: int = 5) -> list[dict]:
    from core.keys import openalex as get_key
    try:
        filters = ["has_abstract:true"]
        if year_from:
            filters.append(f"publication_year:>{year_from - 1}")
        if year_to:
            filters.append(f"publication_year:<{year_to + 1}")
        params = {
            "search":   query,
            "per-page": limit,
            "sort":     "publication_year:asc",
            "filter":   ",".join(filters),
        }
        key = get_key()
        if key:
            params["api_key"] = key
        else:
            params["mailto"] = "pipeline@research.local"
        resp = requests.get("https://api.openalex.org/works", params=params,
                            timeout=15, headers={"User-Agent": "PipelineResearchBot/1.0"})
        resp.raise_for_status()
        results = []
        for w in resp.json().get("results", []):
            abstract = ""
            if w.get("abstract_inverted_index"):
                words = {}
                for word, positions in w["abstract_inverted_index"].items():
                    for pos in positions:
                        words[pos] = word
                abstract = " ".join(words[i] for i in sorted(words))[:600]
            doi = w.get("doi", "")
            results.append({
                "title":   w.get("display_name", ""),
                "authors": [a.get("author", {}).get("display_name", "")
                            for a in w.get("authorships", [])[:3]],
                "year":    w.get("publication_year"),
                "source":  "openalex",
                "doi":     doi,
                "abstract": abstract,
                "link":    doi or w.get("id", ""),
            })
        return results
    except Exception as e:
        logging.warning(f"[OpenAlex/Historical] {e}")
        return []


def _audit_tree(run_id: str) -> list[dict]:
    """Check claims in argument tree and return confidence audit."""
    try:
        tree = TreeBuilder(run_id)
        stats = tree.get_stats()
        gaps = tree.find_gaps()
        tree.close()
        return {
            "stats": stats,
            "gaps": gaps,
        }
    except Exception as e:
        logging.warning(f"[TreeAudit] {e}")
        return {"stats": {}, "gaps": []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    run = db.get_run(args.run_id)
    if not run:
        print(f"ERROR: Run not found: {args.run_id}", file=sys.stderr)
        sys.exit(1)
    problem = run.get("problem", "")

    config = load_config()
    allowed = set(config.get("agent_sources", {}).get("historian", ["openalex"]))

    # Get seminal works as starting points
    seminal = db.get_sources_by_type("seminal", args.run_id)
    if not seminal:
        print("WARNING: No seminal works in DB — run grounder first", file=sys.stderr)

    # Tree audit
    audit = _audit_tree(args.run_id)

    # Search for historical works extending from seminal foundations
    all_historical = []
    for source in seminal[:8]:
        s_authors = json.loads(source.get("authors") or "[]") if source.get("authors") else []
        s_year = source.get("year")
        # Search for works that extend this seminal work's themes
        query_terms = []
        theme_tags = json.loads(source.get("theme_tags") or "[]") if source.get("theme_tags") else []
        if theme_tags:
            query_terms.append(theme_tags[0])
        title_words = [w for w in source.get("title", "").split()[:3]
                       if len(w) > 4]
        query_terms.extend(title_words[:2])
        query = " ".join(query_terms[:3])
        if not query:
            continue

        if "openalex" in allowed:
            results = _search_openalex_historical(
                query,
                year_from=s_year if s_year else None,
                limit=args.limit
            )
            all_historical.extend(results)
            time.sleep(0.3)

    print(f"Historical search: {len(all_historical)} works found from {len(seminal[:8])} seminal starting points")

    # Write context file
    ctx_dir = Path(__file__).parent.parent / "context" / args.run_id
    ctx_dir.mkdir(parents=True, exist_ok=True)
    out_path = ctx_dir / "historian_search.md"

    lines = [
        "# Historian Search Results\n",
        f"**Run:** {args.run_id}",
        f"**Problem:** {problem[:200]}\n",
        "---\n",
        "## Tree Audit\n",
    ]
    stats = audit.get("stats", {})
    lines.append(f"- Total nodes: {stats.get('total_nodes', 0)}")
    lines.append(f"- Total sources: {stats.get('unique_sources', 0)}")
    lines.append(f"- Structural gaps found: {len(audit.get('gaps', []))}\n")

    lines.append("## Seminal Works (Grounder — starting points)\n")
    for s in seminal[:20]:
        s_authors = json.loads(s.get("authors") or "[]") if s.get("authors") else []
        lines.append(
            f"- [{s.get('year', 'n.d.')}] **{s.get('title', '')}** "
            f"— {', '.join(s_authors[:2])}"
        )
        lines.append(f"  *{s.get('seminal_reason', '')}*")
    lines.append("")

    lines.append("## Historical Works Found\n")
    seen_titles = set()
    for r in all_historical:
        title = r.get("title", "")
        if title in seen_titles:
            continue
        seen_titles.add(title)
        authors = ", ".join(r.get("authors", [])[:2])
        abstract = (r.get("abstract", "") or "")[:250]
        lines.append(f"- [{r.get('year', 'n.d.')}] **{title}** — {authors}")
        lines.append(f"  Source: {r.get('source', '')} | {r.get('link', r.get('doi', ''))}")
        if abstract:
            lines.append(f"  {abstract}")
        lines.append("")

    out_path.write_text("\n".join(lines))

    print(f"Context written to: {out_path}")


if __name__ == "__main__":
    main()
