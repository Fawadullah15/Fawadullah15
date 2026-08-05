"""
gen_placeholder_stats.py
─────────────────────────
Generate visually correct but placeholder stats SVGs so the README
renders beautifully on the first push, before GitHub Actions runs.

These will be overwritten by gen_stats.py on the first Action run.
Run this once locally (no token needed).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import ASSETS, COLORS, _esc, font_face

# ── Placeholder data (realistic-looking for a new account) ────────────────────
PLACEHOLDER = {
    "total_contributions": 342,
    "commits":     289,
    "prs":         18,
    "issues":      11,
    "stars":       4,
    "repos":       27,
    "followers":   6,
    "weekly": [
        0, 2, 5, 8, 12, 7, 3, 9, 14, 11, 6, 4, 10, 15, 18, 12, 8, 5,
        11, 16, 20, 14, 9, 6, 12, 17, 22, 16, 11, 8, 14, 19, 24, 18,
        13, 9, 15, 21, 25, 19, 14, 10, 16, 22, 26, 20, 15, 11, 13, 8,
        4, 6, 9,
    ],
    "streak_current": 7,
    "streak_longest": 22,
    "streak_cur_from":  "Jul 29",
    "streak_cur_to":    "Aug 05",
    "streak_lng_from":  "Feb 12",
    "streak_lng_to":    "Mar 05",
    "langs": [
        ("Python",     58),
        ("TypeScript", 21),
        ("HTML",       11),
        ("JavaScript",  6),
        ("CSS",         4),
    ],
    # 365 daily contribution counts
    # 0 = no contribution, higher = more
}

import random, math
random.seed(42)

def fake_daily(n=365):
    """Generate plausible-looking contribution counts for the past year."""
    days = []
    for i in range(n):
        # Simulate more recent activity
        recency = i / n
        # Weekday effect
        dow = i % 7
        weekend = 0.3 if dow >= 5 else 1.0
        base = recency * 4 * weekend
        if random.random() < 0.35:
            days.append(0)
        else:
            days.append(max(0, int(random.gauss(base, 1.5))))
    return days

DAILY_COUNTS = fake_daily(365)

# ── stats.svg ─────────────────────────────────────────────────────────────────

def gen_stats_ph() -> str:
    W, H = 800, 130
    p = PLACEHOLDER
    total   = p["total_contributions"]
    commits = p["commits"]
    prs     = p["prs"]
    issues  = p["issues"]
    stars   = p["stars"]
    repos   = p["repos"]
    followers = p["followers"]
    weeks   = p["weekly"]
    max_w   = max(weeks) or 1

    cx0, cx1, cy0, cy1 = 340, 790, 20, 110
    bar_area_h = cy1 - cy0
    n = len(weeks)
    bar_w = max(1, (cx1 - cx0 - n) // n)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
    ]

    lx = 18
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

    sub_items = [
        (f"{commits:,}", "commits"),
        (f"{prs}",       "pull requests"),
        (f"{issues}",    "issues"),
        (f"{stars}",     "stars"),
        (f"{repos}",     "repos"),
        (f"{followers}", "followers"),
    ]
    sy = 100; sx = lx
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

    out.append(f'<line x1="330" y1="10" x2="330" y2="{H-10}" stroke="{COLORS["border"]}" stroke-width="1"/>')
    out.append(
        f'<text x="{cx0}" y="15" '
        f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
        f'font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">weekly contributions</text>'
    )

    for i, wk in enumerate(weeks):
        bx = cx0 + i * (bar_w + 1)
        bh = int((wk / max_w) * bar_area_h) if max_w else 0
        by = cy1 - bh
        fill = COLORS["accent"] if i == len(weeks) - 1 else COLORS["muted"]
        if bh > 0:
            out.append(f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bh}" fill="{fill}" rx="1"/>')

    out.append(f'<line x1="{cx0}" y1="{cy1}" x2="{cx1}" y2="{cy1}" stroke="{COLORS["border"]}" stroke-width="1"/>')
    out.append('</svg>')
    return "\n".join(out) + "\n"


# ── streak.svg ────────────────────────────────────────────────────────────────

def gen_streak_ph() -> str:
    W, H = 800, 100
    p = PLACEHOLDER
    cur = p["streak_current"]; lng = p["streak_longest"]
    cur_range = f"{p['streak_cur_from']} – {p['streak_cur_to']}"
    lng_range = f"{p['streak_lng_from']} – {p['streak_lng_to']}"

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
    ]

    cx = 80
    out += [
        f'<text x="{cx}" y="52" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="38" fill="{COLORS["accent"]}" font-weight="700" text-anchor="middle">{cur}</text>',
        f'<text x="{cx}" y="68" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="11" fill="{COLORS["text"]}" text-anchor="middle">day streak</text>',
        f'<text x="{cx}" y="84" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="9" fill="{COLORS["dim"]}" text-anchor="middle">{_esc(cur_range)}</text>',
        f'<text x="18" y="20" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">current streak</text>',
        f'<line x1="400" y1="10" x2="400" y2="{H-10}" stroke="{COLORS["border"]}" stroke-width="1"/>',
    ]

    lx = 600
    out += [
        f'<text x="{lx}" y="52" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="38" fill="{COLORS["accent2"]}" font-weight="700" text-anchor="middle">{lng}</text>',
        f'<text x="{lx}" y="68" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="11" fill="{COLORS["text"]}" text-anchor="middle">longest streak</text>',
        f'<text x="{lx}" y="84" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="9" fill="{COLORS["dim"]}" text-anchor="middle">{_esc(lng_range)}</text>',
        f'<text x="418" y="20" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">all-time best</text>',
    ]

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ── langs.svg ─────────────────────────────────────────────────────────────────

LANG_COLORS = {
    "Python":     "#3776ab",
    "TypeScript": "#3178c6",
    "HTML":       "#e44d26",
    "JavaScript": "#f7df1e",
    "CSS":        "#1572b6",
}

def gen_langs_ph() -> str:
    W, H = 800, 200
    langs = PLACEHOLDER["langs"]
    total = sum(b for _, b in langs) or 1

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
        f'<text x="18" y="20" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">top languages · by bytes</text>',
    ]

    bar_x0 = 160; bar_x_max = 620; row_h = 22; start_y = 32
    for i, (name, pct_raw) in enumerate(langs):
        pct  = pct_raw / 100
        bw   = int(pct * (bar_x_max - bar_x0))
        y    = start_y + i * row_h
        col  = LANG_COLORS.get(name, COLORS["muted"])
        pcts = f"{pct * 100:.1f}%"
        out += [
            f'<text x="18" y="{y+13}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="11" fill="{COLORS["text"]}">{_esc(name)}</text>',
            f'<rect x="{bar_x0}" y="{y+4}" width="{bar_x_max-bar_x0}" height="10" fill="{COLORS["bg3"]}" rx="2"/>',
        ]
        if bw > 0:
            out.append(f'<rect x="{bar_x0}" y="{y+4}" width="{bw}" height="10" fill="{col}" rx="2" opacity="0.85"/>')
        out.append(f'<text x="{bar_x_max+8}" y="{y+13}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="10" fill="{COLORS["dim"]}">{_esc(pcts)}</text>')

    mini_y = H - 14; mini_h = 4; cursor = 18; mini_w = W - 36
    for name, pct_raw in langs:
        seg_w = int((pct_raw / 100) * mini_w)
        if seg_w > 0:
            out.append(f'<rect x="{cursor}" y="{mini_y}" width="{seg_w}" height="{mini_h}" fill="{LANG_COLORS.get(name, COLORS["muted"])}" opacity="0.9"/>')
            cursor += seg_w

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ── year.svg ──────────────────────────────────────────────────────────────────

def gen_year_ph() -> str:
    from datetime import date, timedelta
    W, H = 800, 120
    today = date.today()
    counts = DAILY_COUNTS
    max_c = max(counts) or 1

    cell_w = 13; cell_h = 13; gap = 2
    grid_x0 = 18; grid_y0 = 30

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<style>{font_face("data")}</style>',
        f'<rect width="{W}" height="{H}" fill="{COLORS["bg"]}"/>',
        f'<rect x="0" y="0" width="2" height="{H}" fill="{COLORS["accent"]}" rx="0"/>',
        f'<text x="18" y="20" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="9" fill="{COLORS["dim"]}" letter-spacing="0.06em">contribution activity · 365 days</text>',
    ]

    for dow, lbl in {0: "M", 2: "W", 4: "F"}.items():
        ly = grid_y0 + dow * (cell_h + gap) + cell_h - 2
        out.append(f'<text x="8" y="{ly}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="8" fill="{COLORS["muted"]}" text-anchor="middle">{lbl}</text>')

    prev_month = None
    for idx in range(365):
        count = counts[idx]
        d    = today - timedelta(days=364 - idx)
        dow  = d.weekday()
        week = idx // 7
        cx   = grid_x0 + week * (cell_w + gap)
        cy   = grid_y0 + dow  * (cell_h + gap)

        if d.day == 1 and d.month != prev_month:
            out.append(f'<text x="{cx}" y="{grid_y0-4}" font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' font-size="8" fill="{COLORS["muted"]}">{d.strftime("%b")}</text>')
            prev_month = d.month

        if count == 0:
            out.append(f'<rect x="{cx}" y="{cy}" width="{cell_w}" height="{cell_h}" fill="{COLORS["bg3"]}" rx="2"/>')
        else:
            opacity = f'{0.12 + (count/max_c)*0.88:.2f}'
            out.append(f'<rect x="{cx}" y="{cy}" width="{cell_w}" height="{cell_h}" fill="{COLORS["accent"]}" opacity="{opacity}" rx="2"/>')

    out.append('</svg>')
    return "\n".join(out) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    ASSETS.mkdir(exist_ok=True)
    svgs = {
        "stats.svg":  gen_stats_ph(),
        "streak.svg": gen_streak_ph(),
        "langs.svg":  gen_langs_ph(),
        "year.svg":   gen_year_ph(),
    }
    for name, content in svgs.items():
        out = ASSETS / name
        out.write_text(content, encoding="utf-8")
        print(f"  wrote {name}")
    print("Done — placeholder stats SVGs generated.")


if __name__ == "__main__":
    run()
