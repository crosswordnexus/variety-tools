#!/usr/bin/env python3
"""
Spiral Grid Generator
Generates an SVG representation of a spiral crossword grid of any given length (number of cells),
matching the visual style, geometry, and layer structure of Spiral100.svg.

Usage:
    python3 spiral_grid.py [length] [options]

Examples:
    python3 spiral_grid.py 100
    python3 spiral_grid.py 100 --no-numbers
    python3 spiral_grid.py 80 --font-size 12
    python3 spiral_grid.py 64 -o my_spiral.svg
"""

import argparse
import math
import os
import sys


def F_arc(x, b):
    """Primitive for integrating sqrt(x^2 + b^2)."""
    return (x / 2.0) * math.sqrt(x * x + b * b) + (b * b / 2.0) * math.log(x + math.sqrt(x * x + b * b))


def s_inward(theta, r_out_c, b):
    """
    Arc length along centerline winding inward from theta=0 (outer entrance)
    to theta where radius is r_c(theta) = r_out_c - b*theta.
    """
    v = r_out_c - b * theta
    return (F_arc(r_out_c, b) - F_arc(v, b)) / b


def invert_s_inward(target_s, r_out_c, b, max_theta):
    """Finds theta such that s_inward(theta) == target_s using Newton-Raphson."""
    if target_s <= 0.0:
        return 0.0
    theta = target_s / r_out_c
    for _ in range(15):
        v = r_out_c - b * theta
        diff = s_inward(theta, r_out_c, b) - target_s
        if abs(diff) < 1e-9:
            break
        ds_dtheta = math.sqrt(v * v + b * b)
        theta -= diff / ds_dtheta
        theta = max(0.0, min(max_theta, theta))
    return theta


