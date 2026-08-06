"""
theme.py - The Visual Identity System

Layered neutral colors, font settings, and layout parameters.
"""

# The Layered Neutral Palette
COLORS = {
    "bg":       "#09090B", # Background
    "bg_sec":   "#111113", # Secondary
    "card":     "#18181B", # Card
    "border":   "#2A2A2F", # Border
    "text":     "#FAFAFA", # Primary Text
    "text_sec": "#A1A1AA", # Secondary Text
    "muted":    "#71717A", # Muted
}

# 8pt grid system parameters
GRID = 8

def px(multiplier: float) -> float:
    """Return spacing in pixels based on the 8pt grid."""
    return GRID * multiplier
