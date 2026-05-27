#!/usr/bin/env python3
"""
Manage pipeline break files.
Usage:
  python scripts/breaks.py write0 <run_id>   — write Break 0 review doc
  python scripts/breaks.py write1 <run_id>   — write Break 1 review doc
  python scripts/breaks.py write2 <run_id>   — write Break 2 review doc
  python scripts/breaks.py check0 <run_id>   — check for Break 0 instruction file
  python scripts/breaks.py check1 <run_id>   — check for Break 1 instruction file
  python scripts/breaks.py check2 <run_id>   — check for Break 2 instruction file
  python scripts/breaks.py parse  <run_id>   — parse latest available instructions

Prints the file path on write, or instructions content on check.
Exit code 0 = success/found, 1 = not found yet.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from core import breaks as core_breaks
from core import database as db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["write0", "write1", "write2",
                                            "check0", "check1", "check2", "parse"])
    parser.add_argument("run_id")
    args = parser.parse_args()

    run = db.get_run(args.run_id)
    if not run:
        print(f"ERROR: Run not found: {args.run_id}", file=sys.stderr)
        sys.exit(1)
    problem = run.get("problem", "")

    action = args.action
    run_id = args.run_id

    if action == "write0":
        from core.utils import load_config
        from core.concept_mapper import expand as concept_expand
        config = load_config()
        activated = []
        try:
            expansion = concept_expand(problem, run_id, config)
            activated = expansion.get("final_themes", [])
        except Exception:
            # Keyword fallback: match problem words against theme labels/ids
            words = set(problem.lower().split())
            for t in config.get("themes", []):
                label_words = set((t.get("label", "") + " " + t["theme_id"]).lower().split())
                if words & label_words:
                    activated.append(t["theme_id"])
        selected  = [t for t in config.get("themes", []) if t["theme_id"] in activated]
        excluded  = [{"theme_id": t["theme_id"], "label": t.get("label", ""),
                      "reason": "Not activated"}
                     for t in config.get("themes", []) if t["theme_id"] not in activated]
        path = core_breaks._produce_break0_doc(run_id, problem, selected, excluded)
        print(f"Break 0 review written: {path}")
        print(f"Waiting for: artifacts/{run_id}_break0_instructions.md")

    elif action == "write1":
        path = core_breaks._produce_break1_doc(run_id, problem)
        print(f"Break 1 review written: {path}")
        print(f"Waiting for: artifacts/{run_id}_break1_instructions.md")

    elif action == "write2":
        path = core_breaks._produce_break2_doc(run_id, problem)
        print(f"Break 2 review written: {path}")
        print(f"Waiting for: artifacts/{run_id}_break2_instructions.md")

    elif action.startswith("check"):
        num = action[-1]
        instr_path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_break{num}_instructions.md"
        if instr_path.exists():
            content = instr_path.read_text()
            instructions = core_breaks._extract_instructions(content)
            print(instructions)
            sys.exit(0)
        else:
            print(f"NOT FOUND: {instr_path}", file=sys.stderr)
            sys.exit(1)

    elif action == "parse":
        for num in ["1", "2", "0"]:
            instr_path = Path(__file__).parent.parent / "artifacts" / f"{run_id}_break{num}_instructions.md"
            if instr_path.exists():
                content = instr_path.read_text()
                instructions = core_breaks._extract_instructions(content)
                print(f"Break {num} instructions found:")
                print(instructions)
                sys.exit(0)
        print("No instruction files found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
