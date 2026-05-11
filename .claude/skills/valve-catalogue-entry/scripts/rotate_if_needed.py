#!/usr/bin/env python3
"""Rotate a source image so the boxes appear upright.

Usage:
    python3 rotate_if_needed.py SRC DEST [--cw|--ccw|--flip]

Default rotates 90 degrees clockwise (correct for photos taken in landscape
orientation but stored as portrait by the camera). Inspect the result and
re-run with the opposite flag if the boxes come out upside-down.
"""
import argparse
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dest")
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--cw", action="store_const", dest="angle", const=-90)
    grp.add_argument("--ccw", action="store_const", dest="angle", const=90)
    grp.add_argument("--flip", action="store_const", dest="angle", const=180)
    args = ap.parse_args()
    angle = args.angle if args.angle is not None else -90  # default CW

    img = Image.open(args.src)
    out = img.rotate(angle, expand=True)
    out.save(args.dest, "JPEG", quality=92)
    print(f"wrote {args.dest}  size={out.size}  rotation={angle}")


if __name__ == "__main__":
    main()
