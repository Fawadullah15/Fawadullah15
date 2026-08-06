"""
gen_stats.py — Unified GitHub Analytics SVGs.

Four outputs:
  stats.svg  — Bento grid: commits/PRs/issues/stars/repos/followers
  streak.svg — Current streak + longest streak, elegant layout
  langs.svg  — Language distribution (monochrome, clean bars)
  year.svg   — 365-day contribution heatmap (accent opacity scale)

All styled in one coherent visual language.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, COLORS, RADIUS,
    svg_open, svg_close, text_el, rect_el, circle_el, line_el,
    group_open, group_close, _esc, staggered,
    graphql, utc_now, window_dates, font_face
)

# ── GraphQL query ──────────────────────────────────────────────────────────────
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    name
    login
    followers { totalCount }
    repositories(
      first: 100
      privacy: PUBLIC
      ownerAffiliations: OWNER
      orderBy: { field: UPDATED_AT, direction: DESC }
    ) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""


def fetch(login: str) -> dict:
    from_dt, to_dt = window_dates()
    return graphql(QUERY, {"login": login, "from": from_dt, "to": to_dt})


def extract_days(data: dict) -> list:
    days = []
    for week in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in week["contributionDays"]:
            days.append((d["date"], d["contributionCount"]))
    days.sort(key=lambda x: x[0])
    return days


def compute_streaks(days: list) -> dict:
    cur = best = s_cur = s_best = 0
    cur_from = cur_to = best_from = best_to = s_from = ""
    for date, count in days:
        if count > 0:
            if s_cur == 0:
                s_from = date
            s_cur += 1
            if s_cur > s_best:
                s_best = s_cur
                best_from = s_from
                best_to = date
        else:
            s_cur = 0
            s_from = ""
    cur = 0
    for date, count in reversed(days):
        if count > 0:
            cur += 1
            if cur == 1:
                cur_to = date
            cur_from = date
        else:
            break
    return {
        "current": cur, "current_from": cur_from, "current_to": cur_to,
        "longest": s_best, "longest_from": best_from, "longest_to": best_to,
    }


def extract_langs(data: dict) -> list:
    totals: dict[str, int] = defaultdict(int)
    for repo in data["user"]["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            totals[edge["node"]["name"]] += edge["size"]
    return sorted(totals.items(), key=lambda x: -x[1])


def weekly_totals(days: list) -> list:
    weeks: dict[str, int] = defaultdict(int)
    for date, count in days:
        d = datetime.strptime(date, "%Y-%m-%d")
        weeks[d.strftime("%G-W%V")] += count
    return [weeks[k] for k in sorted(weeks)]


def fmt_date(d1: str, d2: str) -> str:
    if not d1:
        return "—"
    def f(s):
        try:
            dt = datetime.strptime(s, "%Y-%m-%d")
            return dt.strftime("%b %-d") if sys.platform != "win32" else dt.strftime("%b %d").lstrip("0")
        except Exception:
            return s
    return f(d1) if d1 == d2 else f"{f(d1)} – {f(d2)}"


# ── stats.svg ─────────────────────────────────────────────────────────────────

def gen_stats(data: dict, days: list) -> str:
    W, H = 820, 160
    cc    = data["user"]["contributionsCollection"]
    total = cc["contributionCalendar"]["totalContributions"]
    commits  = cc["totalCommitContributions"]
    prs      = cc["totalPullRequestContributions"]
    issues   = cc["totalIssueContributions"]
    repos    = data["user"]["repositories"]["totalCount"]
    stars    = sum(r["stargazerCount"] for r in data["user"]["repositories"]["nodes"])
    followers = data["user"]["followers"]["totalCount"]

    weeks  = weekly_totals(days)
    max_w  = max(weeks) if weeks else 1
    CX0, CX1, CY0, CY1 = 330, 810, 20, 130
    bar_area_h = CY1 - CY0
    n  = len(weeks)
    bw = max(1, (CX1 - CX0 - n) // n)

    out = svg_open(W, H)
    out += group_open(cls="a-up")

    # ── Left panel: big numbers ──────────────────────────────
    lx = 20
    # Total contributions — oversized anchor number
    out += text_el(lx, 58, f"{total:,}",
                   size=40, color=COLORS["text_hi"], weight="700")
    out += text_el(lx, 78, "contributions · past year",
                   size=10, color=COLORS["dim"], spacing=0.04)

    # Sub-stats
    sub = [
        (f"{commits:,}", "commits"),
        (f"{prs}",       "pull requests"),
        (f"{issues}",    "issues"),
        (f"{stars}",     "stars"),
        (f"{repos}",     "repos"),
        (f"{followers}", "followers"),
    ]
    sx = lx
    for val, lbl in sub:
        out += text_el(sx, 108, val, size=12, color=COLORS["text"], weight="600")
        out += text_el(sx, 124, lbl, size=9,  color=COLORS["dim"])
        sx += 50

    # Divider
    out += line_el(320, 14, 320, H - 14, stroke=COLORS["border"])

    # ── Right panel: weekly sparkline ────────────────────────
    out += text_el(CX0, 14, "weekly activity",
                   size=9, color=COLORS["muted"], spacing=0.06)

    for i, wk in enumerate(weeks):
        bx   = CX0 + i * (bw + 1)
        bh   = int((wk / max_w) * bar_area_h) if max_w else 0
        by   = CY1 - bh
        is_last = i == len(weeks) - 1
        fill = COLORS["accent"] if is_last else COLORS["bg3"]
        if bh > 0:
            out += rect_el(bx, by, bw, bh, fill=fill, rx=1)

    # Baseline
    out += line_el(CX0, CY1, CX1, CY1, stroke=COLORS["border"])
    out += group_close()
    out += svg_close()
    return out


# ── streak.svg ────────────────────────────────────────────────────────────────

def gen_streak(streaks: dict) -> str:
    W, H = 820, 120
    out = svg_open(W, H)

    # ── Current streak ───────────────────────────────────────
    out += group_open(cls="a-up", delay=0.0)
    cx = 110
    cur = streaks["current"]
    cur_range = fmt_date(streaks["current_from"], streaks["current_to"])

    # Large number with accent
    out += text_el(cx, 62, str(cur),
                   size=44, color=COLORS["text_hi"], weight="700", anchor="middle")
    out += text_el(cx, 80, "day streak",
                   size=11, color=COLORS["text_sec"], anchor="middle")
    out += text_el(cx, 98, cur_range,
                   size=9, color=COLORS["dim"], anchor="middle")
    out += text_el(cx, 18, "CURRENT STREAK",
                   size=9, color=COLORS["accent_hi"], anchor="middle", spacing=0.12)
    out += group_close()

    # Divider
    out += line_el(W // 2, 16, W // 2, H - 16, stroke=COLORS["border"])

    # ── Longest streak ───────────────────────────────────────
    out += group_open(cls="a-up", delay=0.1)
    lx  = W // 2 + (W // 2) // 2
    lng = streaks["longest"]
    lng_range = fmt_date(streaks["longest_from"], streaks["longest_to"])

    out += text_el(lx, 62, str(lng),
                   size=44, color=COLORS["text_hi"], weight="700", anchor="middle")
    out += text_el(lx, 80, "longest streak",
                   size=11, color=COLORS["text_sec"], anchor="middle")
    out += text_el(lx, 98, lng_range,
                   size=9, color=COLORS["dim"], anchor="middle")
    out += text_el(lx, 18, "BEST EVER",
                   size=9, color=COLORS["dim"], anchor="middle", spacing=0.12)
    out += group_close()

    out += svg_close()
    return out


# ── langs.svg ─────────────────────────────────────────────────────────────────

# Monochrome descending shades for languages
LANG_MONO = ["#FAFAFA", "#D4D4D8", "#A1A1AA", "#71717A", "#52525B", "#3F3F46", "#27272A", "#18181B"]


def gen_langs(langs: list) -> str:
    W, H = 820, 220
    top = langs[:8]
    total = sum(b for _, b in top) or 1

    out = svg_open(W, H)
    out += group_open(cls="a-up")

    out += text_el(20, 18, "LANGUAGE DISTRIBUTION",
                   size=9, color=COLORS["dim"], weight="600", spacing=0.12)

    bar_x0  = 180
    bar_xmax = 650
    row_h   = 24
    start_y = 36

    for i, (name, size) in enumerate(top):
        pct   = size / total
        bw    = int(pct * (bar_xmax - bar_x0))
        y     = start_y + i * row_h
        shade = LANG_MONO[i % len(LANG_MONO)]
        pct_s = f"{pct * 100:.1f}%"

        # Language name
        out += text_el(20, y + 13, name, size=11, color=COLORS["text"])
        # Track
        out += rect_el(bar_x0, y + 5, bar_xmax - bar_x0, 10,
                       fill=COLORS["bg3"], rx=3)
        # Fill with animate
        if bw > 0:
            delay = staggered(i, 0.1, 0.05)
            out += (
                f'<rect x="{bar_x0}" y="{y + 5}" width="{bw}" height="10" '
                f'rx="3" fill="{shade}" '
                f'style="animation:grow 0.9s cubic-bezier(0.16,1,0.3,1) {delay:.2f}s forwards;'
                f'transform:scaleX(0);transform-origin:{bar_x0}px center;"/>\n'
            )
        # Percentage
        out += text_el(bar_xmax + 10, y + 13, pct_s,
                       size=10, color=COLORS["dim"])

    # Mini stacked bar
    mini_y, mini_h = H - 16, 4
    cursor, mini_w = 20, W - 40
    for i, (name, size) in enumerate(top):
        sw = int((size / total) * mini_w)
        if sw > 0:
            out += rect_el(cursor, mini_y, sw, mini_h,
                           fill=LANG_MONO[i % len(LANG_MONO)], rx=0)
            cursor += sw

    out += group_close()
    out += svg_close()
    return out


# ── year.svg ──────────────────────────────────────────────────────────────────

def gen_year(days: list) -> str:
    W, H = 820, 130

    today = utc_now().date()
    dtc: dict[str, int] = dict(days)
    all_days = []
    for i in range(364, -1, -1):
        d  = today - timedelta(days=i)
        ds = d.strftime("%Y-%m-%d")
        all_days.append((ds, dtc.get(ds, 0)))

    max_c = max(c for _, c in all_days) or 1

    cell_w, cell_h, gap = 12, 12, 2
    grid_x0, grid_y0   = 20, 34

    out = svg_open(W, H)
    out += group_open(cls="a-in")

    out += text_el(20, 20, "CONTRIBUTION ACTIVITY  ·  365 DAYS",
                   size=9, color=COLORS["dim"], weight="600", spacing=0.10)

    # Day-of-week labels
    for dow, lbl in {0: "M", 2: "W", 4: "F"}.items():
        ly = grid_y0 + dow * (cell_h + gap) + cell_h - 1
        out += text_el(8, ly, lbl, size=8, color=COLORS["muted"], anchor="middle")

    for idx, (date, count) in enumerate(all_days):
        d   = datetime.strptime(date, "%Y-%m-%d")
        dow = d.weekday()
        week = idx // 7
        cx  = grid_x0 + week * (cell_w + gap)
        cy  = grid_y0 + dow  * (cell_h + gap)

        if count == 0:
            out += rect_el(cx, cy, cell_w, cell_h, fill=COLORS["bg3"], rx=2)
        else:
            intensity = min(count / max_c, 1.0)
            opacity   = round(0.15 + intensity * 0.85, 2)
            out += rect_el(cx, cy, cell_w, cell_h,
                           fill=COLORS["accent"], rx=2, opacity=opacity)

    # Month labels
    prev_month = None
    for idx, (date, _) in enumerate(all_days):
        d = datetime.strptime(date, "%Y-%m-%d")
        if d.day == 1 or (d.month != prev_month and idx % 7 == 0):
            week = idx // 7
            mx   = grid_x0 + week * (cell_w + gap)
            out += text_el(mx, grid_y0 - 6, d.strftime("%b"),
                           size=8, color=COLORS["muted"])
            prev_month = d.month

    out += group_close()
    out += svg_close()
    return out


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    import os
    login = os.environ.get("GH_LOGIN", "Fawadullah15")
    ASSETS.mkdir(exist_ok=True)

    print(f"  Fetching data for @{login}…")
    data  = fetch(login)
    days  = extract_days(data)
    stk   = compute_streaks(days)
    langs = extract_langs(data)

    svgs = {
        "stats.svg":  gen_stats(data, days),
        "streak.svg": gen_streak(stk),
        "langs.svg":  gen_langs(langs),
        "year.svg":   gen_year(days),
    }

    for name, content in svgs.items():
        out = ASSETS / name
        out.write_text(content, encoding="utf-8")
        print(f"  wrote {name}  ({len(content):,} bytes)")

    print("Done.")


if __name__ == "__main__":
    run()
