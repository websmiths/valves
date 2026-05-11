#!/usr/bin/env python3
"""List the valve-photo submission that triggered this workflow run.

Strategy: ask git which image files were added in the trigger commit
(GITHUB_SHA), rather than scanning the whole submissions/ directory.
This guarantees one workflow run = one submission, even if previous
runs left stuck files in the directory.

For each image added in the trigger commit, find the matching note
(same basename, .note.txt extension) anywhere in submissions/ — the
note might have been added in a separate commit just after the image.

If GITHUB_SHA is not set (e.g. you're running this locally for debugging),
the script falls back to a directory scan so you can still inspect state.

Output schema:
    {
      "count": int,
      "submissions": [
        {"id": str, "image": str, "note_file": str | null, "ext": str}
      ],
      "stuck": [str],          # leftover image files in submissions/ that
                               # this run is NOT processing — for visibility
      "title": str,
      "summary": str
    }

The script does not move, delete, or modify any files — it only reports.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUB_DIR = REPO / "src-images" / "submissions"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def images_added_in(commit_sha: str) -> list[Path]:
    """Return image paths added in `commit_sha` under submissions/."""
    try:
        out = subprocess.check_output(
            [
                "git", "show", "--name-status", "--format=", commit_sha,
                "--", "src-images/submissions/",
            ],
            cwd=REPO,
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    added: list[Path] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        if status != "A":
            continue
        p = REPO / path
        if p.suffix.lower() in IMAGE_EXTS:
            added.append(p)
    return added


def scan_directory_for_images() -> list[Path]:
    if not SUB_DIR.is_dir():
        return []
    return [
        p for p in sorted(SUB_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]


def main() -> int:
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        target_images = images_added_in(sha)
    else:
        # Local / non-CI fallback: process whatever's sitting in submissions/.
        target_images = scan_directory_for_images()

    submissions = []
    for p in target_images:
        stem = p.stem
        note = SUB_DIR / f"{stem}.note.txt"
        submissions.append({
            "id": stem,
            "image": str(p.relative_to(REPO)) if p.is_absolute() else str(p),
            "note_file": str(note.relative_to(REPO)) if note.is_file() else None,
            "ext": p.suffix.lower().lstrip("."),
        })

    # Anything else in submissions/ that this run is NOT processing — kept
    # for visibility so a human can investigate stuck submissions later.
    target_ids = {s["id"] for s in submissions}
    stuck = []
    if SUB_DIR.is_dir():
        for p in scan_directory_for_images():
            if p.stem not in target_ids:
                stuck.append(str(p.relative_to(REPO)))

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if submissions:
        title = f"Submission: {len(submissions)} new photo{'s' if len(submissions) != 1 else ''} ({today})"
        summary = f"{len(submissions)} submission(s)"
    else:
        title = ""
        summary = "no submissions in trigger commit"

    print(json.dumps({
        "count": len(submissions),
        "submissions": submissions,
        "stuck": stuck,
        "title": title,
        "summary": summary,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
