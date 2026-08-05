"""
gen_fonts.py — Pre-generate JetBrains Mono woff2 font subsets.

Requires: fonttools + brotli  (pip install fonttools brotli)
Downloads JetBrains Mono Regular from GitHub releases.

Run this ONCE (via the init workflow) to generate:
  fonts/ramp.b64      — 13 ramp chars for portrait
  fonts/heading.b64   — heading label chars
  fonts/data.b64      — data/stats label chars (basic Latin, two weights)

These .b64 files are then committed and embedded into every SVG.
Font is SIL OFL 1.1 — safe for public repo distribution.
"""

import sys
import os
import base64
import urllib.request
import tempfile
from pathlib import Path

ROOT  = Path(__file__).parent.parent
FONTS = ROOT / "fonts"

JB_URL = (
    "https://github.com/JetBrains/JetBrainsMono/releases/download/"
    "v2.304/JetBrainsMono-2.304.zip"
)

RAMP_CHARS   = ' .`:-=+*cs#%@'
HEADING_CHARS = ' abcdefghijklmnopqrstuvwxyz./'
DATA_CHARS   = (
    ' 0123456789abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '.,%-+/:·★⑂—·\''
)


def download_font(url: str, dest: Path) -> None:
    print(f"  Downloading {url} ...")
    urllib.request.urlretrieve(url, dest)
    print(f"  Saved → {dest}")


def subset_to_b64(ttf_path: Path, chars: str, output_name: str) -> None:
    """Subset a TTF to the given chars and save as base64 woff2."""
    try:
        from fontTools.subset import main as ft_subset
    except ImportError:
        print("  fonttools not found — run: pip install fonttools brotli")
        return

    FONTS.mkdir(exist_ok=True)
    out_path = FONTS / f"{output_name}.woff2"
    b64_path = FONTS / f"{output_name}.b64"

    # Build subset
    args = [
        str(ttf_path),
        f"--text={chars}",
        "--flavor=woff2",
        "--layout-features=",
        "--no-hinting",
        f"--output-file={out_path}",
    ]
    ft_subset(args)

    # Encode to base64
    data = out_path.read_bytes()
    b64  = base64.b64encode(data).decode("ascii")
    b64_path.write_text(b64, encoding="ascii")

    print(f"  {output_name}.b64: {len(data):,} bytes raw → {len(b64):,} chars base64")


def run() -> None:
    import zipfile

    FONTS.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "jbmono.zip"
        download_font(JB_URL, zip_path)

        print("  Extracting...")
        with zipfile.ZipFile(zip_path) as zf:
            # Find the Regular TTF inside the zip
            ttf_names = [n for n in zf.namelist() if "Regular" in n and n.endswith(".ttf")]
            if not ttf_names:
                raise RuntimeError("Could not find Regular TTF in zip")
            ttf_name = ttf_names[0]
            zf.extract(ttf_name, tmp_path)
            ttf_path = tmp_path / ttf_name
        print(f"  TTF: {ttf_path.name}")

        subset_to_b64(ttf_path, RAMP_CHARS,    "ramp")
        subset_to_b64(ttf_path, HEADING_CHARS, "heading")
        subset_to_b64(ttf_path, DATA_CHARS,    "data")

    # Copy the SIL OFL licence
    lic_src = ROOT / "fonts" / "LICENSE"
    if not lic_src.exists():
        print("  fonts/LICENSE not found — add it manually from jetbrains.com/mono")

    print("Done — commit the .b64 files.")


if __name__ == "__main__":
    run()
