#!/usr/bin/env python3
"""
Save any agent's JSON output to the appropriate DB table.
Usage: python scripts/save_output.py <agent> <run_id> [--file path.json]
       echo '{"implications":[...]}' | python scripts/save_output.py vision <run_id>

Supported agents: historian, gaper, vision, theorist, rude, synthesizer, thinker, scribe
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import argparse
from datetime import datetime, timezone
from core import database as db
from core.utils import generate_id


def save_historian(run_id: str, data: dict, problem: str):
    saved = 0
    for work in data.get("historical_works", []):
        if not work.get("title"):
            continue
        source_id = generate_id("HIST")
        ok = db.upsert_source({
            "source_id":        source_id,
            "title":            work.get("title", ""),
            "authors":          work.get("authors", []),
            "year":             work.get("year"),
            "source_name":      work.get("source", "historian"),
            "doi":              work.get("doi", ""),
            "abstract":         work.get("abstract", ""),
            "active_link":      work.get("active_link", ""),
            "theme_tags":       work.get("theme_tags", []),
            "type":             "historical",
            "historical_reason": work.get("historical_reason", ""),
            "phase_tag":        work.get("phase_tag", ""),
            "intersection_tags": work.get("intersection_tags", []),
            "added_by":         "Historian",
            "date_collected":   datetime.now(timezone.utc).isoformat(),
            "last_checked":     datetime.now(timezone.utc).isoformat(),
            "link_status":      "unknown",
            "run_id":           run_id,
        })
        if ok:
            saved += 1

    # Write artifact
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_historian_map.md"
    path.parent.mkdir(exist_ok=True)
    lines = [f"# Historical Map — {run_id}\n", f"**Problem:** {problem}\n", "---\n"]
    for phase in data.get("phases", []):
        lines.append(f"## {phase.get('name', '')} ({phase.get('period', '')})")
        lines.append(phase.get("description", ""))
        if phase.get("transition_driver"):
            lines.append(f"*Transition: {phase['transition_driver']}*")
        lines.append("")
    for dead_end in data.get("dead_ends", []):
        lines.append(f"### Dead End: {dead_end.get('approach', '')} ({dead_end.get('period', '')})")
        lines.append(f"*Failed because: {dead_end.get('failure_reason', '')}*")
        lines.append(f"Lesson: {dead_end.get('lesson', '')}")
        lines.append("")
    path.write_text("\n".join(lines))
    print(f"Saved {saved} historical works | Artifact: {path}")


def save_gaper(run_id: str, data: dict):
    saved = 0
    for gap in data.get("gaps", []):
        gap_id = generate_id("GAP")
        ok = db.insert_gap({
            "gap_id":            gap_id,
            "run_id":            run_id,
            "gap_type":          gap.get("gap_type", ""),
            "gap_origin":        gap.get("gap_origin", "analytical"),
            "description":       gap.get("description", ""),
            "significance":      gap.get("significance", "Medium"),
            "significance_reason": gap.get("significance_reason", ""),
            "tree_node_ref":     gap.get("tree_node_ref", ""),
            "references_grounder": gap.get("references_grounder", []),
            "references_historian": gap.get("references_historian", []),
            "references_social": gap.get("references_current", gap.get("references_social", [])),
            "dead_end_revisit":  gap.get("dead_end_revisit", False),
            "recurring_pattern": gap.get("recurring_pattern", False),
            "recurring_reason":  gap.get("recurring_reason", ""),
            "primary_evaluation": gap.get("primary_evaluation", ""),
        })
        if ok:
            saved += 1

    # Write gaps artifact
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_gaper_gaps.md"
    path.parent.mkdir(exist_ok=True)
    lines = [f"# Gap Analysis — {run_id}\n", "---\n"]
    high = [g for g in data.get("gaps", []) if g.get("significance") == "High"]
    med  = [g for g in data.get("gaps", []) if g.get("significance") == "Medium"]
    low  = [g for g in data.get("gaps", []) if g.get("significance") == "Low"]
    for label, group in [("High", high), ("Medium", med), ("Low", low)]:
        if group:
            lines.append(f"## {label} Significance\n")
            for g in group:
                lines.append(f"### [{g.get('gap_origin','?')}] {g.get('gap_type','')}")
                lines.append(g.get("description", ""))
                if g.get("significance_reason"):
                    lines.append(f"*{g['significance_reason']}*")
                lines.append("")
    summary = data.get("gap_map_summary", "")
    if summary:
        lines += ["\n## Gap Map Summary\n", summary]
    path.write_text("\n".join(lines))
    print(f"Saved {saved} gaps | Artifact: {path}")


def save_vision(run_id: str, data: dict):
    saved = 0
    for impl in data.get("implications", []):
        impl_id = generate_id("IMP")
        ok = db.insert_implication({
            "implication_id":      impl_id,
            "run_id":              run_id,
            "implication":         impl.get("implication", ""),
            "implication_type":    impl.get("implication_type", ""),
            "strength":            impl.get("strength", "Moderate"),
            "strength_reason":     impl.get("strength_reason", ""),
            "scope":               impl.get("scope", "immediate"),
            "derived_from_grounder": impl.get("derived_from_grounder", []),
            "derived_from_historian": impl.get("derived_from_historian", []),
            "derived_from_gaper":  impl.get("derived_from_gaper", []),
            "hidden_assumption":   impl.get("hidden_assumption", False),
            "assumption_note":     impl.get("assumption_note", ""),
            "currently_pursued":   impl.get("currently_pursued", False),
            "pursuit_reference":   impl.get("pursuit_reference", ""),
        })
        if ok:
            saved += 1
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_vision_implications.md"
    path.parent.mkdir(exist_ok=True)
    lines = [f"# Vision — Implications\n**Run:** {run_id}\n\n---\n"]
    for strength in ("Strong", "Moderate", "Speculative"):
        group = [i for i in data.get("implications", []) if i.get("strength") == strength]
        if group:
            lines.append(f"## {strength}\n")
            for i in group:
                lines.append(f"### {i.get('implication_type','')}: {i.get('implication','')[:80]}")
                lines.append(i.get("implication", ""))
                lines.append(f"*{i.get('strength_reason','')}*\n")
    meta = data.get("meta_observation", "")
    if meta:
        lines += ["\n## Meta-Observation\n", meta]
    path.write_text("\n".join(lines))
    print(f"Saved {saved} implications | Artifact: {path}")


def save_theorist(run_id: str, data: dict):
    saved = 0
    for prop in data.get("proposals", []):
        prop_id = generate_id("PROP")
        ok = db.insert_proposal({
            "proposal_id":     prop_id,
            "run_id":          run_id,
            "proposal":        prop.get("proposal", ""),
            "proposal_type":   prop.get("proposal_type", "novel"),
            "addresses_gaps":  prop.get("addresses_gaps", []),
            "addresses_implications": prop.get("addresses_implications", []),
            "addresses_foundations": prop.get("addresses_foundations", []),
            "assumptions":     prop.get("assumptions", []),
            "requirements":    prop.get("requirements", []),
            "predictions":     prop.get("predictions", []),
            "dead_end_reassessment": prop.get("dead_end_reassessment", False),
            "dead_end_reference": prop.get("dead_end_reference", ""),
            "dead_end_reason": prop.get("dead_end_reason", ""),
            "interdependencies": prop.get("interdependencies", []),
            "promise_rating":  prop.get("promise_rating", "Medium"),
            "promise_reason":  prop.get("promise_reason", ""),
            "scope":           prop.get("scope", ""),
            "status":          "proposed",
        })
        if ok:
            saved += 1
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_theorist_proposals.md"
    path.parent.mkdir(exist_ok=True)
    lines = [f"# Theorist — Research Proposals\n**Run:** {run_id}\n\n---\n"]
    for i, prop in enumerate(data.get("proposals", []), 1):
        lines.append(f"## Proposal {i}: {prop.get('proposal','')[:80]}")
        lines.append(prop.get("proposal", ""))
        lines.append(f"**Type:** {prop.get('proposal_type','')}  **Promise:** {prop.get('promise_rating','')}")
        if prop.get("promise_reason"):
            lines.append(f"*{prop['promise_reason']}*")
        lines.append("")
    overview = data.get("overview_rationale", "")
    if overview:
        lines += ["\n## Overview Rationale\n", overview]
    path.write_text("\n".join(lines))
    print(f"Saved {saved} proposals | Artifact: {path}")


def save_rude(run_id: str, data: dict):
    proposals = db.get_proposals(run_id)
    saved = 0
    for ev in data.get("evaluations", []):
        ev_id = generate_id("EVAL")
        # Match proposal by text similarity
        proposal_ref = ev.get("proposal_ref", "")
        matched_id = None
        for p in proposals:
            if proposal_ref and p.get("proposal", "").startswith(proposal_ref[:80]):
                matched_id = p.get("proposal_id")
                break

        ok = db.insert_evaluation({
            "evaluation_id":              ev_id,
            "run_id":                     run_id,
            "proposal_id":                matched_id or "",
            "verdict":                    ev.get("verdict", "insufficient_evidence"),
            "verdict_reason":             ev.get("verdict_reason", ""),
            "weakest_empirical_link":     ev.get("weakest_empirical_link", ""),
            "dead_end_references":        ev.get("dead_end_references", []),
            "social_evidence_references": ev.get("social_evidence_references", []),
            "evidence_to_change_verdict": ev.get("evidence_to_change_verdict", ""),
        })
        if ok:
            saved += 1
        # Update proposal status
        if matched_id:
            verdict = ev.get("verdict", "")
            status = "feasible" if verdict == "feasible" else \
                     "partially_feasible" if verdict == "partially_feasible" else \
                     "infeasible"
            db.update_proposal_status(matched_id, status)

    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_rude_evaluations.md"
    path.parent.mkdir(exist_ok=True)
    lines = [f"# Rude — Adversarial Evaluations\n**Run:** {run_id}\n\n---\n"]
    for ev in data.get("evaluations", []):
        lines.append(f"## {ev.get('verdict','?').upper()}: {ev.get('proposal_ref','')[:70]}")
        lines.append(f"**Verdict reason:** {ev.get('verdict_reason','')}")
        if ev.get("weakest_empirical_link"):
            lines.append(f"**Weakest link:** {ev['weakest_empirical_link']}")
        lines.append("")
    if data.get("overall_assessment"):
        lines += ["\n## Overall Assessment\n", data["overall_assessment"]]
    path.write_text("\n".join(lines))
    print(f"Saved {saved} evaluations | Artifact: {path}")


def save_synthesizer(run_id: str, data: dict):
    synthesis_id = generate_id("SYN")
    ok = db.insert_synthesis({
        "synthesis_id":               synthesis_id,
        "run_id":                     run_id,
        "sharpened_problem":          data.get("sharpened_problem", ""),
        "intellectual_origins":       data.get("intellectual_origins_summary", ""),
        "historical_trajectory":      data.get("historical_trajectory_summary", ""),
        "knowledge_landscape":        data.get("knowledge_landscape", {}),
        "gap_landscape_summary":      data.get("gap_landscape_summary", ""),
        "logical_demands_summary":    data.get("logical_demands_summary", ""),
        "viable_proposals_summary":   data.get("viable_proposals_summary", ""),
        "tensions_and_contradictions": data.get("tensions_and_contradictions", []),
        "break1_override_log":        data.get("break1_override_log", []),
        "trajectory_statement":       data.get("trajectory_statement", ""),
        "full_narrative":             data.get("full_narrative", ""),
    })
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_synthesizer_narrative.md"
    path.parent.mkdir(exist_ok=True)
    lines = [f"# Synthesizer — Research Narrative\n**Run:** {run_id}\n\n---\n"]
    if data.get("sharpened_problem"):
        lines += ["## Sharpened Problem\n", data["sharpened_problem"], ""]
    if data.get("full_narrative"):
        lines += ["## Full Narrative\n", data["full_narrative"], ""]
    if data.get("trajectory_statement"):
        lines += ["## Trajectory Statement\n", data["trajectory_statement"], ""]
    tensions = data.get("tensions_and_contradictions", [])
    if tensions:
        lines.append("## Tensions and Contradictions\n")
        for t in tensions:
            lines.append(f"- {t}")
    path.write_text("\n".join(lines))
    print(f"Saved synthesis: {synthesis_id}" if ok else "Synthesis save failed")
    print(f"Artifact: {path}")


def save_thinker(run_id: str, data: dict):
    saved = 0
    for d in data.get("directions", []):
        dir_id = generate_id("DIR")
        ok = db.insert_direction({
            "direction_id":     dir_id,
            "run_id":           run_id,
            "direction":        d.get("direction", ""),
            "direction_type":   d.get("direction_type", "new_research"),
            "grounding_ref":    d.get("grounding_reference", ""),
            "distance_rating":  d.get("distance_rating", "Mid"),
            "reasoning":        d.get("reasoning", ""),
        })
        if ok:
            saved += 1
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_thinker_directions.md"
    path.parent.mkdir(exist_ok=True)
    lines = [f"# Thinker — New Research Directions\n**Run:** {run_id}\n\n---\n"]
    for dist in ("Near", "Mid", "Far"):
        group = [d for d in data.get("directions", []) if d.get("distance_rating") == dist]
        if group:
            lines.append(f"## {dist}-term\n")
            for d in group:
                lines.append(f"### {d.get('direction_type','')}: {d.get('direction','')[:80]}")
                lines.append(d.get("direction", ""))
                if d.get("reasoning"):
                    lines.append(f"*{d['reasoning']}*")
                lines.append("")
    path.write_text("\n".join(lines))
    print(f"Saved {saved} directions | Artifact: {path}")


def save_scribe(run_id: str, data: dict, output_type: str = "research_brief"):
    artifact_id = generate_id("ART")
    content = data.get("content", str(data))
    ext = "tex" if output_type in ("literature_review", "paper_section", "grant_background") else "md"
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_{output_type}.{ext}"
    path.parent.mkdir(exist_ok=True)
    path.write_text(content)
    db.insert_artifact({
        "artifact_id":  artifact_id,
        "run_id":       run_id,
        "output_type":  output_type,
        "file_path":    str(path),
        "content":      content[:500],
    })
    print(f"Artifact saved: {path}")


SAVERS = {
    "historian":   save_historian,
    "gaper":       save_gaper,
    "vision":      save_vision,
    "theorist":    save_theorist,
    "rude":        save_rude,
    "synthesizer": save_synthesizer,
    "thinker":     save_thinker,
    "scribe":      save_scribe,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", choices=list(SAVERS))
    parser.add_argument("run_id")
    parser.add_argument("--file", help="JSON file (default: stdin)")
    parser.add_argument("--output-type", default="research_brief", help="For scribe only")
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

    saver = SAVERS[args.agent]
    if args.agent == "historian":
        saver(args.run_id, data, problem)
    elif args.agent == "scribe":
        saver(args.run_id, data, args.output_type)
    else:
        saver(args.run_id, data)


if __name__ == "__main__":
    main()
