#!/usr/bin/env python3
"""
Initialize a new pipeline run.
Usage: python scripts/init_run.py <run_id> "<problem>"

Creates the DB run record and argument tree root.
Prints the run_id on success.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from core import database as db
from core.argument_tree import TreeBuilder
from core.utils import load_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id", help="Unique run identifier (e.g. RUN-XXXXXXXX)")
    parser.add_argument("problem", help="Research problem / question")
    args = parser.parse_args()

    db.init_db()

    existing = db.get_run(args.run_id)
    if existing:
        print(f"Run already exists: {args.run_id}")
        print(f"Problem: {existing.get('problem', '')[:120]}")
        print(f"Status: {existing.get('status', 'unknown')}")
        return

    db.create_run(args.run_id, args.problem)

    tree = TreeBuilder(args.run_id)
    root_id = tree.create_root(args.problem)
    tree.close()

    ctx_dir = Path(__file__).parent.parent / "context" / args.run_id
    ctx_dir.mkdir(parents=True, exist_ok=True)

    print(f"Run initialized: {args.run_id}")
    print(f"Problem: {args.problem[:120]}")
    print(f"Tree root: {root_id}")
    print(f"Context dir: {ctx_dir}")


if __name__ == "__main__":
    main()
