#!/usr/bin/env python3
"""
Extract structural gaps from the argument tree (deterministic — no LLM).
Usage: python scripts/gaper_structural.py <run_id>

Writes context/<run_id>/gaper_structural.md with all structural gaps
that the tree proves exist (unanswered questions, unsupported claims, etc.)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from core import database as db
from core.argument_tree import TreeBuilder


def _get_structural_gaps(run_id: str) -> dict:
    """Extract structural gaps directly from the argument tree."""
    try:
        tree = TreeBuilder(run_id)
        gaps = tree.find_gaps()
        bridge_needs = tree.find_bridge_needs()
        stats = tree.get_stats()
        tree.close()

        unanswered    = [g for g in gaps if g.get("gap_type") == "unanswered_question"]
        unsupported   = [g for g in gaps if g.get("gap_type") == "unsupported_claim"]
        weak_claims   = [g for g in gaps if g.get("gap_type") == "weak_claim"]

        return {
            "total_nodes":     stats.get("total_nodes", 0),
            "unique_sources":  stats.get("unique_sources", 0),
            "unanswered":      unanswered,
            "unsupported":     unsupported,
            "weak_claims":     weak_claims,
            "bridge_needs":    bridge_needs,
            "all_gaps":        gaps,
        }
    except Exception as e:
        print(f"WARNING: Tree audit failed — {e}", file=sys.stderr)
        return {
            "total_nodes": 0, "unique_sources": 0,
            "unanswered": [], "unsupported": [],
            "weak_claims": [], "bridge_needs": [], "all_gaps": [],
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()

    run = db.get_run(args.run_id)
    if not run:
        print(f"ERROR: Run not found: {args.run_id}", file=sys.stderr)
        sys.exit(1)
    problem = run.get("problem", "")

    result = _get_structural_gaps(args.run_id)

    ctx_dir = Path(__file__).parent.parent / "context" / args.run_id
    ctx_dir.mkdir(parents=True, exist_ok=True)
    out_path = ctx_dir / "gaper_structural.md"

    lines = [
        "# Structural Gaps — Argument Tree Analysis\n",
        f"**Run:** {args.run_id}",
        f"**Problem:** {problem[:200]}\n",
        f"**Tree nodes:** {result['total_nodes']} | **Unique sources:** {result['unique_sources']}\n",
        "---\n",
        "## STRUCTURAL GAPS (proven — cannot be dismissed)\n",
        "> These gaps are FACTS derived from the tree structure.",
        "> The Gaper agent MUST include all of them in its final gap map.\n",
    ]

    # Unanswered questions
    lines.append(f"### Unanswered Questions ({len(result['unanswered'])})\n")
    if result["unanswered"]:
        for g in result["unanswered"]:
            lines.append(f"- **[{g.get('node_id', '?')}]** {g.get('description', '')}")
            lines.append(f"  *Significance: {g.get('significance', 'High')} — question node has no claim children*")
    else:
        lines.append("*(none — all questions have claims)*")
    lines.append("")

    # Unsupported claims
    lines.append(f"### Unsupported Claims ({len(result['unsupported'])})\n")
    if result["unsupported"]:
        for g in result["unsupported"]:
            lines.append(f"- **[{g.get('node_id', '?')}]** {g.get('description', '')}")
            lines.append(f"  *Significance: {g.get('significance', 'Medium')} — claim node has no evidence*")
    else:
        lines.append("*(none — all claims have evidence)*")
    lines.append("")

    # Weak claims
    lines.append(f"### Weak Claims ({len(result['weak_claims'])})\n")
    if result["weak_claims"]:
        for g in result["weak_claims"]:
            conf = g.get("confidence", 0)
            lines.append(f"- **[{g.get('node_id', '?')}]** {g.get('description', '')}")
            lines.append(f"  *Confidence: {conf:.2f} | single source or low evidence weight*")
    else:
        lines.append("*(none — all claims adequately supported)*")
    lines.append("")

    # Temporal bridge needs
    lines.append(f"### Temporal Bridge Needs ({len(result['bridge_needs'])})\n")
    if result["bridge_needs"]:
        for b in result["bridge_needs"]:
            lines.append(f"- **[{b.get('node_id', '?')}]** {b.get('description', '')}")
            lines.append(f"  *Period gap: {b.get('period_gap', 'unknown')}*")
    else:
        lines.append("*(none identified)*")
    lines.append("")

    total = (len(result["unanswered"]) + len(result["unsupported"]) +
             len(result["weak_claims"]) + len(result["bridge_needs"]))

    out_path.write_text("\n".join(lines))

    print(f"Structural gaps found: {total}")
    print(f"  Unanswered questions: {len(result['unanswered'])}")
    print(f"  Unsupported claims:   {len(result['unsupported'])}")
    print(f"  Weak claims:          {len(result['weak_claims'])}")
    print(f"  Bridge needs:         {len(result['bridge_needs'])}")
    print(f"Written to: {out_path}")


if __name__ == "__main__":
    main()
