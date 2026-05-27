#!/usr/bin/env python3
"""
Stop / AfterAgent hook — runs when the agent session ends.

Prints a brief summary of what was accomplished and what's pending,
so the researcher knows where to pick up next session.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def main():
    try:
        from core import database as db
        runs = db.list_runs()
        active = [r for r in runs if r.get("status") not in ("completed", "aborted")]
        if not active:
            print("[SEEKER] Session ended. No active runs.")
            return

        print(f"[SEEKER] Session ended. {len(active)} active run(s):")
        for r in active[:3]:
            run_id = r["run_id"]
            print(f"  {run_id} — {str(r.get('problem',''))[:70]}")
            # Check break files
            artifacts = Path(ROOT) / "artifacts"
            for n in ["0", "1", "2"]:
                review = artifacts / f"{run_id}_break{n}_review.md"
                instr  = artifacts / f"{run_id}_break{n}_instructions.md"
                if review.exists() and not instr.exists():
                    print(f"    → Waiting for Break {n} instructions: {review.name}")
            print(f"  Resume with: /seeker-resume (run_id: {run_id})")
    except Exception as e:
        print(f"[SEEKER] Session ended. (Status check failed: {e})", file=sys.stderr)


if __name__ == "__main__":
    main()
