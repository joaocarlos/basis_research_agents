#!/usr/bin/env python3
"""
Assemble context for a given agent and write it to context/<run_id>/<agent>_context.md.
Usage: python scripts/context_for.py <agent> <run_id> [--break1 <text>] [--break2 <text>]

Supported agents: grounder, social, historian, gaper, vision, theorist, rude,
                  synthesizer, thinker, scribe, understanding_map
Prints the file path on success.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from core import context as ctx
from core import database as db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", help="Agent name")
    parser.add_argument("run_id", help="Run ID")
    parser.add_argument("--break1", default="", help="Break 1 instructions text")
    parser.add_argument("--break2", default="", help="Break 2 instructions text")
    parser.add_argument("--output-type", default="research_brief")
    parser.add_argument("--audience", default="researcher")
    args = parser.parse_args()

    run = db.get_run(args.run_id)
    if not run:
        print(f"ERROR: Run not found: {args.run_id}", file=sys.stderr)
        sys.exit(1)
    problem = run.get("problem", "")

    agent = args.agent.lower().replace("-", "_")

    dispatchers = {
        "grounder":        lambda: ctx.for_grounder(args.run_id, problem,
                               db.get_sources_by_type("current", args.run_id)),
        "historian":       lambda: ctx.for_historian(args.run_id, problem),
        "gaper":           lambda: ctx.for_gaper(args.run_id, problem, args.break1 or None),
        "vision":          lambda: ctx.for_vision(args.run_id, problem, args.break1 or None),
        "theorist":        lambda: ctx.for_theorist(args.run_id, problem, args.break1 or None),
        "rude":            lambda: ctx.for_rude(args.run_id, problem, args.break1 or None),
        "synthesizer":     lambda: ctx.for_synthesizer(args.run_id, problem, args.break1 or None),
        "thinker":         lambda: ctx.for_thinker(args.run_id, problem, args.break2 or None),
        "scribe":          lambda: ctx.for_scribe(args.run_id, problem,
                               args.output_type, args.audience, args.break2 or None),
        "understanding_map": lambda: ctx.for_understanding_map(args.run_id, problem),
    }

    if agent not in dispatchers:
        print(f"ERROR: Unknown agent '{agent}'. Valid: {', '.join(dispatchers)}", file=sys.stderr)
        sys.exit(1)

    content = dispatchers[agent]()

    ctx_dir = Path(__file__).parent.parent / "context" / args.run_id
    ctx_dir.mkdir(parents=True, exist_ok=True)
    out_path = ctx_dir / f"{agent}_context.md"
    out_path.write_text(content)

    print(str(out_path))


if __name__ == "__main__":
    main()
