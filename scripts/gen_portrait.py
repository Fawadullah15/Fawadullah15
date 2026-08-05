"""
gen_portrait.py — ASCII portrait generator for Fawadullah15.

Two modes:
  1. PHOTO mode  — assets/portrait_input.jpg exists → Pillow pipeline
  2. PLACEHOLDER — no photo → geometric placeholder art

Output: assets/portrait.svg
  - JetBrains Mono, 90 columns, rows ≈ cols × (h/w) × 0.48
  - SMIL typing animation: each row wipes left→right, fill="freeze"
  - Cursor block rides the wipe edge per row
  - No loop — portrait prints once and stops
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import ASSETS, FONTS, COLORS, font_face, _esc

# ── Constants ──────────────────────────────────────────────────────────────────
RAMP      = " .`:-=+*cs#%@"   # 13 brightness levels (leading space = white/blank)
COLS      = 90
CHAR_W    = 7.74               # px per character — JetBrains Mono 0.600 em at 12.9px
FONT_SIZE = 12.9
LINE_H    = FONT_SIZE * 1.2    # line height px
ROW_DELAY = 0.075              # seconds between rows starting
ROW_DUR   = 0.38               # seconds to wipe one row
PAD_X     = 4
PAD_Y     = 6

SVG_W     = int(COLS * CHAR_W + PAD_X * 2)


# ── Ramp mapping ──────────────────────────────────────────────────────────────

def brightness_to_char(v: float) -> str:
    """Map 0.0 (dark) → 1.0 (bright) to a ramp character."""
    idx = int(v * (len(RAMP) - 1))
    return RAMP[max(0, min(idx, len(RAMP) - 1))]


# ── Image pipeline (Pillow) ────────────────────────────────────────────────────

def process_photo(path: Path) -> list[str]:
    """
    Full photo-to-ASCII pipeline.
    Requires: Pillow  (pip install Pillow)
    """
    try:
        from PIL import Image, ImageFilter, ImageOps
    except ImportError:
        print("Pillow not found — falling back to placeholder.")
        return make_placeholder()

    # Attempt background removal (optional — rembg)
    img = Image.open(path).convert("RGBA")
    try:
        from rembg import remove as rembg_remove
        img = rembg_remove(img)
        # White out the removed background so it maps to blank ramp
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg.convert("L")
    except ImportError:
        img = img.convert("L")

    rows = int(COLS * (img.height / img.width) * 0.48)
    img  = img.resize((COLS, rows), Image.LANCZOS)

    # Bilateral-like smoothing via box filter × 2 (no OpenCV in stdlib)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.SMOOTH_MORE)

    # CLAHE approximation via Pillow equalize + blend
    equalized = ImageOps.equalize(img)
    img = Image.blend(img, equalized, alpha=0.55)

    pixels = img.load()
    result = []
    for r in range(rows):
        row = ""
        for c in range(COLS):
            v = pixels[c, r] / 255.0
            # Darkening curve: (v)^1.7 — makes mid-tones darker, preserves edges
            v = v ** 1.7
            row += brightness_to_char(v)
        result.append(row)
    return result


# ── Placeholder art ───────────────────────────────────────────────────────────

def make_placeholder() -> list[str]:
    """
    Generate a placeholder ASCII art when no portrait photo is provided.
    Draws a stylized 'F' monogram inside a decorative frame.
    Replace assets/portrait_input.jpg and re-run to use a real portrait.
    """
    ROWS = int(COLS * 1.5 * 0.48)  # aspect ~1.5 tall
    rows: list[str] = []

    for r in range(ROWS):
        y = r / ROWS   # 0.0 → 1.0
        row = ""
        for c in range(COLS):
            x = c / COLS  # 0.0 → 1.0

            # Outer border frame (2-char thick)
            on_border = (c < 2 or c >= COLS - 2 or r < 2 or r >= ROWS - 2)
            on_inner  = (c == 3 or c == COLS - 3 or r == 3 or r == ROWS - 3)

            if on_border:
                row += "#"
            elif on_inner:
                row += "="
            else:
                # Draw a stylised "F" centered
                cx = c - COLS // 2 + 2
                cy = r - ROWS // 2

                # Vertical stem: x in [-2, 2], full height
                in_stem = (-2 <= cx <= 2)
                # Top bar: y in [-ROWS//4-2, -ROWS//4+2], x in [-2, COLS//4]
                in_top  = (-ROWS // 4 - 2 <= cy <= -ROWS // 4 + 2) and (-2 <= cx <= COLS // 6)
                # Mid bar: y in [-2, 2], x in [-2, COLS//6]
                in_mid  = (-2 <= cy <= 2) and (-2 <= cx <= COLS // 7)

                if in_stem:
                    row += "%" if (-1 <= cx <= 1) else "c"
                elif in_top or in_mid:
                    row += "*" if (cx % 4 == 0) else "="
                else:
                    # background texture — subtle dot pattern
                    if (c + r) % 9 == 0:
                        row += "."
                    elif (c * 2 + r * 3) % 17 == 0:
                        row += "`"
                    else:
                        row += " "
        rows.append(row)
    return rows


# ── SVG builder ───────────────────────────────────────────────────────────────

def build_svg(rows: list[str]) -> str:
    nrows = len(rows)
    svg_h = int(nrows * LINE_H + PAD_Y * 2 + 4)

    # Font
    b64_path = FONTS / "ramp.b64"
    if b64_path.exists():
        b64  = b64_path.read_text(encoding="ascii").strip()
        face = (
            f'@font-face{{'
            f'font-family:"JB";'
            f'src:url("data:font/woff2;base64,{b64}") format("woff2");'
            f'}}'
        )
    else:
        face = (
            '@font-face{'
            'font-family:"JB";'
            'src:local("JetBrains Mono"),local("Courier New");'
            '}'
        )

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{SVG_W}" height="{svg_h}" viewBox="0 0 {SVG_W} {svg_h}">',
        f'<style>{face}</style>',
        f'<rect width="{SVG_W}" height="{svg_h}" fill="{COLORS["bg"]}"/>',
    ]

    full_text_w = COLS * CHAR_W

    for i, row in enumerate(rows):
        y_base  = PAD_Y + (i + 1) * LINE_H          # text baseline y
        y_top   = PAD_Y + i * LINE_H                 # top of line box
        begin   = f"{i * ROW_DELAY:.3f}s"
        end_t   = i * ROW_DELAY + ROW_DUR

        clip_id = f"c{i}"

        # ClipPath — rect animates width 0 → full
        lines.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="{PAD_X}" y="{y_top:.1f}" '
            f'width="0" height="{LINE_H:.1f}">'
            f'<animate attributeName="width" '
            f'from="0" to="{full_text_w:.1f}" '
            f'begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
            f'</rect>'
            f'</clipPath>'
        )

        # Text row
        escaped = _esc(row)
        lines.append(
            f'<text clip-path="url(#{clip_id})" '
            f'x="{PAD_X}" y="{y_base:.1f}" '
            f'font-family=\'&quot;JB&quot;,&quot;JetBrains Mono&quot;,&quot;Courier New&quot;,Courier,monospace\' '
            f'font-size="{FONT_SIZE}" '
            f'fill="{COLORS["text"]}" '
            f'xml:space="preserve">{escaped}</text>'
        )

        # Cursor block — rides the wipe edge, disappears when row done
        cur_y = y_top
        cur_h = LINE_H - 1
        lines.append(
            f'<rect y="{cur_y:.1f}" width="{CHAR_W:.2f}" height="{cur_h:.1f}" '
            f'fill="{COLORS["accent"]}" opacity="0.8">'
            # x position tracks the wipe
            f'<animate attributeName="x" '
            f'from="{PAD_X}" to="{PAD_X + full_text_w:.1f}" '
            f'begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
            # fade out when row finishes
            f'<animate attributeName="opacity" '
            f'from="0.8" to="0" '
            f'begin="{end_t:.3f}s" dur="0.05s" fill="freeze"/>'
            f'</rect>'
        )

    lines.append('</svg>')
    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    ASSETS.mkdir(exist_ok=True)

    photo_path = ASSETS / "portrait_input.jpg"
    if photo_path.exists():
        print(f"  portrait_input.jpg found — running photo pipeline...")
        rows = process_photo(photo_path)
    else:
        print("  No portrait_input.jpg — generating placeholder art.")
        rows = make_placeholder()

    print(f"  Grid: {COLS} cols × {len(rows)} rows")

    svg = build_svg(rows)
    out = ASSETS / "portrait.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"  Wrote {out}")
    print(f"  SVG size: {len(svg):,} bytes")


if __name__ == "__main__":
    run()
