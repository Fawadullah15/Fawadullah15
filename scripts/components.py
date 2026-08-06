"""
components.py - Reusable SVG components for the GitHub profile.

A lightweight wrapper to generate consistent SVGs using the theme system.
"""

from typing import List, Optional
from theme import COLORS, px
from utils import font_face, _esc

class SVGElement:
    def render(self) -> str:
        raise NotImplementedError

class Group(SVGElement):
    def __init__(self, children: List[SVGElement], x: float = 0, y: float = 0, class_name: str = "", style: str = ""):
        self.children = children
        self.x = x
        self.y = y
        self.class_name = class_name
        self.style = style

    def render(self) -> str:
        attrs = []
        if self.x or self.y:
            attrs.append(f'transform="translate({self.x}, {self.y})"')
        if self.class_name:
            attrs.append(f'class="{self.class_name}"')
        if self.style:
            attrs.append(f'style="{self.style}"')
        
        attr_str = " ".join(attrs)
        open_tag = f"<g {attr_str}>" if attr_str else "<g>"
        
        inner = "".join(c.render() for c in self.children)
        return f"{open_tag}\n{inner}\n</g>\n"

class Rect(SVGElement):
    def __init__(self, w: float, h: float, fill: str = "none", stroke: str = "none", 
                 stroke_width: float = 0, rx: float = 0, opacity: float = 1.0):
        self.w = w
        self.h = h
        self.fill = fill
        self.stroke = stroke
        self.stroke_width = stroke_width
        self.rx = rx
        self.opacity = opacity

    def render(self) -> str:
        return (f'<rect width="{self.w}" height="{self.h}" fill="{self.fill}" '
                f'stroke="{self.stroke}" stroke-width="{self.stroke_width}" '
                f'rx="{self.rx}" opacity="{self.opacity}"/>\n')

class Text(SVGElement):
    def __init__(self, text: str, x: float = 0, y: float = 0, size: float = 12, 
                 color: str = COLORS["text_sec"], weight: str = "400", 
                 anchor: str = "start", spacing: float = 0, family: str = "primary"):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.weight = weight
        self.anchor = anchor
        self.spacing = spacing
        
        if family == "primary":
            self.font = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
        elif family == "mono":
            self.font = "'JB', 'JetBrains Mono', 'Courier New', Courier, monospace"
        else:
            self.font = family

    def render(self) -> str:
        ls = f'letter-spacing="{self.spacing}em" ' if self.spacing else ""
        return (f'<text x="{self.x}" y="{self.y}" font-family="{self.font}" '
                f'font-size="{self.size}" fill="{self.color}" font-weight="{self.weight}" '
                f'text-anchor="{self.anchor}" {ls}dominant-baseline="auto">'
                f'{_esc(self.text)}</text>\n')

class SVGDoc:
    def __init__(self, w: float, h: float):
        self.w = w
        self.h = h
        self.children: List[SVGElement] = []
        self.defs: List[str] = []

    def add(self, element: SVGElement):
        self.children.append(element)
        
    def add_def(self, def_str: str):
        self.defs.append(def_str)

    def render(self) -> str:
        ff = font_face("data", "JB")
        
        # Base animations (invisible polish)
        styles = f"""
        {ff}
        @keyframes fadeUp {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .animate-in {{ animation: fadeUp 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }}
        """

        defs_xml = f"<defs>\n{chr(10).join(self.defs)}\n</defs>\n" if self.defs else ""
        
        inner = "".join(c.render() for c in self.children)
        
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">\n'
                f'<style>{styles}</style>\n'
                f'{defs_xml}'
                f'<rect width="{self.w}" height="{self.h}" fill="{COLORS["bg"]}"/>\n'
                f'{inner}'
                f'</svg>\n')
