"""
gen_placeholder_stats.py — Offline-safe placeholder stats.

Used when GITHUB_TOKEN is unavailable (local preview).
Uses representative dummy data. Same visual output as live stats.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent))
from gen_stats import gen_stats, gen_streak, gen_langs, gen_year
from utils import ASSETS, utc_now

# ── Placeholder data ──────────────────────────────────────────────────────────
import random as _rnd


def _build_weeks_impl():
    weeks = []
    today = utc_now().date()
    start = today - timedelta(days=363)
    for w in range(53):
        days_list = []
        for d in range(7):
            day     = start + timedelta(days=w * 7 + d)
            weekday = day.weekday()
            count   = 0
            if weekday < 5:
                _rnd.seed(w * 7 + d + 42)
                count = _rnd.choices([0, 1, 2, 3, 5, 8, 12],
                                     weights=[25, 20, 20, 15, 10, 6, 4])[0]
            days_list.append({"date": day.strftime("%Y-%m-%d"), "contributionCount": count})
        weeks.append({"contributionDays": days_list})
    return weeks


DATA = {
    "user": {
        "name": "Fawadullah Imraj",
        "login": "Fawadullah15",
        "followers": {"totalCount": 12},
        "repositories": {
            "totalCount": 24,
            "nodes": [
                {"stargazerCount": 8, "forkCount": 2, "languages": {"edges": [{"size": 52000, "node": {"name": "Python"}}, {"size": 14000, "node": {"name": "TypeScript"}}]}},
                {"stargazerCount": 5, "forkCount": 1, "languages": {"edges": [{"size": 38000, "node": {"name": "JavaScript"}}, {"size": 8000, "node": {"name": "HTML"}}]}},
                {"stargazerCount": 3, "forkCount": 0, "languages": {"edges": [{"size": 22000, "node": {"name": "Python"}}, {"size": 6000, "node": {"name": "CSS"}}]}},
                {"stargazerCount": 2, "forkCount": 0, "languages": {"edges": [{"size": 18000, "node": {"name": "TypeScript"}}, {"size": 4000, "node": {"name": "Dockerfile"}}]}},
            ],
        },
        "contributionsCollection": {
            "totalCommitContributions": 1103,
            "totalPullRequestContributions": 22,
            "totalIssueContributions": 9,
            "contributionCalendar": {
                "totalContributions": 1134,
                "weeks": _build_weeks_impl(),
            },
        },
    }
}


def run() -> None:
    from gen_stats import extract_days, compute_streaks, extract_langs
    ASSETS.mkdir(exist_ok=True)

    days  = extract_days(DATA)
    stk   = compute_streaks(days)
    langs = extract_langs(DATA)

    svgs = {
        "stats.svg":  gen_stats(DATA, days),
        "streak.svg": gen_streak(stk),
        "langs.svg":  gen_langs(langs),
        "year.svg":   gen_year(days),
    }
    for name, content in svgs.items():
        out = ASSETS / name
        out.write_text(content, encoding="utf-8")
        print(f"  wrote {name}")

    print("Done — placeholder stats.")


if __name__ == "__main__":
    run()
