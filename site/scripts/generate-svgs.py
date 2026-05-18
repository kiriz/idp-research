#!/usr/bin/env python3
"""
generate-svgs.py
Converts .excalidraw files to clean SVGs without requiring a DOM or Canvas.
Handles: rectangle, ellipse, diamond, line, arrow, text
Run: python3 scripts/generate-svgs.py
"""

import json
import os
import math
import html
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SOURCE_DIR = ROOT / "docs/diagrams"
OUTPUT_DIR = ROOT / "site/public/diagrams"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PADDING = 40
FONT_FAMILIES = {1: "sans-serif", 2: "serif", 3: "monospace"}


def hex_with_opacity(color: str, opacity: float) -> str:
    """Convert hex color + opacity to rgba CSS."""
    if color == "transparent" or not color.startswith("#"):
        return "none"
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return f"rgba({r},{g},{b},{opacity:.2f})"


def fill_color(el: dict) -> str:
    bg = el.get("backgroundColor", "transparent")
    if bg == "transparent":
        return "none"
    opacity = el.get("opacity", 100) / 100
    fill_style = el.get("fillStyle", "solid")
    if fill_style in ("hachure", "cross-hatch", "zigzag"):
        return hex_with_opacity(bg, opacity * 0.6)
    return hex_with_opacity(bg, opacity)


def stroke_color(el: dict) -> str:
    sc = el.get("strokeColor", "#000000")
    if sc == "transparent":
        return "none"
    opacity = el.get("opacity", 100) / 100
    return hex_with_opacity(sc, opacity)


def stroke_dash(el: dict) -> str:
    style = el.get("strokeStyle", "solid")
    sw = el.get("strokeWidth", 1)
    if style == "dashed":
        return f'stroke-dasharray="{sw*6},{sw*3}"'
    if style == "dotted":
        return f'stroke-dasharray="{sw},{sw*3}"'
    return ""


def has_roundness(el: dict) -> bool:
    return bool(el.get("roundness"))


def render_rectangle(el: dict) -> str:
    x, y, w, h = el["x"], el["y"], el["width"], el["height"]
    rx = 8 if has_roundness(el) else 0
    sw = el.get("strokeWidth", 1)
    dash = stroke_dash(el)
    angle = el.get("angle", 0)
    cx, cy = x + w / 2, y + h / 2
    transform = f' transform="rotate({math.degrees(angle):.2f} {cx:.2f} {cy:.2f})"' if angle else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill_color(el)}" stroke="{stroke_color(el)}" stroke-width="{sw}" '
        f'{dash}{transform}/>'
    )


def render_ellipse(el: dict) -> str:
    x, y, w, h = el["x"], el["y"], el["width"], el["height"]
    cx, cy = x + w / 2, y + h / 2
    rx, ry = w / 2, h / 2
    sw = el.get("strokeWidth", 1)
    dash = stroke_dash(el)
    angle = el.get("angle", 0)
    transform = f' transform="rotate({math.degrees(angle):.2f} {cx:.2f} {cy:.2f})"' if angle else ""
    return (
        f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" '
        f'fill="{fill_color(el)}" stroke="{stroke_color(el)}" stroke-width="{sw}" '
        f'{dash}{transform}/>'
    )


def render_diamond(el: dict) -> str:
    x, y, w, h = el["x"], el["y"], el["width"], el["height"]
    points = f"{x+w/2:.2f},{y:.2f} {x+w:.2f},{y+h/2:.2f} {x+w/2:.2f},{y+h:.2f} {x:.2f},{y+h/2:.2f}"
    sw = el.get("strokeWidth", 1)
    dash = stroke_dash(el)
    angle = el.get("angle", 0)
    cx, cy = x + w / 2, y + h / 2
    transform = f' transform="rotate({math.degrees(angle):.2f} {cx:.2f} {cy:.2f})"' if angle else ""
    return (
        f'<polygon points="{points}" '
        f'fill="{fill_color(el)}" stroke="{stroke_color(el)}" stroke-width="{sw}" '
        f'{dash}{transform}/>'
    )


