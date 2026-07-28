#!/usr/bin/env python3
"""
prep_photo.py  —  run LOCALLY, once per photo (not in the daily workflow).

Turns a normal portrait into a clean grayscale source for ASCII conversion:
  1. remove background (rembg) so the subject is isolated
  2. CLAHE local-contrast boost so a flat face gets real highlights/shadows
  3. composite onto pure white so the background maps to blank (spaces)

Usage:
    python scripts/prep_photo.py source-photo.jpg
    -> writes source-prepped.png
"""
import sys
from pathlib import Path

import numpy as np
import cv2
from PIL import Image
from rembg import remove


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/prep_photo.py <photo.jpg>")
    src = Path(sys.argv[1])
    out = src.with_name("source-prepped.png")

    # 1) remove background -> RGBA
    cut = remove(Image.open(src).convert("RGBA"))

    # 2) composite onto white
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    composed = Image.alpha_composite(white, cut).convert("L")

    # 3) CLAHE local contrast
    arr = np.array(composed)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    arr = clahe.apply(arr)

    Image.fromarray(arr).save(out)
    print(f"Wrote {out}  ({out.width if hasattr(out,'width') else ''})")
    print("Next: python scripts/make_ascii_svg.py")


if __name__ == "__main__":
    main()
