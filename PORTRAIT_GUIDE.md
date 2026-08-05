# Adding Your Portrait

The profile ships with a geometric placeholder by default.
Replace it with your actual photo by following these steps.

---

## Photo requirements

The ASCII renderer works with **shadow**, not detail.
It has 13 brightness levels — choose your photo accordingly.

| Requirement | Why |
|-------------|-----|
| Side-lit (window at ~45°) | Creates the shadow gradient the ramp needs |
| Fill the frame — chin to crown | At 90 cols a small face gets ~30 chars wide |
| 1200 px or larger | Thin features like glasses vanish on downscale |
| Plain or blurred background | Dark walls produce `@@@` that swamp the face |
| Slight angle, not dead-on | Gives the nose and jaw a shadow edge |

---

## Steps

**1. Add your photo**

Copy your photo into the `assets/` folder and name it exactly:

```
assets/portrait_input.jpg
```

JPEG or PNG both work — the script reads whichever is there.

**2. Run the portrait generator locally (optional preview)**

```bash
pip install Pillow
python scripts/gen_portrait.py
```

Open `assets/portrait.svg` in a browser to preview.
The portrait types from top to bottom, then freezes.

**3. Commit and push**

```bash
git add assets/portrait_input.jpg assets/portrait.svg
git commit -m "portrait: add photo"
git push
```

**4. Or let the init workflow do it**

If you push `portrait_input.jpg` before running the init workflow,
the workflow will process it automatically:

```
GitHub → Actions → init profile → Run workflow
```

---

## Tuning

Edit these constants in `scripts/gen_portrait.py` if the result
needs adjustment:

```python
COLS      = 90      # character columns — wider = more detail
ROW_DELAY = 0.075   # seconds between rows
ROW_DUR   = 0.38    # seconds to wipe one row
```

The darkening curve `v ** 1.7` in `process_photo()` controls how
aggressively mid-tones become shadow. Increase the exponent for
bolder contrast, decrease it for softer rendering.

---

## Font note

The portrait grid assumes JetBrains Mono's 0.600 em advance
(`CHAR_W = 7.74` at `font-size: 12.9`). After running the init
workflow, the font is embedded in the SVG as a base64 woff2 subset
(~1.3 KB), so the portrait looks identical on every OS and browser.