def render_line(el: dict) -> str:
    ox, oy = el["x"], el["y"]
    pts = el.get("points", [[0, 0], [el.get("width", 0), el.get("height", 0)]])
    sw = el.get("strokeWidth", 1)
    dash = stroke_dash(el)
    sc = stroke_color(el)
    if len(pts) == 2:
        x1, y1 = ox + pts[0][0], oy + pts[0][1]
        x2, y2 = ox + pts[1][0], oy + pts[1][1]
        return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{sc}" stroke-width="{sw}" {dash}/>'
    coords = " ".join(f"{ox+p[0]:.2f},{oy+p[1]:.2f}" for p in pts)
    return f'<polyline points="{coords}" fill="none" stroke="{sc}" stroke-width="{sw}" {dash}/>'


def render_arrow(el: dict, arrow_id: str) -> tuple[str, str]:
    """Returns (defs_snippet, use_snippet)."""
    ox, oy = el["x"], el["y"]
    pts = el.get("points", [[0, 0], [el.get("width", 0), el.get("height", 0)]])
    sw = el.get("strokeWidth", 1)
    dash = stroke_dash(el)
    sc = stroke_color(el)
    end_head = el.get("endArrowhead")
    start_head = el.get("startArrowhead")

    defs = ""
    marker_end = ""
    marker_start = ""
    if end_head:
        mid = f"arrow-end-{arrow_id}"
        defs += (
            f'<marker id="{mid}" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">'
            f'<polygon points="0 0, 10 3.5, 0 7" fill="{sc}"/></marker>'
        )
        marker_end = f'marker-end="url(#{mid})"'
    if start_head:
        mid = f"arrow-start-{arrow_id}"
        defs += (
            f'<marker id="{mid}" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto-start-reverse">'
            f'<polygon points="0 0, 10 3.5, 0 7" fill="{sc}"/></marker>'
        )
        marker_start = f'marker-start="url(#{mid})"'

    if len(pts) == 2:
        x1, y1 = ox + pts[0][0], oy + pts[0][1]
        x2, y2 = ox + pts[1][0], oy + pts[1][1]
        # Shorten endpoint slightly so marker doesn't overlap
        if end_head and (x2 != x1 or y2 != y1):
            length = math.hypot(x2 - x1, y2 - y1)
            ratio = max(0, (length - sw * 8)) / length
            x2e = x1 + (x2 - x1) * ratio
            y2e = y1 + (y2 - y1) * ratio
        else:
            x2e, y2e = x2, y2
        line = (
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2e:.2f}" y2="{y2e:.2f}" '
            f'stroke="{sc}" stroke-width="{sw}" {dash} {marker_end} {marker_start}/>'
        )
    else:
        # Multi-point: use polyline, shorten last segment
        abs_pts = [(ox + p[0], oy + p[1]) for p in pts]
        if end_head and len(abs_pts) >= 2:
            lx1, ly1 = abs_pts[-2]
            lx2, ly2 = abs_pts[-1]
            length = math.hypot(lx2 - lx1, ly2 - ly1)
            if length > sw * 8:
                ratio = (length - sw * 8) / length
                abs_pts[-1] = (lx1 + (lx2 - lx1) * ratio, ly1 + (ly2 - ly1) * ratio)
        coords = " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in abs_pts)
        line = (
            f'<polyline points="{coords}" fill="none" '
            f'stroke="{sc}" stroke-width="{sw}" {dash} {marker_end} {marker_start}/>'
        )

    return defs, line


def render_text(el: dict) -> str:
    raw = el.get("text", el.get("originalText", ""))
    if not raw:
        return ""
    x, y, w, h = el["x"], el["y"], el["width"], el["height"]
    fs = el.get("fontSize", 16)
    ff = FONT_FAMILIES.get(el.get("fontFamily", 1), "sans-serif")
    sc = stroke_color(el)
    align = el.get("textAlign", "left")
    v_align = el.get("verticalAlign", "top")
    line_height = el.get("lineHeight", 1.25)
    angle = el.get("angle", 0)

    svg_anchor = {"left": "start", "center": "middle", "right": "end"}.get(align, "start")

    if align == "center":
        tx = x + w / 2
    elif align == "right":
        tx = x + w
    else:
        tx = x

    lines = raw.split("\n")
    total_height = len(lines) * fs * line_height

    if v_align == "middle":
        ty_start = y + h / 2 - total_height / 2 + fs
    elif v_align == "bottom":
        ty_start = y + h - total_height + fs
    else:
        ty_start = y + fs

    transform = ""
    if angle:
        cx, cy = x + w / 2, y + h / 2
        transform = f' transform="rotate({math.degrees(angle):.2f} {cx:.2f} {cy:.2f})"'

    parts = []
    for i, line in enumerate(lines):
        ty = ty_start + i * fs * line_height
        escaped = html.escape(line)
        parts.append(
            f'<tspan x="{tx:.2f}" y="{ty:.2f}">{escaped}</tspan>'
        )

    return (
        f'<text font-family="{ff}" font-size="{fs}" fill="{sc}" '
        f'text-anchor="{svg_anchor}"{transform}>'
        + "".join(parts)
        + "</text>"
    )


