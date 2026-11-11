import os, sys
from pathlib import Path

# Paths
ROOT = Path("E:/Projects/Fawadimraj Github/Fawadullah15")
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "scripts"))

# Import updated generators
import utils
import gen_headings
import gen_hero
import gen_building
import gen_skills
import gen_timeline
import gen_projects
import gen_contact
import gen_placeholder_stats

# 1. Headings
print("Writing headings...")
for slug, text in gen_headings.HEADINGS:
    svg = gen_headings.make_heading(text)
    (ASSETS / f"{slug}.svg").write_text(svg, encoding="utf-8")

# 2. Hero
print("Writing hero...")
(ASSETS / "hero.svg").write_text(gen_hero.make_hero(), encoding="utf-8")

# 3. Building
print("Writing building...")
(ASSETS / "building.svg").write_text(gen_building.make_building(), encoding="utf-8")

# 4. Skills
print("Writing skills...")
(ASSETS / "skills.svg").write_text(gen_skills.make_skills(), encoding="utf-8")

# 5. Timeline
print("Writing timeline...")
(ASSETS / "timeline.svg").write_text(gen_timeline.make_timeline(), encoding="utf-8")

# 6. Projects
print("Writing projects...")
(ASSETS / "projects.svg").write_text(gen_projects.gen_projects(gen_projects.PLACEHOLDER_REPOS), encoding="utf-8")

# 7. Contact
print("Writing contact...")
(ASSETS / "contact.svg").write_text(gen_contact.make_contact(), encoding="utf-8")

# 8. Stats, Streak, Langs, Year
print("Writing analytics...")
gen_placeholder_stats.run()

print("ALL SVGS REGENERATED DIRECTLY.")
