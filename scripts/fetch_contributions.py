#!/usr/bin/env python3
"""
fetch_contributions.py
Scrape the PUBLIC GitHub contribution calendar (no token, no GraphQL) and
write data/contributions.json with raw days + derived stats.

The calendar HTML lives at:
    https://github.com/users/<username>/contributions
which is the same fragment GitHub's own profile page uses.
"""
import json
import re
import sys
import datetime as dt
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Nicholas69-69"          # <-- your username
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

URL = f"https://github.com/users/{USERNAME}/contributions"
HEADERS = {"User-Agent": "Mozilla/5.0 (profile-art heatmap fetcher)"}

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}


def parse_count_from_tooltip(text: str) -> int:
    """'2 contributions on October 6th.' -> 2 ; 'No contributions...' -> 0"""
    text = text.strip()
    if text.lower().startswith("no contribution"):
        return 0
    m = re.match(r"([\d,]+)\s+contribution", text)
    return int(m.group(1).replace(",", "")) if m else 0


def main() -> None:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Map tooltip target id -> contribution count
    counts: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for", "")
        if target.startswith("contribution-day-component"):
            counts[target] = parse_count_from_tooltip(tip.get_text())

    # Read each day cell: date + level (+ count via tooltip id)
    days: list[dict] = []
    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")
        if not date:
            continue
        level = int(cell.get("data-level", 0))
        cid = cell.get("id", "")
        count = counts.get(cid, 0)
        days.append({"date": date, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])

    total = sum(d["count"] for d in days)

    # streaks (based on any day with count > 0)
    longest = current = run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    # current streak = trailing run up to the last day
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

    # monthly totals
    monthly: dict[str, int] = {}
    for d in days:
        key = d["date"][:7]  # YYYY-MM
        monthly[key] = monthly.get(key, 0) + d["count"]

    payload = {
        "username": USERNAME,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly_totals": monthly,
        "days": days,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT} — {total} contributions, "
          f"{len(days)} days, current streak {current}, longest {longest}.")


if __name__ == "__main__":
    sys.exit(main())
