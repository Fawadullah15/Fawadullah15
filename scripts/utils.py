"""
Shared utilities for the Fawadullah15 profile SVG generators.

All code is Python standard library only.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "assets"
FONTS  = ROOT / "fonts"

# ── Design tokens ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":       "#0a0a0f",
    "bg2":      "#10101a",
    "bg3":      "#16162a",
    "border":   "#1e1e35",
    "muted":    "#3d3d5c",
    "dim":      "#5a5a80",
    "text":     "#c8c8d8",
    "text_hi":  "#e8e8f0",
    "accent":   "#6e7ef7",
    "accent2":  "#9b8ff5",
    "green":    "#4ade80",
    "amber":    "#fbbf24",
    "red":      "#f87171",
}

RAMP = " .`:-=+*cs#%@"   # 14 chars, index 0 = blank

# ── Font loading ───────────────────────────────────────────────────────────────

def _load_b64(name: str) -> str | None:
    """Return base64 woff2 string if the pre-generated file exists, else None."""
    path = FONTS / f"{name}.b64"
    if path.exists():
        return path.read_text(encoding="ascii").strip()
    return None


def font_face(subset: str, family: str = "JB") -> str:
    """Return an SVG @font-face block, embedded if available."""
    b64 = _load_b64(subset)
    if b64:
        return (
            f'@font-face{{'
            f'font-family:"{family}";'
            f'src:url("data:font/woff2;base64,{b64}") format("woff2");'
            f'}}'
        )
    # graceful fallback — no embedding, rely on system monospace
    return (
        f'@font-face{{'
        f'font-family:"{family}";'
        f'src:local("JetBrains Mono"),local("Courier New");'
        f'}}'
    )


# ── GitHub GraphQL ─────────────────────────────────────────────────────────────

GRAPHQL_URL = "https://api.github.com/graphql"


def graphql(query: str, variables: dict | None = None) -> dict:
    """Execute a GitHub GraphQL query; returns the JSON response dict."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable is not set. "
            "Export your token before running this script."
        )
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Fawadullah15-profile-generator/1.0",
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
    """Execute a GitHub REST GET request and return parsed JSON."""
    token = os.environ.get("GITHUB_TOKEN", "")
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}" if token else "",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Fawadullah15-profile-generator/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ── Date helpers ───────────────────────────────────────────────────────────────

def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def window_dates() -> tuple[str, str]:
    """
    Return (from, to) ISO strings for a pinned 365-day window aligned to whole
    UTC days.  Two runs minutes apart will produce byte-identical output.
    """
    today = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
    from_dt = today - timedelta(days=364)
    to_dt   = today.replace(hour=23, minute=59, second=59)
    return from_dt.isoformat().replace("+00:00", "Z"), to_dt.isoformat().replace("+00:00", "Z")


# ── SVG primitives ─────────────────────────────────────────────────────────────

def svg_open(w: int, h: int, extra_style: str = "") -> str:
    """Open an SVG document with the standard design system style."""
    ff = font_face("data")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<style>\n'
        f'{ff}\n'
        f'* {{font-family:"JB","JetBrains Mono","Courier New",Courier,monospace;}}\n'
        f'{extra_style}\n'
        f'</style>\n'
        f'<rect width="{w}" height="{h}" fill="{COLORS["bg"]}"/>\n'
    )


def svg_close() -> str:
    return "</svg>\n"


def label(x: int, y: int, text: str, size: int = 11, color: str | None = None,
          anchor: str = "start", weight: str = "400") -> str:
    col = color or COLORS["dim"]
    return (
        f'<text x="{x}" y="{y}" '
        f'font-size="{size}" fill="{col}" '
        f'text-anchor="{anchor}" '
        f'font-weight="{weight}" '
        f'dominant-baseline="auto">{_esc(text)}</text>\n'
    )


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def bar_h(x: int, y: int, w: int, h: int, fill: str, rx: int = 2) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" rx="{rx}"/>\n'


def rule(x1: int, y: int, x2: int, stroke: str | None = None) -> str:
    col = stroke or COLORS["border"]
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="1"/>\n'
