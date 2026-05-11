#!/usr/bin/env python3
"""Crop a rectangular region from a source image and save it as a JPEG.

Usage:
    python3 crop_box.py SRC DEST LEFT TOP RIGHT BOTTOM [--quality 92]

LEFT, TOP, RIGHT, BOTTOM are pixel coordinates in the source image. Use
rotate_if_needed.py first if the photo was taken sideways.
"""
import argparse
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dest")
    ap.add_argument("left", type=int)
    ap.add_argument("top", type=int)
    ap.add_argument("right", type=int)
    ap.add_argument("bottom", type=int)
    ap.add_argument("--quality", type=int, default=92)
    args = ap.parse_args()

    img = Image.open(args.src)
    crop = img.crop((args.left, args.top, args.right, args.bottom))
    crop.save(args.dest, "JPEG", quality=args.quality)
    print(f"wrote {args.dest}  size={crop.size}")


if __name__ == "__main__":
    main()
