"""
gen_products.py - Generate the Featured Products SVG.

Creates massive, detailed "product pages" for the top repositories.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from theme import COLORS, px
from components import SVGDoc, Group, Text, Rect
from data import get_top_repositories
from utils import _esc

def build_products(repos: list) -> str:
    W = 800
    CARD_H = 340
    GAP = 40
    H = len(repos) * (CARD_H + GAP)
    
    doc = SVGDoc(W, H)
    
    for i, repo in enumerate(repos):
        y_offset = i * (CARD_H + GAP)
        delay = i * 0.2
        
        g = Group(children=[], x=40, y=y_offset, class_name="animate-in", style=f"animation-delay: {delay}s")
        
        # Card Background
        g.children.append(Rect(w=W-80, h=CARD_H, fill=COLORS["card"], stroke=COLORS["border"], stroke_width=1, rx=12))
        
        # Cover Graphic Area (Top Half)
        COVER_H = 160
        g.children.append(Rect(w=W-80, h=COVER_H, fill=COLORS["bg_sec"], rx=12))
        # Mask bottom corners of cover so it blends into card
        # Using a group to provide the y-offset since Rect has no x or y

        # Wait, I didn't add x, y to Rect in components.py. 
        # I'll just use a Group to translate a Rect if I need offsets.
        
        # We need an offset for cover bottom
        cover_bottom = Group(children=[Rect(w=W-80, h=20, fill=COLORS["bg_sec"])], y=COVER_H-20)
        g.children.append(cover_bottom)
        
        # Typographic Cover Logo
        name = repo.get("name", "Unknown").upper()
        cover_text = Group(children=[
            Text(name, x=(W-80)/2, y=COVER_H/2 + 10, size=28, color=COLORS["border"], weight="800", anchor="middle", spacing=0.1)
        ])
        g.children.append(cover_text)
        
        # Separator line
        sep = Group(children=[Rect(w=W-80, h=1, fill=COLORS["border"])], y=COVER_H)
        g.children.append(sep)
        
        # Content Area
        content_y = COVER_H + 30
        
        # Title
        title_group = Group(children=[
            Text(repo.get("name", ""), x=30, y=0, size=20, color=COLORS["text"], weight="600")
        ], y=content_y)
        g.children.append(title_group)
        
        # Description
        desc = repo.get("description") or "No description provided."
        # Simple wrap
        desc_words = desc.split()
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
            
        desc_group = Group(children=[], y=content_y + 30)
        for li, dl in enumerate(d_lines[:3]):
            desc_group.children.append(Text(dl, x=30, y=li*20, size=13, color=COLORS["text_sec"]))
        g.children.append(desc_group)
        
        # Metrics / Footer
        footer_y = CARD_H - 30
        
        lang = "Unknown"
        if repo.get("primaryLanguage"):
            lang = repo["primaryLanguage"]["name"]
            
        stars = repo.get("stargazerCount", 0)
        forks = repo.get("forkCount", 0)
        
        footer_group = Group(children=[
            Group(children=[Rect(w=W-80, h=1, fill=COLORS["border"])], y=-20)
        ], y=footer_y)
        
        footer_group.children.append(Group(children=[Rect(w=W-80, h=1, fill=COLORS["border"])], y=-20))
        
        footer_group.children.append(Text(f"● {lang}", x=30, y=0, size=12, color=COLORS["text"]))
        footer_group.children.append(Text(f"★ {stars}   ⑂ {forks}", x=140, y=0, size=12, color=COLORS["muted"]))
        
        # Mock Button
        btn_group = Group(children=[
            Rect(w=100, h=30, fill=COLORS["text"], rx=15),
            Text("View Source", x=50, y=19, size=11, color=COLORS["bg"], weight="600", anchor="middle")
        ], x=W-80-130, y=-15)
        
        footer_group.children.append(btn_group)
        g.children.append(footer_group)
        
        doc.add(g)

    return doc.render()

if __name__ == "__main__":
    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    login = "Fawadullah15"
    repos = get_top_repositories(login, limit=3)
    if not repos:
        # Fallback for testing
        repos = [
            {"name": "Shop-Management", "description": "A high-performance full-stack POS system.", "stargazerCount": 12, "forkCount": 2, "primaryLanguage": {"name": "Python"}},
            {"name": "AI-Agents", "description": "Multi-agent framework using LangGraph.", "stargazerCount": 5, "forkCount": 0, "primaryLanguage": {"name": "Jupyter Notebook"}},
            {"name": "PDF-to-Excel", "description": "Automated data extraction tool.", "stargazerCount": 3, "forkCount": 1, "primaryLanguage": {"name": "Python"}}
        ]
        
    svg = build_products(repos)
    (assets_dir / "products.svg").write_text(svg, encoding="utf-8")
    print("Wrote assets/products.svg")
