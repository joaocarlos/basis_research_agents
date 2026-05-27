#!/usr/bin/env python3
"""
SessionStart hook — runs when a code agent session begins.
Initialises the DB, detects resumable runs, and prints a concise status summary.
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

import json

def main():
    try:
        from core import database as db
        db.init_db()
    except Exception as e:
        print(f"[SEEKER/SessionStart] DB init warning: {e}", file=sys.stderr)
        return

    # Check for in-progress runs
    try:
        runs = db.list_runs()
        active = [r for r in runs if r.get("status") not in ("completed", "aborted")]
        if active:
            print(f"[SEEKER] {len(active)} active run(s) found:")
            for r in active[:3]:
                print(f"  {r['run_id']} — {str(r.get('problem',''))[:80]}")
            print("[SEEKER] Use /seeker-resume or `python scripts/run_status.py` to continue.")
        else:
            print("[SEEKER] Pipeline ready. Use /seeker-run to start a new research run.")
    except Exception:
        pass

    # Print API key status (no values — just presence)
    keys_present = []
    keys_missing = []
    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
                "SEMANTIC_SCHOLAR_API_KEY", "SCOPUS_API_KEY"]:
        if os.environ.get(key):
            keys_present.append(key.replace("_API_KEY", ""))
        else:
            keys_missing.append(key.replace("_API_KEY", ""))
    if keys_missing:
        print(f"[SEEKER] API keys configured: {', '.join(keys_present) or 'none'}")
        print(f"[SEEKER] Keys not set (optional): {', '.join(keys_missing)}")


if __name__ == "__main__":
    main()
