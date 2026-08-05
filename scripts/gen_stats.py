"""
gen_stats.py — Generate GitHub statistics SVGs.

Output files:
  assets/stats.svg    — total contributions + weekly sparkline
  assets/streak.svg   — current streak / longest streak
  assets/langs.svg    — top languages by bytes (horizontal bars)
  assets/year.svg     — 365-day contribution grid (one char/day)

Requires ONLY Python standard library.
Uses GITHUB_TOKEN environment variable (no PAT needed, workflow token works).
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    ASSETS, FONTS, COLORS, RAMP, _esc, font_face,
    graphql, window_dates, utc_now,
    label, bar_h, rule, svg_open, svg_close,
)

# ─────────────────────────────────────────────────────────────────────────────
# GraphQL query
# ─────────────────────────────────────────────────────────────────────────────

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
        name
        stargazerCount
        forkCount
        primaryLanguage { name }
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch_data(login: str) -> dict:
    from_dt, to_dt = window_dates()
    return graphql(QUERY, {"login": login, "from": from_dt, "to": to_dt})


# ─────────────────────────────────────────────────────────────────────────────
# Data processing
# ─────────────────────────────────────────────────────────────────────────────

def extract_days(data: dict) -> list[tuple[str, int]]:
    """Return [(date_str, count), ...] for every day in the collection window."""
    days = []
    for week in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in week["contributionDays"]:
            days.append((d["date"], d["contributionCount"]))
    days.sort(key=lambda x: x[0])
    return days


def compute_streaks(days: list[tuple[str, int]]) -> dict:
    """Return current_streak, longest_streak with date ranges."""
    if not days:
        return {"current": 0, "current_from": "", "current_to": "",
                "longest": 0, "longest_from": "", "longest_to": ""}

    cur = 0; cur_from = ""; cur_to = ""
    best = 0; best_from = ""; best_to = ""
    streak = 0; s_from = ""

    for date, count in days:
        if count > 0:
            if streak == 0:
                s_from = date
            streak += 1
            if streak > best:
                best = streak
                best_from = s_from
                best_to = date
        else:
            streak = 0
            s_from = ""

    # Current streak: count backwards from most recent day
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
        "current": cur,
        "current_from": cur_from,
        "current_to":   cur_to,
        "longest":      best,
        "longest_from": best_from,
        "longest_to":   best_to,
    }


def extract_languages(data: dict) -> list[tuple[str, int]]:
    """Return [(language, bytes), ...] sorted descending, public repos only."""
    totals: dict[str, int] = defaultdict(int)
    for repo in data["user"]["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            totals[edge["node"]["name"]] += edge["size"]
    return sorted(totals.items(), key=lambda x: -x[1])


def weekly_totals(days: list[tuple[str, int]]) -> list[int]:
    """Group days into ISO weeks; return list of weekly totals."""
    weeks: dict[str, int] = defaultdict(int)
    for date, count in days:
        d = datetime.strptime(date, "%Y-%m-%d")
        iso_week = d.strftime("%G-W%V")   # ISO year + week
        weeks[iso_week] += count
    return [weeks[k] for k in sorted(weeks)]


# ─────────────────────────────────────────────────────────────────────────────
# SVG: stats.svg  (800 × 130)
# ─────────────────────────────────────────────────────────────────────────────

def gen_stats(data: dict, days: list[tuple[str, int]]) -> str:
    W, H = 800, 130
    cc   = data["user"]["contributionsCollection"]
    total = cc["contributionCalendar"]["totalContributions"]
    commits = cc["totalCommitContributions"]
    prs     = cc["totalPullRequestContributions"]
    issues  = cc["totalIssueContributions"]
    repos   = data["user"]["repositories"]["totalCount"]
    stars   = sum(r["stargazerCount"] for r in data["user"]["repositories"]["nodes"])
    followers = data["user"]["followers"]["totalCount"]

    # Weekly sparkline
    weeks = weekly_totals(days)
    max_w = max(weeks) if weeks else 1
    # Chart area: x 340–790, y 20–110
    cx0, cx1, cy0, cy1 = 340, 790, 20, 110
    bar_area_w = cx1 - cx0
    bar_area_h = cy1 - cy0
    n = len(weeks)
    bar_w = max(1, (bar_area_w - n) // n)  # gap of 1px between bars

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        # left border accent
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
    ]

    # ── Left panel: key numbers ──
    lx = 18
    # Total contributions — large accent number
    out.append(
        f'<text x="{lx}" y="52" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="36" fill="{COLORS["accent"]}" font-weight="700">{total:,}</text>'
    )
    out.append(
        f'<text x="{lx}" y="70" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="11" fill="{COLORS["dim"]}" letter-spacing="0.06em">contributions · past year</text>'
    )

    # Sub-stats row
    sub_items = [
        (f"{commits:,}",  "commits"),
        (f"{prs}",        "pull requests"),
        (f"{issues}",     "issues"),
        (f"{stars}",      "stars"),
        (f"{repos}",      "repos"),
        (f"{followers}",  "followers"),
    ]
    sy = 100
    sx = lx
    for val, lbl in sub_items:
        out.append(
            f'<text x="{sx}" y="{sy}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="10" fill="{COLORS["text"]}">{_esc(val)}</text>'
        )
        out.append(
            f'<text x="{sx}" y="{sy + 12}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="9" fill="{COLORS["dim"]}">{_esc(lbl)}</text>'
        )
        sx += 50

    # Divider
    out.append(f'<line x1="330" y1="10" x2="330" y2="{H - 10}" stroke="{COLORS["border"]}" stroke-width="1"/>')

    # ── Right panel: weekly sparkline ──
    out.append(
        f'<text x="{cx0}" y="15" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">weekly contributions</text>'
    )

    for i, wk in enumerate(weeks):
        bx = cx0 + i * (bar_w + 1)
        if max_w == 0:
            bh = 0
        else:
            bh = int((wk / max_w) * bar_area_h)
        by = cy1 - bh
        # Highlight the most recent (last) week
        fill = COLORS["accent"] if i == len(weeks) - 1 else COLORS["muted"]
        if bh > 0:
            out.append(
                f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bh}" '
                f'fill="{fill}" rx="1"/>'
            )

    # Baseline rule
    out.append(f'<line x1="{cx0}" y1="{cy1}" x2="{cx1}" y2="{cy1}" stroke="{COLORS["border"]}" stroke-width="1"/>')

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# SVG: streak.svg  (800 × 100)
# ─────────────────────────────────────────────────────────────────────────────

def fmt_date_range(d1: str, d2: str) -> str:
    """Format 'Jan 1 – Aug 5' from ISO date strings."""
    if not d1:
        return "—"
    def f(s: str) -> str:
        try:
            dt = datetime.strptime(s, "%Y-%m-%d")
            return dt.strftime("%b %-d") if sys.platform != "win32" else dt.strftime("%b %d").lstrip("0")
        except Exception:
            return s
    if d1 == d2:
        return f(d1)
    return f"{f(d1)} – {f(d2)}"


def gen_streak(streaks: dict) -> str:
    W, H = 800, 100
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
    ]

    # ── Current streak (left) ──
    cx = 80
    cur = streaks["current"]
    cur_range = fmt_date_range(streaks["current_from"], streaks["current_to"])
    out += [
        f'<text x="{cx}" y="52" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="38" fill="{COLORS["accent"]}" font-weight="700" text-anchor="middle">{cur}</text>',
        f'<text x="{cx}" y="68" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="11" fill="{COLORS["text"]}" text-anchor="middle">day streak</text>',
        f'<text x="{cx}" y="84" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" text-anchor="middle">{_esc(cur_range)}</text>',
        f'<text x="18" y="20" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">current streak</text>',
    ]

    # Divider
    out.append(f'<line x1="400" y1="10" x2="400" y2="{H - 10}" stroke="{COLORS["border"]}" stroke-width="1"/>')

    # ── Longest streak (right) ──
    lx = 600
    lng = streaks["longest"]
    lng_range = fmt_date_range(streaks["longest_from"], streaks["longest_to"])
    out += [
        f'<text x="{lx}" y="52" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="38" fill="{COLORS["accent2"]}" font-weight="700" text-anchor="middle">{lng}</text>',
        f'<text x="{lx}" y="68" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="11" fill="{COLORS["text"]}" text-anchor="middle">longest streak</text>',
        f'<text x="{lx}" y="84" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" text-anchor="middle">{_esc(lng_range)}</text>',
        f'<text x="418" y="20" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">all-time best</text>',
    ]

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# SVG: langs.svg  (800 × 200)
# ─────────────────────────────────────────────────────────────────────────────

# Language → hex color mapping (a curated subset)
LANG_COLORS: dict[str, str] = {
    "Python":       "#3776ab",
    "TypeScript":   "#3178c6",
    "JavaScript":   "#f7df1e",
    "HTML":         "#e44d26",
    "CSS":          "#1572b6",
    "Rust":         "#dea584",
    "Go":           "#00add8",
    "C":            "#555555",
    "C++":          "#f34b7d",
    "Java":         "#b07219",
    "Kotlin":       "#a97bff",
    "Swift":        "#f05138",
    "Ruby":         "#701516",
    "Shell":        "#89e051",
    "Dockerfile":   "#384d54",
    "MDX":          "#fcb32c",
    "Markdown":     "#4a4a4a",
    "YAML":         "#cb171e",
    "JSON":         "#8bc34a",
    "Vue":          "#41b883",
    "Svelte":       "#ff3e00",
}

def lang_color(name: str) -> str:
    return LANG_COLORS.get(name, COLORS["muted"])


def gen_langs(langs: list[tuple[str, int]]) -> str:
    W, H = 800, 200
    top  = langs[:8]  # top 8 languages
    total_bytes = sum(b for _, b in top) or 1

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
        f'<text x="18" y="20" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">top languages · by bytes</text>',
    ]

    bar_x0    = 160
    bar_x_max = 620
    row_h     = 22
    start_y   = 32

    for i, (name, size) in enumerate(top):
        pct   = size / total_bytes
        bar_w = int(pct * (bar_x_max - bar_x0))
        y     = start_y + i * row_h
        col   = lang_color(name)
        pct_s = f"{pct * 100:.1f}%"

        # Language name
        out.append(
            f'<text x="18" y="{y + 13}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="11" fill="{COLORS["text"]}">{_esc(name)}</text>'
        )
        # Track background
        out.append(
            f'<rect x="{bar_x0}" y="{y + 4}" width="{bar_x_max - bar_x0}" height="10" '
            f'fill="{COLORS["bg3"]}" rx="2"/>'
        )
        # Filled bar
        if bar_w > 0:
            out.append(
                f'<rect x="{bar_x0}" y="{y + 4}" width="{bar_w}" height="10" '
                f'fill="{col}" rx="2" opacity="0.85"/>'
            )
        # Percentage label
        out.append(
            f'<text x="{bar_x_max + 8}" y="{y + 13}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="10" fill="{COLORS["dim"]}">{_esc(pct_s)}</text>'
        )

    # Stacked minibar across bottom (full-width color breakdown)
    mini_y  = H - 14
    mini_h  = 4
    cursor  = 18
    mini_w  = W - 36
    for name, size in top:
        seg_w = int((size / total_bytes) * mini_w)
        if seg_w > 0:
            out.append(
                f'<rect x="{cursor}" y="{mini_y}" width="{seg_w}" height="{mini_h}" '
                f'fill="{lang_color(name)}" opacity="0.9"/>'
            )
            cursor += seg_w

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# SVG: year.svg  (800 × 120)
# ─────────────────────────────────────────────────────────────────────────────

def gen_year(days: list[tuple[str, int]]) -> str:
    """365-day contribution grid using the portrait ramp."""
    W, H = 800, 120

    # Pad to exactly 365 days
    today = utc_now().date()
    date_to_count: dict[str, int] = dict(days)
    all_days = []
    for i in range(364, -1, -1):
        d = today - timedelta(days=i)
        ds = d.strftime("%Y-%m-%d")
        all_days.append((ds, date_to_count.get(ds, 0)))

    max_c = max(c for _, c in all_days) or 1

    # Grid layout: 53 weeks × 7 days
    cell_w = 13
    cell_h = 13
    gap    = 2
    grid_x0 = 18
    grid_y0 = 30

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
        f'<text x="18" y="20" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">'
        f'contribution activity · {all_days[0][0][:4]}–{all_days[-1][0][:4]}'
        f'</text>',
    ]

    # Day-of-week labels (Mon, Wed, Fri)
    dow_labels = {0: "M", 2: "W", 4: "F"}
    for dow, lbl in dow_labels.items():
        ly = grid_y0 + dow * (cell_h + gap) + cell_h - 2
        out.append(
            f'<text x="8" y="{ly}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="8" fill="{COLORS["muted"]}" text-anchor="middle">{lbl}</text>'
        )

    # Fill cells
    for idx, (date, count) in enumerate(all_days):
        d    = datetime.strptime(date, "%Y-%m-%d")
        dow  = d.weekday()         # 0=Mon
        week = idx // 7
        cx   = grid_x0 + week * (cell_w + gap)
        cy   = grid_y0 + dow  * (cell_h + gap)

        if count == 0:
            fill = COLORS["bg3"]
        else:
            intensity = min(count / max_c, 1.0)
            # Map 0→1 to accent with varying opacity
            fill = COLORS["accent"]
            alpha = int(30 + intensity * 225)
            # Use opacity instead of rgba (SVG compatible)
            opacity = f'{0.12 + intensity * 0.88:.2f}'
            out.append(
                f'<rect x="{cx}" y="{cy}" width="{cell_w}" height="{cell_h}" '
                f'fill="{COLORS["accent"]}" opacity="{opacity}" rx="2"/>'
            )
            continue

        out.append(
            f'<rect x="{cx}" y="{cy}" width="{cell_w}" height="{cell_h}" '
            f'fill="{fill}" rx="2"/>'
        )

    # Month labels along top
    prev_month = None
    for idx, (date, _) in enumerate(all_days):
        d = datetime.strptime(date, "%Y-%m-%d")
        if d.day == 1 or (d.month != prev_month and idx % 7 == 0):
            week = idx // 7
            mx   = grid_x0 + week * (cell_w + gap)
            out.append(
                f'<text x="{mx}" y="{grid_y0 - 4}" '
                f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
                f'font-size="8" fill="{COLORS["muted"]}">{d.strftime("%b")}</text>'
            )
            prev_month = d.month

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run() -> None:
    import os
    login = os.environ.get("GH_LOGIN", "Fawadullah15")
    ASSETS.mkdir(exist_ok=True)

    print(f"  Fetching data for @{login}...")
    data  = fetch_data(login)
    days  = extract_days(data)
    stk   = compute_streaks(days)
    langs = extract_languages(data)

    print(f"  {len(days)} days · {len(langs)} languages")
    print(f"  Streak: current={stk['current']} longest={stk['longest']}")

    svgs = {
        "stats.svg":  gen_stats(data, days),
        "streak.svg": gen_streak(stk),
        "langs.svg":  gen_langs(langs),
        "year.svg":   gen_year(days),
    }

    for name, content in svgs.items():
        out = ASSETS / name
        out.write_text(content, encoding="utf-8")
        print(f"  Wrote {name} ({len(content):,} bytes)")

    print("Done.")


if __name__ == "__main__":
    run()
