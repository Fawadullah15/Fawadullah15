"""
gen_timeline.py - Generate the Timeline SVG.

Creates a sleek, vertically stepped timeline for education and experience.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from theme import COLORS, px
from components import SVGDoc, Group, Text, Rect
from data import load_config

def build_timeline() -> str:
    config = load_config()
    timeline = config.get("timeline", [])
    
    W = 800
    ITEM_H = 120
    H = max(400, len(timeline) * ITEM_H + 80)
    doc = SVGDoc(W, H)
    
    # Title
    doc.add(Text("EXPERIENCE & LEADERSHIP", x=40, y=40, size=10, 
                 color=COLORS["text"], weight="600", spacing=0.15))
                 
    # Timeline Group
    tl_group = Group(children=[], x=60, y=100)
    
    for i, item in enumerate(timeline):
        delay = i * 0.15
        g = Group(children=[], y=i * ITEM_H, class_name="animate-in", style=f"animation-delay: {delay}s")
        
        # Continuous vertical line (except for last item)
        if i < len(timeline) - 1:
            line_g = Group(children=[Rect(w=1, h=ITEM_H, fill=COLORS["border"])], x=3, y=14)
            g.children.append(line_g)
            
        # Node dot (glowing for the most recent)
        if i == 0:
            # Active glowing dot
            dot_glow = Group(children=[Rect(w=15, h=15, fill=COLORS["text"], rx=8, opacity=0.2)], x=-4, y=-4)
            dot = Group(children=[Rect(w=7, h=7, fill=COLORS["text"], rx=4)], x=0, y=0)
            g.children.append(dot_glow)
            g.children.append(dot)
        else:
            # Inactive dot
            dot = Group(children=[Rect(w=7, h=7, fill=COLORS["muted"], rx=4)], x=0, y=0)
            g.children.append(dot)
            
        # Year label
        g.children.append(Text(item["year"], x=40, y=8, size=12, color=COLORS["text"], weight="600"))
        
        # Role & Company
        g.children.append(Text(item["role"], x=120, y=8, size=14, color=COLORS["text"], weight="500"))
        g.children.append(Text(item["company"], x=120, y=28, size=12, color=COLORS["text_sec"]))
        
        # Description
        desc_words = item["description"].split()
        d_line = ""
        d_lines = []
        for w in desc_words:
            if len(d_line) + len(w) < 80:
                d_line += w + " "
            else:
                d_lines.append(d_line)
                d_line = w + " "
        if d_line:
            d_lines.append(d_line)
            
        for li, dl in enumerate(d_lines[:3]):
            g.children.append(Text(dl, x=120, y=55 + li*20, size=12, color=COLORS["muted"]))
            
        tl_group.children.append(g)

    doc.add(tl_group)
    return doc.render()

if __name__ == "__main__":
    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    svg = build_timeline()
    (assets_dir / "timeline.svg").write_text(svg, encoding="utf-8")
    print("Wrote assets/timeline.svg")
