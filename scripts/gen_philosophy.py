"""
gen_philosophy.py - Generate the Engineering Philosophy SVG.

Displays core principles in a sleek, horizontal or grid layout.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from theme import COLORS, px
from components import SVGDoc, Group, Text, Rect
from data import load_config

def build_philosophy() -> str:
    config = load_config()
    philosophy = config.get("philosophy", [])
    
    W, H = 800, 240
    doc = SVGDoc(W, H)
    
    # Section Title
    doc.add(Text("ENGINEERING PHILOSOPHY", x=40, y=40, size=10, 
                 color=COLORS["text"], weight="600", spacing=0.15))
                 
    # Three column layout
    col_w = (W - 80 - 40) / 3
    
    for i, item in enumerate(philosophy):
        x = 40 + i * (col_w + 20)
        y = 80
        
        delay = i * 0.15
        g = Group(children=[], class_name="animate-in", style=f"animation-delay: {delay}s")
        
        # Top Accent line
        g.children.append(Rect(w=col_w, h=1, fill=COLORS["border"]))
        g.children.append(Rect(w=20, h=1, fill=COLORS["text_sec"]))
        
        # Title
        g.children.append(Text(item["title"], x=0, y=30, size=14, color=COLORS["text"], weight="500"))
        
        # Description (Wrapped)
        words = item["description"].split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) < 36:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
            
        for li, line in enumerate(lines[:4]):
            g.children.append(Text(line, x=0, y=55 + li*18, size=11, color=COLORS["muted"]))
            
        # Wrap in a translate group
        trans_g = Group(children=[g], x=x, y=y)
        doc.add(trans_g)

    return doc.render()

if __name__ == "__main__":
    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    svg = build_philosophy()
    (assets_dir / "philosophy.svg").write_text(svg, encoding="utf-8")
    print("Wrote assets/philosophy.svg")
