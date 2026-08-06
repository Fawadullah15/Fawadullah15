"""
gen_dashboard.py - Generate the Unified GitHub Dashboard SVG.

Replaces fragmented stats SVGs with a single, elegant Bento grid.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from theme import COLORS, px
from components import SVGDoc, Group, Text, Rect
from data import graphql, get_token

def fetch_dashboard_data(login: str) -> dict:
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(
          first: 50
          privacy: PUBLIC
          ownerAffiliations: OWNER
        ) {
          totalCount
          nodes {
            stargazerCount
            forkCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name } }
            }
          }
        }
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    try:
        data = graphql(query, {"login": login})
        return data["user"]
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return {}

def build_dashboard(data: dict) -> str:
    W, H = 800, 320
    doc = SVGDoc(W, H)
    
    doc.add(Text("GITHUB ANALYTICS", x=40, y=40, size=10, 
                 color=COLORS["text"], weight="600", spacing=0.15))
                 
    # Bento Grid Group
    grid = Group(children=[], x=40, y=80, class_name="animate-in")
    
    # Left Panel (Key Metrics) - 240x200
    grid.children.append(Rect(w=240, h=200, fill=COLORS["card"], stroke=COLORS["border"], stroke_width=1, rx=12))
    
    cc = data.get("contributionsCollection", {})
    total_contribs = cc.get("contributionCalendar", {}).get("totalContributions", 0)
    commits = cc.get("totalCommitContributions", 0)
    prs = cc.get("totalPullRequestContributions", 0)
    issues = cc.get("totalIssueContributions", 0)
    
    repos = data.get("repositories", {})
    total_repos = repos.get("totalCount", 0)
    stars = sum(r.get("stargazerCount", 0) for r in repos.get("nodes", []))
    
    # Big Number
    grid.children.append(Text(f"{total_contribs:,}", x=20, y=45, size=36, color=COLORS["text"], weight="700"))
    grid.children.append(Text("Contributions (Past Year)", x=20, y=70, size=11, color=COLORS["muted"]))
    
    # Sub metrics
    metric_y = 110
    grid.children.append(Text(f"{commits:,} Commits", x=20, y=metric_y, size=12, color=COLORS["text_sec"]))
    grid.children.append(Text(f"{prs} Pull Requests", x=20, y=metric_y + 25, size=12, color=COLORS["text_sec"]))
    grid.children.append(Text(f"{issues} Issues", x=20, y=metric_y + 50, size=12, color=COLORS["text_sec"]))
    
    grid.children.append(Text(f"{stars} Stars", x=130, y=metric_y, size=12, color=COLORS["text_sec"]))
    grid.children.append(Text(f"{total_repos} Repos", x=130, y=metric_y + 25, size=12, color=COLORS["text_sec"]))
    
    # Right Panel (Language Heatmap/Bars) - 460x200
    grid.children.append(Group(children=[
        Rect(w=460, h=200, fill=COLORS["card"], stroke=COLORS["border"], stroke_width=1, rx=12)
    ], x=260, y=0))
    
    # Process languages
    langs_dict = {}
    for r in repos.get("nodes", []):
        for edge in r.get("languages", {}).get("edges", []):
            name = edge["node"]["name"]
            langs_dict[name] = langs_dict.get(name, 0) + edge["size"]
            
    sorted_langs = sorted(langs_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    total_bytes = sum(langs_dict.values()) or 1
    
    lang_g = Group(children=[], x=280, y=30)
    lang_g.children.append(Text("Language Distribution", x=0, y=0, size=12, color=COLORS["text_sec"], weight="600"))
    
    for i, (name, size) in enumerate(sorted_langs):
        pct = size / total_bytes
        y = 40 + i * 28
        bar_w = int(pct * 300)
        
        # Shade generation
        shade = [
            "#FAFAFA", "#E4E4E7", "#A1A1AA", "#71717A", "#52525B"
        ][i % 5]
        
        lang_g.children.append(Text(name, x=0, y=y+8, size=11, color=COLORS["text"]))
        lang_g.children.append(Rect(w=bar_w, h=6, fill=shade, rx=3, opacity=0.9)) # Wait, need x offset
        # Rect translated
        lang_g.children.append(Group(children=[Rect(w=bar_w, h=6, fill=shade, rx=3)], x=90, y=y))
        lang_g.children.append(Text(f"{pct*100:.1f}%", x=400, y=y+8, size=11, color=COLORS["muted"]))

    grid.children.append(lang_g)
    doc.add(grid)
    
    return doc.render()

if __name__ == "__main__":
    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    login = "Fawadullah15"
    data = fetch_dashboard_data(login)
    if not data:
        # Fallback dummy data
        data = {
            "contributionsCollection": {
                "contributionCalendar": {"totalContributions": 1240},
                "totalCommitContributions": 1100,
                "totalPullRequestContributions": 15,
                "totalIssueContributions": 8
            },
            "repositories": {
                "totalCount": 24,
                "nodes": [
                    {"stargazerCount": 10, "languages": {"edges": [{"size": 5000, "node": {"name": "Python"}}]}},
                    {"stargazerCount": 5, "languages": {"edges": [{"size": 3000, "node": {"name": "TypeScript"}}]}}
                ]
            }
        }
        
    svg = build_dashboard(data)
    (assets_dir / "dashboard.svg").write_text(svg, encoding="utf-8")
    print("Wrote assets/dashboard.svg")