def generate_spiral_svg(
    num_cells=100,
    show_numbers=True,
    channel_width=50.0,
    inner_radius=62.845,
    turns=None,
    font_size=12.0,
    font_family="'Franklin Gothic Book', Arial, sans-serif",
    number_position="corner",  # "corner" (outer-entrance corner) or "center"
    stroke_width_wall=3.0,
    stroke_width_cap=3.0,
    stroke_width_div=2.0,
    number_direction="inward",  # "inward" (1 at outside -> N at inside) or "outward" (1 at inside -> N at outside)
):
    """
    Generates an SVG string representing a spiral crossword grid of `num_cells` cells.

    Parameters:
        num_cells (int): Total number of cells in the grid.
        show_numbers (bool): Whether to include cell numbers in Layer 3.
        channel_width (float): Track/corridor width in px (default: 50.0).
        inner_radius (float): Centerline radius of the innermost loop (default: 62.845).
        turns (float): Optional exact number of channel revolutions.
        font_size (float): Number text font size (default: 12.0 px).
        font_family (str): Font family string.
        number_position (str): 'corner' (outer-entrance corner) or 'center'.
        stroke_width_wall (float): Stroke width for spiral corridor walls (default: 3.0).
        stroke_width_cap (float): Stroke width for outer and inner end caps (default: 3.0).
        stroke_width_div (float): Stroke width for internal cell divisions (default: 2.0).
        number_direction (str): 'inward' (default) or 'outward'.

    Returns:
        str: Valid SVG markup.
    """
    num_cells = int(num_cells)
    if num_cells < 1:
        raise ValueError("num_cells must be at least 1.")

    W = float(channel_width)
    b = W / (2.0 * math.pi)
    r_in_c = float(inner_radius)

    # In Spiral100.svg: 100 cells span 5 full turns (10*pi) with r_in_c ≈ 62.845,
    # yielding ~59.08 arc length per cell (aspect ratio ~1.18).
    if turns is not None:
        theta_total = float(turns) * 2.0 * math.pi
    else:
        # Benchmark target arc length per cell:
        ref_theta = 10.0 * math.pi
        ref_r_out = r_in_c + b * ref_theta
        ref_total_s = s_inward(ref_theta, ref_r_out, b)
        target_cell_len = ref_total_s / 100.0

        # Approximate theta_total, then refine with Newton-Raphson:
        target_total_s = num_cells * target_cell_len
        disc = r_in_c * r_in_c + 2.0 * b * target_total_s
        theta_total = (-r_in_c + math.sqrt(max(0.0, disc))) / b

        for _ in range(12):
            r_out_test = r_in_c + b * theta_total
            s_test = s_inward(theta_total, r_out_test, b)
            diff = s_test - target_total_s
            if abs(diff) < 1e-9:
                break
            ds = math.sqrt(r_out_test * r_out_test + b * b)
            theta_total -= diff / ds

    r_out_c = r_in_c + b * theta_total
    total_s = s_inward(theta_total, r_out_c, b)
    cell_len = total_s / num_cells

    # Compute division angles along centerline
    div_thetas = []
    for k in range(num_cells + 1):
        target_sk = k * cell_len
        th = invert_s_inward(target_sk, r_out_c, b, theta_total)
        div_thetas.append(th)

    # Polar to Cartesian conversion
    # Clockwise, theta=0 pointing straight up (0, -r)
    def to_cartesian(r, theta, cx, cy):
        x = cx + r * math.sin(theta)
        y = cy - r * math.cos(theta)
        return x, y

    # Compute bounding box
    wall_theta_max = theta_total + 2.0 * math.pi
    sample_steps = max(200, int(wall_theta_max * 20))
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')

    for i in range(sample_steps + 1):
        th = wall_theta_max * i / sample_steps
        r = (r_out_c + W / 2.0) - b * th
        x, y = to_cartesian(r, th, 0.0, 0.0)
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    padding = 10.0
    width = (max_x - min_x) + 2 * padding
    height = (max_y - min_y) + 2 * padding
    cx = padding - min_x
    cy = padding - min_y

    # Build the smooth cubic bezier spiral wall
    num_bezier_segs = max(16, int(math.ceil(wall_theta_max / (math.pi / 8.0))))
    bezier_thetas = [wall_theta_max * i / num_bezier_segs for i in range(num_bezier_segs + 1)]

    def wall_pt_and_deriv(th):
        r = (r_out_c + W / 2.0) - b * th
        x, y = to_cartesian(r, th, cx, cy)
        dx = -b * math.sin(th) + r * math.cos(th)
        dy = b * math.cos(th) + r * math.sin(th)
        return (x, y), (dx, dy)

    path_d_parts = []
    pt0, _ = wall_pt_and_deriv(bezier_thetas[0])
    path_d_parts.append(f"M {pt0[0]:.3f},{pt0[1]:.3f}")

    for i in range(len(bezier_thetas) - 1):
        thA = bezier_thetas[i]
        thB = bezier_thetas[i + 1]
        dth = thB - thA
        (xA, yA), (dxA, dyA) = wall_pt_and_deriv(thA)
        (xB, yB), (dxB, dyB) = wall_pt_and_deriv(thB)
        cp1x = xA + (dth / 3.0) * dxA
        cp1y = yA + (dth / 3.0) * dyA
        cp2x = xB - (dth / 3.0) * dxB
        cp2y = yB - (dth / 3.0) * dyB
        path_d_parts.append(f"C {cp1x:.3f},{cp1y:.3f} {cp2x:.3f},{cp2y:.3f} {xB:.3f},{yB:.3f}")

    wall_path_d = " ".join(path_d_parts)

    # Build cell divisions (Layer 2)
    divisions = []
    for k, th in enumerate(div_thetas):
        r_outer = (r_out_c + W / 2.0) - b * th
        r_inner = r_outer - W
        p_outer = to_cartesian(r_outer, th, cx, cy)
        p_inner = to_cartesian(r_inner, th, cx, cy)
        is_cap = (k == 0 or k == num_cells)
        sw = stroke_width_cap if is_cap else stroke_width_div
        linecap = "round" if is_cap else "butt"
        divisions.append({
            "id": f"division_{k}",
            "d": f"M {p_outer[0]:.3f},{p_outer[1]:.3f} L {p_inner[0]:.3f},{p_inner[1]:.3f}",
            "stroke_width": sw,
            "linecap": linecap,
        })

    # Build numbers (Layer 3)
    text_elements = []
    if show_numbers:
        # Offsets for outer-entrance corner placement:
        # Along corridor: offset from cell start division
        # Radially: offset inward from outer wall
        offset_along = max(7.0, min(14.0, cell_len * 0.20, font_size * 0.9))
        offset_radial = max(6.0, min(14.0, W * 0.22, font_size * 0.85))

        for k in range(num_cells):
            s_start = k * cell_len
            if number_position == "corner":
                s_pos = s_start + offset_along
                th_pos = invert_s_inward(s_pos, r_out_c, b, theta_total)
                r_wall_outer = (r_out_c + W / 2.0) - b * th_pos
                r_num = r_wall_outer - offset_radial
            else:
                # Center placement
                s_pos = s_start + 0.5 * cell_len
                th_pos = invert_s_inward(s_pos, r_out_c, b, theta_total)
                r_num = r_out_c - b * th_pos

            tx, ty = to_cartesian(r_num, th_pos, cx, cy)
            num_val = (k + 1) if number_direction == "inward" else (num_cells - k)
            text_elements.append({
                "id": f"text_cell_{num_val}",
                "number": str(num_val),
                "x": f"{tx:.3f}",
                "y": f"{ty:.3f}",
            })

    # Assemble SVG markup
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg width="{width:.2f}" height="{height:.2f}" viewBox="0 0 {width:.2f} {height:.2f}"',
        '     version="1.1" xmlns="http://www.w3.org/2000/svg"',
        '     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">',
        '  <g id="layer1" inkscape:label="Spiral path" inkscape:groupmode="layer">',
        f'    <path id="spiral_wall" d="{wall_path_d}"',
        f'          style="fill:none;stroke:#000000;stroke-width:{stroke_width_wall};stroke-linecap:round;stroke-linejoin:miter;stroke-opacity:1" />',
        '  </g>',
        '  <g id="layer2" inkscape:label="Cell divisions" inkscape:groupmode="layer">',
    ]

    for div in divisions:
        lines.append(
            f'    <path id="{div["id"]}" d="{div["d"]}" '
            f'style="fill:none;stroke:#000000;stroke-width:{div["stroke_width"]};stroke-linecap:{div["linecap"]};stroke-linejoin:miter;stroke-opacity:1" />'
        )

    lines.append('  </g>')

    if show_numbers and text_elements:
        lines.append('  <g id="layer3" inkscape:label="Text" inkscape:groupmode="layer">')
        for t in text_elements:
            lines.append(
                f'    <text id="{t["id"]}" x="{t["x"]}" y="{t["y"]}" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'style="font-family:{font_family};font-size:{font_size}px;font-weight:normal;fill:#000000;fill-opacity:1;">'
                f'<tspan x="{t["x"]}" y="{t["y"]}" dominant-baseline="central">{t["number"]}</tspan></text>'
            )
        lines.append('  </g>')

    lines.append('</svg>\n')
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an SVG spiral grid of any given length with optional cell numbers."
    )
    parser.add_argument(
        "length",
        type=int,
        nargs="?",
        default=100,
        help="Number of cells in the spiral grid (default: 100).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output SVG filename (default: Spiral<length>.svg).",
    )
    parser.add_argument(
        "--no-numbers",
        action="store_true",
        help="Generate grid without cell numbers.",
    )
    parser.add_argument(
        "--font-size",
        type=float,
        default=16.0,
        help="Font size for cell numbers in pixels (default: 16.0).",
    )
    parser.add_argument(
        "--number-position",
        choices=["corner", "center"],
        default="corner",
        help="Where to place cell numbers: 'corner' (outer-entrance corner) or 'center' (default: corner).",
    )
    parser.add_argument(
        "--channel-width",
        type=float,
        default=50.0,
        help="Width of the spiral track in pixels (default: 50.0).",
    )
    parser.add_argument(
        "--turns",
        type=float,
        default=None,
        help="Exact number of channel revolutions (e.g. 5.0). Default auto-scales to keep cell aspect ratio ~1.18.",
    )
    parser.add_argument(
        "--outward",
        action="store_true",
        help="Number cells outward from center (1 at center, N at outside). Default is inward (1 at outside, N at center).",
    )

    args = parser.parse_args()

    svg_content = generate_spiral_svg(
        num_cells=args.length,
        show_numbers=not args.no_numbers,
        channel_width=args.channel_width,
        turns=args.turns,
        font_size=args.font_size,
        number_position=args.number_position,
        number_direction="outward" if args.outward else "inward",
    )

    if args.output:
        out_path = args.output
    else:
        num_suffix = "_no_numbers" if args.no_numbers else ""
        out_path = f"Spiral{args.length}{num_suffix}.svg"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Generated {out_path} ({args.length} cells, numbers={'off' if args.no_numbers else 'on'}, position={args.number_position}, font_size={args.font_size}px).")


if __name__ == "__main__":
    main()
