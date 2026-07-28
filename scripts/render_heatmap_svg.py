#!/usr/bin/env python3
"""
render_heatmap_svg.py
Turn data/contributions.json into contrib-heatmap.svg:
a 53-week x 7-day calendar of rounded boxes that slide in diagonally
(top-left -> bottom-right) once on load, then freeze. No looping.

Pure SVG + CSS keyframes so GitHub renders + animates it inside <img>.
"""
import json
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

# GitHub-ish green ramp; index 5 is a neon top end for big days.
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 13          # box size
GAP = 3            # gap between boxes
PAD = 20           # outer padding
TOP = 54           # space for title + weekday labels
LABEL_COL = 30     # space on the left for weekday labels

DOW_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}
MONTH_ABBR = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level_to_color(level: int) -> str:
    return PALETTE[min(max(level, 0), 5)]


def main() -> None:
    data = json.loads(DATA.read_text())
    days = data["days"]

    # Build a date->day map, then lay out into GitHub's week columns.
    by_date = {d["date"]: d for d in days}
    first = dt.date.fromisoformat(days[0]["date"])
    last = dt.date.fromisoformat(days[-1]["date"])

    # GitHub weeks start on Sunday. Column = weeks since the first Sunday.
    start_sunday = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    weeks = ((last - start_sunday).days // 7) + 1

    grid_w = LABEL_COL + weeks * (CELL + GAP)
    width = grid_w + PAD * 2
    height = TOP + 7 * (CELL + GAP) + 46  # + footer

    rects = []
    month_marks = []
    seen_months = set()

    for w in range(weeks):
        for dow in range(7):  # 0=Sun .. 6=Sat
            cur = start_sunday + dt.timedelta(days=w * 7 + dow)
            if cur < first or cur > last:
                continue
            iso = cur.isoformat()
            day = by_date.get(iso)
            level = day["level"] if day else 0
            count = day["count"] if day else 0
            x = PAD + LABEL_COL + w * (CELL + GAP)
            y = TOP + dow * (CELL + GAP)
            delay = (w + dow) * 0.012  # diagonal stagger
            title = (f"{count} contribution{'s' if count != 1 else ''} on {iso}"
                     if count else f"No contributions on {iso}")
            rects.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                f'fill="{level_to_color(level)}" class="c" '
                f'style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )
            # month label on the first row when the month changes
            if dow == 0 and cur.month not in seen_months and cur.day <= 7:
                seen_months.add(cur.month)
                month_marks.append(
                    f'<text x="{x}" y="{TOP - 8}" class="mlabel">'
                    f'{MONTH_ABBR[cur.month]}</text>'
                )

    # weekday labels
    dow_texts = []
    for dow, label in DOW_LABELS.items():
        y = TOP + dow * (CELL + GAP) + CELL - 2
        dow_texts.append(
            f'<text x="{PAD}" y="{y}" class="dlabel">{label}</text>')

    # legend + footer
    legend_y = TOP + 7 * (CELL + GAP) + 22
    legend = [f'<text x="{PAD}" y="{legend_y + 10}" class="foot">'
              f'{data["total_last_year"]:,} contributions in the last year'
              f'</text>']
    lx = width - PAD - (len(PALETTE) * (CELL + 2)) - 70
    legend.append(f'<text x="{lx - 8}" y="{legend_y + 10}" '
                  f'class="foot" text-anchor="end">Less</text>')
    for i, c in enumerate(PALETTE):
        legend.append(
            f'<rect x="{lx + i * (CELL + 2)}" y="{legend_y}" width="{CELL}" '
            f'height="{CELL}" rx="3" fill="{c}"/>')
    legend.append(f'<text x="{lx + len(PALETTE) * (CELL + 2) + 6}" '
                  f'y="{legend_y + 10}" class="foot">More</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">
  <style>
    .c {{ opacity: 0; transform-box: fill-box; transform-origin: center;
          animation: pop .45s ease-out forwards; }}
    @keyframes pop {{
      0%   {{ opacity: 0; transform: translateY(-6px) scale(.4); }}
      70%  {{ opacity: 1; transform: translateY(0) scale(1.12); }}
      100% {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    .title {{ fill:#39d353; font-size:14px; font-weight:600; }}
    .mlabel {{ fill:#8b949e; font-size:10px; }}
    .dlabel {{ fill:#8b949e; font-size:9px; }}
    .foot   {{ fill:#8b949e; font-size:11px; }}
  </style>
  <rect width="{width}" height="{height}" fill="#0d1117" rx="8"/>
  <text x="{PAD}" y="26" class="title">contribution graph</text>
  {''.join(month_marks)}
  {''.join(dow_texts)}
  {''.join(rects)}
  {''.join(legend)}
</svg>'''

    OUT.write_text(svg)
    print(f"Wrote {OUT} ({weeks} weeks, {len(rects)} day cells).")


if __name__ == "__main__":
    main()