def compute_bounds(elements: list) -> tuple[float, float, float, float]:
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for el in elements:
        if el.get("isDeleted"):
            continue
        x, y = el.get("x", 0), el.get("y", 0)
        w, h = el.get("width", 0), el.get("height", 0)
        pts = el.get("points")
        if pts:
            for p in pts:
                min_x = min(min_x, x + p[0])
                min_y = min(min_y, y + p[1])
                max_x = max(max_x, x + p[0])
                max_y = max(max_y, y + p[1])
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)
    return min_x, min_y, max_x, max_y


def excalidraw_to_svg(path: Path) -> str:
    data = json.loads(path.read_text())
    elements = [e for e in data.get("elements", []) if not e.get("isDeleted")]

    if not elements:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100"><text x="10" y="50" font-family="sans-serif" font-size="14" fill="#666">Empty diagram</text></svg>'

    min_x, min_y, max_x, max_y = compute_bounds(elements)
    vx = min_x - PADDING
    vy = min_y - PADDING
    vw = (max_x - min_x) + PADDING * 2
    vh = (max_y - min_y) + PADDING * 2

    # Separate bound text elements (rendered inside their container)
    bound_text_ids = set()
    for el in elements:
        for be in el.get("boundElements") or []:
            if be.get("type") == "text":
                bound_text_ids.add(be["id"])

    defs_parts = []
    body_parts = []

    # Render in order: shapes first, then arrows, then text on top
    shape_els = [e for e in elements if e["type"] not in ("arrow", "text")]
    arrow_els = [e for e in elements if e["type"] == "arrow"]
    text_els = [e for e in elements if e["type"] == "text"]

    for el in shape_els:
        t = el["type"]
        if t == "rectangle":
            body_parts.append(render_rectangle(el))
        elif t == "ellipse":
            body_parts.append(render_ellipse(el))
        elif t == "diamond":
            body_parts.append(render_diamond(el))
        elif t == "line":
            body_parts.append(render_line(el))

    for i, el in enumerate(arrow_els):
        defs, line = render_arrow(el, str(i))
        if defs:
            defs_parts.append(defs)
        body_parts.append(line)

    for el in text_els:
        body_parts.append(render_text(el))

    defs_block = f"<defs>{''.join(defs_parts)}</defs>" if defs_parts else ""
    body = "\n  ".join(body_parts)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vx:.2f} {vy:.2f} {vw:.2f} {vh:.2f}" '
        f'width="{vw:.0f}" height="{vh:.0f}">'
        f'<rect width="100%" height="100%" fill="#ffffff"/>'
        f"{defs_block}"
        f"\n  {body}\n"
        f"</svg>"
    )


def main():
    files = sorted(SOURCE_DIR.glob("*.excalidraw"))
    print(f"Found {len(files)} Excalidraw diagrams")
    errors = []
    for f in files:
        name = f.stem
        out = OUTPUT_DIR / f"{name}.svg"
        try:
            svg = excalidraw_to_svg(f)
            out.write_text(svg, encoding="utf-8")
            print(f"  ✓ {name}.svg")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            errors.append((name, str(e)))
    print(f"\nDone — {len(files) - len(errors)}/{len(files)} generated to {OUTPUT_DIR}")
    if errors:
        for name, err in errors:
            print(f"  ERROR: {name}: {err}")


if __name__ == "__main__":
    main()
