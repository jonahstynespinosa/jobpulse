#!/usr/bin/env python3
"""Standalone ingestion script — runs without the FastAPI server.
Used by GitHub Actions and local manual runs."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from database import init_db
from ingestion import run_ingestion

if __name__ == "__main__":
    init_db()
    results = run_ingestion()

    total_fetched = sum(r["fetched"] for r in results.values())
    total_added = sum(r["added"] for r in results.values())

    print("\n=== Ingestion complete ===")
    for src, r in results.items():
        print(f"  {src:12s}  fetched={r['fetched']:4d}  added={r['added']:4d}  skipped={r['skipped']:4d}")
    print(f"  {'TOTAL':12s}  fetched={total_fetched:4d}  added={total_added:4d}")

    sys.exit(0 if total_fetched > 0 else 1)
