#!/usr/bin/env python3
"""
make_info_card.py
Hand-author a neofetch-style info card SVG that fades in line by line.
Edit the ROWS below to change your card. Set STATIC=1 for a frozen frame.

    python scripts/make_info_card.py          # animated
    STATIC=1 python scripts/make_info_card.py # frozen (for previews)
"""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

# ---- edit your card here -------------------------------------------------
TITLE = "nicholas@github"
# (key, value) rows. Keys get the accent color, values the light color.
ROWS = [
    ("Role",       "Game Developer  ·  South Africa"),
    ("Now",        "Vehicle survival + FPS prototypes in Unity"),
    ("Learning",   "Shader authoring · profiling · clean architecture"),
    ("Stack",      "Unity · C# · .NET · ShaderLab / HLSL"),
    ("Tools",      "Rider · Visual Studio · Git · Blender"),
    ("Focus",      "Game feel · honest physics · low-end optimisation"),
    ("Open to",    "Junior gameplay/engine roles · freelance · jams"),
    ("Ask me",     "Unity · C# · getting a prototype to a build"),
]
# desert palette to match the banner
ACCENT = "#E9A319"   # amber
ACCENT2 = "#C1440E"  # burnt orange
FG = "#e6e1d6"       # warm off-white
DIM = "#8a8175"
BG = "#0d1117"
# -------------------------------------------------------------------------

PAD = 22
TITLE_Y = 40
ROW_START = 74
ROW_H = 30
KEY_W = 96
WIDTH = 560


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> None:
    height = ROW_START + len(ROWS) * ROW_H + 20
    lines = []

    # title bar (fake terminal dots)
    lines.append(f'<circle cx="{PAD+4}" cy="20" r="5" fill="#ff5f56"/>')
    lines.append(f'<circle cx="{PAD+22}" cy="20" r="5" fill="#ffbd2e"/>')
    lines.append(f'<circle cx="{PAD+40}" cy="20" r="5" fill="#27c93f"/>')
    lines.append(f'<text x="{WIDTH/2}" y="24" text-anchor="middle" '
                 f'class="ttl">{esc(TITLE)}</text>')
    lines.append(f'<line x1="{PAD}" y1="{TITLE_Y+4}" x2="{WIDTH-PAD}" '
                 f'y2="{TITLE_Y+4}" stroke="#21262d" stroke-width="1"/>')

    for i, (k, v) in enumerate(ROWS):
        y = ROW_START + i * ROW_H
        delay = 0 if STATIC else 0.18 + i * 0.14
        cls = "row" if not STATIC else "row static"
        lines.append(
            f'<g class="{cls}" style="animation-delay:{delay:.2f}s">'
            f'<text x="{PAD}" y="{y}" class="key">{esc(k)}</text>'
            f'<text x="{PAD}" y="{y+16}" class="val">'
            f'<tspan class="arrow">&gt; </tspan>{esc(v)}</text>'
            f'</g>'
        )

    anim = "" if STATIC else """
    .row { opacity: 0; transform: translateX(-8px);
           animation: slidein .5s ease-out forwards; }
    @keyframes slidein { to { opacity: 1; transform: translateX(0); } }"""

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}"
     viewBox="0 0 {WIDTH} {height}"
     font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">
  <style>
    .ttl {{ fill:{ACCENT}; font-size:14px; font-weight:600; }}
    .key {{ fill:{ACCENT2}; font-size:12px; font-weight:600;
            letter-spacing:.5px; text-transform:uppercase; }}
    .val {{ fill:{FG}; font-size:13px; }}
    .arrow {{ fill:{ACCENT}; }}
    .static {{ opacity: 1; }}{anim}
  </style>
  <rect width="{WIDTH}" height="{height}" rx="8" fill="{BG}"
        stroke="#21262d" stroke-width="1"/>
  {''.join(lines)}
</svg>'''

    OUT.write_text(svg)
    print(f"Wrote {OUT} ({'static' if STATIC else 'animated'}, {len(ROWS)} rows).")


if __name__ == "__main__":
    main()
