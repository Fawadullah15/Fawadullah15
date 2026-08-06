"""
gen_hero.py - Generate the cinematic Hero SVG.

Edge-to-edge luxury spacing, massive typography, subtle glow.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from theme import COLORS, px
from components import SVGDoc, Group, Text, Rect

def build_hero() -> str:
    W, H = 800, 360
    doc = SVGDoc(W, H)
    
    # Glow definitions (subtle mesh-like gradient)
    doc.add_def('''
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#FAFAFA" stop-opacity="0.04"/>
        <stop offset="100%" stop-color="#09090B" stop-opacity="0"/>
    </radialGradient>
    ''')
    
    # Background Glow
    doc.add(Rect(W, H, fill="url(#glow)", opacity=1.0))
    
    main_group = Group(children=[], class_name="animate-in")
    
    # Top label
    main_group.children.append(
        Text("AI ENGINEER · FULL STACK DEVELOPER", x=W/2, y=H/2 - 40, size=10, 
             color=COLORS["text_sec"], weight="500", anchor="middle", spacing=0.3)
    )
    
    # Cinematic Name
    main_group.children.append(
        Text("FAWADULLAH IMRAJ", x=W/2, y=H/2 + 10, size=48, 
             color=COLORS["text"], weight="800", anchor="middle", spacing=0.02)
    )
    
    # Mission Statement
    main_group.children.append(
        Text("Crafting intelligent systems. Merging AI research with production-grade engineering.", 
             x=W/2, y=H/2 + 60, size=12, 
             color=COLORS["muted"], weight="400", anchor="middle", spacing=0.01)
    )
    
    # Hairline divider at bottom
    main_group.children.append(
        Rect(w=W, h=1, fill=COLORS["border"], opacity=1.0)
    )
    # Actually wait, SVG elements don't accept W=, H= like that in Rect constructor natively if I didn't define it perfectly.
    # Let me add the divider manually or check my Rect definition.
    # Rect(w, h, fill, stroke...)
    
    doc.add(main_group)
    
    # Bottom Hairline Divider (separate from main animation or inside it)
    doc.add(Rect(w=W-160, h=1, fill=COLORS["border"], opacity=0.5)) 
    # Will need to set x and y, Rect doesn't have x,y in components.py. 
    # I can wrap it in a Group with translate.
    div_group = Group(children=[Rect(w=W-120, h=1, fill=COLORS["border"])], x=60, y=H-1)
    doc.add(div_group)

    return doc.render()

if __name__ == "__main__":
    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    svg = build_hero()
    (assets_dir / "hero.svg").write_text(svg, encoding="utf-8")
    print("Wrote assets/hero.svg")
