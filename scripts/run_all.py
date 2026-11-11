import sys
from pathlib import Path

# Setup paths
repo_root = Path("E:/Projects/Fawadimraj Github/Fawadullah15")
scripts_dir = repo_root / "scripts"
assets_dir = repo_root / "assets"
assets_dir.mkdir(exist_ok=True)
sys.path.insert(0, str(scripts_dir))

print("=== Generating all SVG assets ===")

# 1. gen_headings.py
try:
    import gen_headings
    print("Generating headings...")
    for slug, text in gen_headings.HEADINGS:
        svg = gen_headings.make_heading(text)
        (assets_dir / f"{slug}.svg").write_text(svg, encoding="utf-8")
    print(f"  Generated {len(gen_headings.HEADINGS)} heading SVGs.")
except Exception as e:
    print(f"Error in gen_headings: {e}")

# 2. gen_hero.py
try:
    import gen_hero
    print("Generating hero...")
    hero_svg = gen_hero.make_hero()
    (assets_dir / "hero.svg").write_text(hero_svg, encoding="utf-8")
    print("  Generated hero.svg")
except Exception as e:
    print(f"Error in gen_hero: {e}")

# 3. gen_building.py
try:
    import gen_building
    print("Generating building...")
    b_svg = gen_building.make_building()
    (assets_dir / "building.svg").write_text(b_svg, encoding="utf-8")
    print("  Generated building.svg")
except Exception as e:
    print(f"Error in gen_building: {e}")

# 4. gen_skills.py
try:
    import gen_skills
    print("Generating skills...")
    s_svg = gen_skills.make_skills()
    (assets_dir / "skills.svg").write_text(s_svg, encoding="utf-8")
    print("  Generated skills.svg")
except Exception as e:
    print(f"Error in gen_skills: {e}")

# 5. gen_timeline.py
try:
    import gen_timeline
    print("Generating timeline...")
    t_svg = gen_timeline.make_timeline()
    (assets_dir / "timeline.svg").write_text(t_svg, encoding="utf-8")
    print("  Generated timeline.svg")
except Exception as e:
    print(f"Error in gen_timeline: {e}")

# 6. gen_projects.py
try:
    import gen_projects
    print("Generating projects...")
    p_svg = gen_projects.gen_projects(gen_projects.PLACEHOLDER_REPOS)
    (assets_dir / "projects.svg").write_text(p_svg, encoding="utf-8")
    print("  Generated projects.svg")
except Exception as e:
    print(f"Error in gen_projects: {e}")

# 7. gen_contact.py
try:
    import gen_contact
    print("Generating contact...")
    c_svg = gen_contact.make_contact()
    (assets_dir / "contact.svg").write_text(c_svg, encoding="utf-8")
    print("  Generated contact.svg")
except Exception as e:
    print(f"Error in gen_contact: {e}")

# 8. gen_placeholder_stats.py
try:
    import gen_placeholder_stats
    print("Generating placeholder stats (stats, streak, langs, year)...")
    gen_placeholder_stats.run()
    print("  Generated stats SVGs.")
except Exception as e:
    print(f"Error in gen_placeholder_stats: {e}")

print("=== Assets Generation Complete ===")
