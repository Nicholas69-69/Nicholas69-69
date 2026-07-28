#!/usr/bin/env python3
"""
make_ascii_svg.py  —  run LOCALLY after prep_photo.py.

Downsamples source-prepped.png to a character grid and maps brightness to a
density ramp, then emits avi-ascii.svg where each ROW wipes in left-to-right
(a small block cursor rides the wipe edge), staggered top->bottom. Prints
once and freezes — no looping.

Usage:
    python scripts/make_ascii_svg.py
    -> writes ascii-portrait.svg
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "ascii-portrait.svg"

# bright (sparse) -> dark (dense). Leading space clears bg to nothing.
RAMP = " .`:-=+*cs#%@"

COLS = 100          # character columns
CHAR_ASPECT = 0.5   # monospace glyphs are ~half as wide as tall
CH_W = 7            # px per char cell width in the SVG
CH_H = 12           # px per char cell height
FILL = "#c9d1d9"    # single light-gray fill (monochrome = clean, not noisy)
BG = "#0d1117"
ROW_DELAY = 0.045   # seconds between rows starting


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC} — run prep_photo.py first")

    img = Image.open(SRC).convert("L")
    w, h = img.size
    rows = max(1, int(COLS * (h / w) * CHAR_ASPECT))
    img = img.resize((COLS, rows))
    px = img.load()

    n = len(RAMP) - 1
    grid = []
    for y in range(rows):
        line = "".join(RAMP[int(px[x, y] / 255 * n)] for x in range(COLS))
        grid.append(line.rstrip())  # trailing spaces are invisible anyway

    svg_w = COLS * CH_W + 20
    svg_h = rows * CH_H + 20

    row_svgs = []
    for i, line in enumerate(grid):
        if not line:
            continue
        y = 16 + i * CH_H
        delay = i * ROW_DELAY
        line_w = len(line) * CH_W
        text = (line.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))
        clip_id = f"clip{i}"
        # a clip-rect grows from width 0 -> line_w to reveal the row
        row_svgs.append(f'''
    <clipPath id="{clip_id}"><rect x="10" y="{y-CH_H}" width="0" height="{CH_H+4}">
      <animate attributeName="width" from="0" to="{line_w}" dur="0.35s"
               begin="{delay:.3f}s" fill="freeze"/>
    </rect></clipPath>
    <text x="10" y="{y}" clip-path="url(#{clip_id})"
          xml:space="preserve">{text}</text>
    <rect x="10" y="{y-CH_H+2}" width="{CH_W}" height="{CH_H}" fill="{FILL}" opacity="0">
      <animate attributeName="x" from="10" to="{10+line_w}" dur="0.35s"
               begin="{delay:.3f}s" fill="freeze"/>
      <animate attributeName="opacity" values="0;1;1;0" dur="0.35s"
               begin="{delay:.3f}s" fill="freeze"/>
    </rect>''')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}"
     viewBox="0 0 {svg_w} {svg_h}">
  <style>
    text {{ font-family: ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
            font-size: {CH_H-2}px; fill: {FILL}; letter-spacing: 0; }}
  </style>
  <rect width="{svg_w}" height="{svg_h}" rx="8" fill="{BG}"/>
  {''.join(row_svgs)}
</svg>'''

    OUT.write_text(svg)
    print(f"Wrote {OUT} ({COLS}x{rows} chars).")


if __name__ == "__main__":
    main()
