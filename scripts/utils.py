"""
utils.py — Unified design system & shared utilities.

Design tokens, SVG primitives, GitHub API helpers.
One visual language. One source of truth.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).parent.parent
ASSETS = ROOT / "assets"
FONTS  = ROOT / "fonts"

# ── Design Tokens ─────────────────────────────────────────────────────────────
# Layered neutrals — feels premium, never harsh
COLORS = {
    # Backgrounds
    "bg":        "#09090B",   # Absolute base — deepest
    "bg2":       "#111113",   # Secondary surface
    "bg3":       "#18181B",   # Card surface
    "bg4":       "#1C1C1F",   # Elevated card

    # Borders
    "border":    "#2A2A2F",   # Subtle border
    "border2":   "#3A3A40",   # Active border

    # Text hierarchy
    "text_hi":   "#FAFAFA",   # Headings / primary
    "text":      "#E4E4E7",   # Body
    "text_sec":  "#A1A1AA",   # Secondary / labels
    "dim":       "#71717A",   # Muted / metadata
    "muted":     "#52525B",   # Very muted

    # Accent — ONE premium color (electric indigo, sophisticated)
    "accent":    "#6366F1",   # Indigo — AI / tech feel
    "accent_lo": "#4338CA",   # Darker accent
    "accent_hi": "#818CF8",   # Lighter accent / glow
    "accent_bg": "#1E1B4B",   # Accent tint background
}

# Typography scale (8pt grid base)
TYPE = {
    "xs":    9,
    "sm":   11,
    "base": 13,
    "md":   15,
    "lg":   18,
    "xl":   24,
    "2xl":  32,
    "3xl":  48,
    "hero": 64,
}

# Spacing (8pt grid)
SPACE = {i: i * 8 for i in range(1, 16)}

# Border radius system
RADIUS = {
    "sm":  4,
    "md":  8,
    "lg": 12,
    "xl": 16,
    "pill": 999,
}

# Animation timing
EASING = "cubic-bezier(0.16, 1, 0.3, 1)"
DUR_FAST   = "0.3s"
DUR_BASE   = "0.6s"
DUR_SLOW   = "1.0s"
DUR_SLOWER = "1.4s"

RAMP = " .`:-=+*cs#%@"

# ── Font loading ───────────────────────────────────────────────────────────────

def _load_b64(name: str) -> str | None:
    path = FONTS / f"{name}.b64"
    if path.exists():
        return path.read_text(encoding="ascii").strip()
    return None


def font_face(subset: str = "data", family: str = "JB") -> str:
    b64 = _load_b64(subset)
    if b64:
        return (
            f'@font-face{{font-family:"{family}";'
            f'src:url("data:font/woff2;base64,{b64}") format("woff2");}}'
        )
    return (
        f'@font-face{{font-family:"{family}";'
        f'src:local("JetBrains Mono"),local("Courier New");}}'
    )


# ── Shared SVG style block ─────────────────────────────────────────────────────

def base_style(extra: str = "") -> str:
    ff = font_face("data")
    return f"""
{ff}
* {{
  font-family: "JB", "JetBrains Mono", "Courier New", Courier, monospace;
  box-sizing: border-box;
}}
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(6px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes fadeIn {{
  from {{ opacity:0; }}
  to   {{ opacity:1; }}
}}
@keyframes slideRight {{
  from {{ opacity:0; transform:translateX(-8px); }}
  to   {{ opacity:1; transform:translateX(0); }}
}}
@keyframes pulse {{
  0%,100% {{ opacity:1; }}
  50%     {{ opacity:0.4; }}
}}
@keyframes glow {{
  0%,100% {{ filter:drop-shadow(0 0 4px {COLORS["accent"]}88); }}
  50%     {{ filter:drop-shadow(0 0 12px {COLORS["accent"]}cc); }}
}}
@keyframes grow {{
  from {{ transform:scaleX(0); transform-origin:left; }}
  to   {{ transform:scaleX(1); transform-origin:left; }}
}}
.a-up   {{ animation: fadeUp    {DUR_BASE} {EASING} forwards; opacity:0; }}
.a-in   {{ animation: fadeIn    {DUR_BASE} {EASING} forwards; opacity:0; }}
.a-right {{ animation: slideRight {DUR_BASE} {EASING} forwards; opacity:0; }}
.a-glow {{ animation: glow 3s ease-in-out infinite; }}
.a-pulse {{ animation: pulse 2s ease-in-out infinite; }}
.a-grow {{ animation: grow {DUR_SLOW} {EASING} forwards; transform:scaleX(0); }}
{extra}
""".strip()


def svg_open(w: int, h: int, extra_style: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<style>\n{base_style(extra_style)}\n</style>\n'
        f'<rect width="{w}" height="{h}" fill="{COLORS["bg"]}"/>\n'
    )


def svg_close() -> str:
    return "</svg>\n"


# ── SVG Primitives ─────────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def text_el(x, y, content, size=13, color=None, weight="400",
            anchor="start", spacing=None, cls="", opacity=1.0) -> str:
    col = color or COLORS["text"]
    ls = f' letter-spacing="{spacing}em"' if spacing else ""
    c  = f' class="{cls}"' if cls else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{ls}{c}{op} '
        f'dominant-baseline="auto">{_esc(str(content))}</text>\n'
    )


def rect_el(x, y, w, h, fill=None, rx=0, stroke=None, sw=1,
            cls="", opacity=1.0) -> str:
    col  = fill or COLORS["bg3"]
    s    = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    c    = f' class="{cls}"' if cls else ""
    op   = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" rx="{rx}"{s}{c}{op}/>\n'


def line_el(x1, y1, x2, y2, stroke=None, sw=1, opacity=1.0) -> str:
    col = stroke or COLORS["border"]
    op  = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{sw}"{op}/>\n'


def circle_el(cx, cy, r, fill=None, opacity=1.0, cls="") -> str:
    col = fill or COLORS["accent"]
    op  = f' opacity="{opacity}"' if opacity != 1.0 else ""
    c   = f' class="{cls}"' if cls else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"{op}{c}/>\n'


def bar_h(x, y, w, h, fill, rx=2) -> str:
    return rect_el(x, y, w, h, fill=fill, rx=rx)


def rule(x1, y, x2, stroke=None) -> str:
    return line_el(x1, y, x2, y, stroke=stroke)


def label(x, y, text, size=11, color=None, anchor="start", weight="400") -> str:
    return text_el(x, y, text, size=size, color=color or COLORS["dim"],
                   anchor=anchor, weight=weight)


def group_open(cls="", delay=0, x=0, y=0) -> str:
    parts = []
    if x or y:
        parts.append(f'transform="translate({x},{y})"')
    if cls:
        style = f'style="animation-delay:{delay:.2f}s"' if delay else ""
        parts.append(f'class="{cls}"')
        if style:
            parts.append(style)
    return f'<g {" ".join(parts)}>\n'


def group_close() -> str:
    return "</g>\n"


def staggered(index: int, base_delay: float = 0.0, step: float = 0.1) -> float:
    return base_delay + index * step


# ── Gradient defs ──────────────────────────────────────────────────────────────

def accent_gradient_h(id_="accentH", x1=0, y1=0, x2=1, y2=0) -> str:
    return (
        f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'gradientUnits="objectBoundingBox">'
        f'<stop offset="0%" stop-color="{COLORS["accent"]}"/>'
        f'<stop offset="100%" stop-color="{COLORS["accent_hi"]}"/>'
        f'</linearGradient>'
    )


def fade_right_gradient(id_="fadeR") -> str:
    return (
        f'<linearGradient id="{id_}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{COLORS["border"]}" stop-opacity="1"/>'
        f'<stop offset="100%" stop-color="{COLORS["bg"]}" stop-opacity="0"/>'
        f'</linearGradient>'
    )


# ── GitHub API ─────────────────────────────────────────────────────────────────

GRAPHQL_URL = "https://api.github.com/graphql"


def graphql(query: str, variables: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set.")
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Fawadullah15-profile/2.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"GraphQL HTTP {e.code}: {body}") from e
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def rest_get(path: str) -> object:
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}" if token else "",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Fawadullah15-profile/2.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ── Date helpers ───────────────────────────────────────────────────────────────

def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def window_dates() -> tuple[str, str]:
    today   = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
    from_dt = today - timedelta(days=364)
    to_dt   = today.replace(hour=23, minute=59, second=59)
    return (
        from_dt.isoformat().replace("+00:00", "Z"),
        to_dt.isoformat().replace("+00:00", "Z"),
    )
