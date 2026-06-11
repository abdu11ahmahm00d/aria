#!/usr/bin/env python3
"""ARIA pipeline entry point."""

import sys
import json
import time
import os

from dotenv import load_dotenv

load_dotenv()

import aria._fix_langchain  # noqa: F401, E402
from pipeline import aria_pipeline  # noqa: E402
from aria.state import ARIAState  # noqa: E402


def run(
    grades: str, students: str, submissions: str, output_dir: str = "output"
) -> dict:
    os.makedirs(output_dir, exist_ok=True)

    initial_state: ARIAState = {
        "grades_path": grades,
        "students_path": students,
        "submissions_path": submissions,
        "normalized_data": {},
        "flags": [],
        "report": "",
        "error": None,
    }

    start_time = time.time()
    print("[ARIA] Starting pipeline...")
    final = aria_pipeline.invoke(initial_state)
    elapsed = round(time.time() - start_time, 2)

    if final.get("error"):
        print(f"[ARIA] Pipeline failed: {final['error']}")
        sys.exit(1)

    flags = final.get("flags", [])
    report = final.get("report", "")

    flags_path = os.path.join(output_dir, "flags.json")
    with open(flags_path, "w", encoding="utf-8") as f:
        json.dump(flags, f, indent=2)
    print(f"[ARIA] Flags: {len(flags)} -> {flags_path}")

    report_path = os.path.join(output_dir, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[ARIA] Report saved to {report_path}")

    print(f"[ARIA] Complete in {elapsed}s")
    return {"flags": flags, "report": report}


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <grades> <students> <submissions> [output_dir]")
        sys.exit(1)
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "output"
    run(sys.argv[1], sys.argv[2], sys.argv[3], output_dir)
