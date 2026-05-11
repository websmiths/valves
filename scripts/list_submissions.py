#!/usr/bin/env python3
"""List pending valve-photo submissions for the process-submission workflow.

Scans `src-images/submissions/` for image files. For each, finds its
matching `*.note.txt` (same basename) if present. Emits a JSON document
on stdout describing the work to do, plus a one-line summary suitable
for a step-output / PR title.

Output schema:
    {
      "count": int,
      "submissions": [
        {"id": str, "image": str, "note_file": str | null, "ext": str}
      ],
      "title": str,            # e.g. "Submission: 2 new photos (2026-05-11)"
      "summary": str           # short status-line for commits / logs
    }

The script does not move, delete, or modify any files — it only reports.
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUB_DIR = REPO / "src-images" / "submissions"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> int:
    if not SUB_DIR.is_dir():
        # Nothing to do — print an empty result and exit 0 so the workflow
        # can branch on count == 0 rather than on exit code.
        print(json.dumps({"count": 0, "submissions": [], "title": "", "summary": "no submissions"}))
        return 0

    submissions = []
    for p in sorted(SUB_DIR.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMAGE_EXTS:
            continue
        stem = p.stem  # filename without extension
        note = SUB_DIR / f"{stem}.note.txt"
        submissions.append({
            "id": stem,
            "image": str(p.relative_to(REPO)),
            "note_file": str(note.relative_to(REPO)) if note.is_file() else None,
            "ext": p.suffix.lower().lstrip("."),
        })

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if submissions:
        title = f"Submission: {len(submissions)} new photo{'s' if len(submissions) != 1 else ''} ({today})"
        summary = f"{len(submissions)} submission(s)"
    else:
        title = ""
        summary = "no submissions"

    print(json.dumps({
        "count": len(submissions),
        "submissions": submissions,
        "title": title,
        "summary": summary,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
