#!/usr/bin/env python3
"""
Show pipeline run status.
Usage:
  python scripts/run_status.py             — list all recent runs
  python scripts/run_status.py <run_id>    — detailed status for one run
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from core import database as db


AGENT_ORDER = [
    "grounder", "social", "historian", "gaper",
    "vision", "theorist", "rude", "synthesizer", "thinker", "scribe"
]

BREAK_NAMES = {0: "Theme confirmation", 1: "Foundations review", 2: "Trajectory & output selection"}


def _agent_done(run_id: str, agent: str) -> bool:
    checks = {
        "grounder":    lambda: bool(db.get_sources_by_type("seminal", run_id)),
        "social":      lambda: bool(db.get_sources_by_type("current", run_id)),
        "historian":   lambda: bool(db.get_sources_by_type("historical", run_id)),
        "gaper":       lambda: bool(db.get_gaps(run_id)),
        "vision":      lambda: bool(db.get_implications(run_id)),
        "theorist":    lambda: bool(db.get_proposals(run_id)),
        "rude":        lambda: bool(db.get_evaluations(run_id)),
        "synthesizer": lambda: bool(db.get_synthesis(run_id)),
        "thinker":     lambda: bool(db.get_directions(run_id)),
        "scribe":      lambda: bool(db.get_artifacts(run_id)),
    }
    try:
        return checks.get(agent, lambda: False)()
    except Exception:
        return False


def _break_done(run_id: str, num: int) -> bool:
    path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_break{num}_instructions.md"
    return path.exists()


def show_run_detail(run_id: str):
    run = db.get_run(run_id)
    if not run:
        print(f"Run not found: {run_id}")
        return

    print(f"\nRun: {run_id}")
    print(f"Problem: {run.get('problem', '')[:100]}")
    print(f"Status:  {run.get('status', 'unknown')}")
    print(f"Created: {run.get('created_at', '')}")
    print()

    # Break 0
    b0 = _break_done(run_id, 0)
    print(f"  {'✓' if b0 else '○'} Break 0 — {BREAK_NAMES[0]}")

    # Discovery phase
    print("\n  Discovery Phase:")
    for agent in ["grounder", "social", "historian", "gaper"]:
        done = _agent_done(run_id, agent)
        print(f"    {'✓' if done else '○'} {agent.capitalize()}")

    # Break 1
    b1 = _break_done(run_id, 1)
    print(f"\n  {'✓' if b1 else '○'} Break 1 — {BREAK_NAMES[1]}")

    # Inference phase
    print("\n  Inference Phase:")
    for agent in ["vision", "theorist", "rude", "synthesizer"]:
        done = _agent_done(run_id, agent)
        print(f"    {'✓' if done else '○'} {agent.capitalize()}")

    # Break 2
    b2 = _break_done(run_id, 2)
    print(f"\n  {'✓' if b2 else '○'} Break 2 — {BREAK_NAMES[2]}")

    # Output phase
    print("\n  Output Phase:")
    for agent in ["thinker", "scribe"]:
        done = _agent_done(run_id, agent)
        print(f"    {'✓' if done else '○'} {agent.capitalize()}")

    # Artifact inventory
    artifacts_dir = Path(__file__).parent.parent / "artifacts"
    artifacts = list(artifacts_dir.glob(f"{run_id}_*.md")) + \
                list(artifacts_dir.glob(f"{run_id}_*.tex"))
    if artifacts:
        print(f"\n  Artifacts ({len(artifacts)}):")
        for a in sorted(artifacts):
            print(f"    - {a.name}")
    print()


def show_all_runs():
    runs = db.list_runs()
    if not runs:
        print("No runs found. Start one with: python scripts/init_run.py <run_id> '<problem>'")
        return
    print(f"\n{'Run ID':<20} {'Status':<15} {'Problem':<60}")
    print("-" * 95)
    for r in runs[:20]:
        print(f"{r.get('run_id',''):<20} {r.get('status',''):<15} "
              f"{str(r.get('problem',''))[:60]}")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id", nargs="?", help="Run ID (optional — lists all if omitted)")
    args = parser.parse_args()

    db.init_db()

    if args.run_id:
        show_run_detail(args.run_id)
    else:
        show_all_runs()


if __name__ == "__main__":
    main()
