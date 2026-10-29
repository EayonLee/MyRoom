"""The window wall: recessed two-leaf casement, sill, reveal, curtains.

The -X wall carries a tall multi-pane window. Its frame sits in the reveal;
the sill projects into the room and the curtains hang in front of it.
"""
from __future__ import annotations

import math

from lib import geo

from . import dims
from .dims import REVEAL, W, WIN_Y0, WIN_Y1, WIN_Z0, WIN_Z1


def build_window(m: dict) -> None:
    """Two-leaf casement window recessed into the -X wall."""
    col = geo.collection("Room")
    depth = 0.055       # frame face, measured back from the inner wall plane
    fx = 0.055          # frame member width
    mull = 0.075        # central post where the two leaves meet
    wt = 0.060          # frame member depth (along X)
    wy = WIN_Y1 - WIN_Y0
    wz = WIN_Z1 - WIN_Z0
    yc = (WIN_Y0 + WIN_Y1) / 2
    zc = (WIN_Z0 + WIN_Z1) / 2
    xf = -depth - wt / 2

    # Reveal lining: four jambs closing the opening, flush with x = 0 at the
    # room side and running back to the frame.
    geo.box("RevealTop", (REVEAL, wy, 0.018),
            (-REVEAL / 2, yc, WIN_Z1 - 0.009), col=col, mat=m["trim"])
    geo.box("RevealBottom", (REVEAL, wy, 0.018),
            (-REVEAL / 2, yc, WIN_Z0 + 0.009), col=col, mat=m["trim"])
    geo.box("RevealFront", (REVEAL, 0.018, wz),
            (-REVEAL / 2, WIN_Y0 + 0.009, zc), col=col, mat=m["trim"])
    geo.box("RevealBack", (REVEAL, 0.018, wz),
            (-REVEAL / 2, WIN_Y1 - 0.009, zc), col=col, mat=m["trim"])

    # The reference has a visible ledge projecting beyond the plaster.
    sill_front = 0.08
    sill_back = -REVEAL - 0.02
    geo.box("Sill", (sill_front - sill_back, wy + 0.10, 0.030),
            ((sill_front + sill_back) / 2, yc, WIN_Z0 - 0.015),
            col=col, mat=m["trim"])

    # Outer timber frame, inside the reveal.
    geo.box("FrameFront", (wt, fx, wz), (xf, WIN_Y0 + fx / 2, zc),
            col=col, mat=m["trim"])
    geo.box("FrameBack", (wt, fx, wz), (xf, WIN_Y1 - fx / 2, zc),
            col=col, mat=m["trim"])
    geo.box("FrameTop", (wt, wy, fx), (xf, yc, WIN_Z1 - fx / 2),
            col=col, mat=m["trim"])
    geo.box("FrameBot", (wt, wy, fx), (xf, yc, WIN_Z0 + fx / 2),
            col=col, mat=m["trim"])

    # Two leaves share a centre post and a slim horizontal rail, as in the
    # reference. Each leaf carries a glazing bead around its perimeter.
    inner_w = wy - 2 * fx
    inner_h = wz - 2 * fx
    geo.box("MullionV", (wt - 0.008, mull, inner_h + 0.02), (xf, yc, zc),
            col=col, mat=m["trim"])
    rail_z = WIN_Z0 + wz * 0.72
    geo.box("MullionH", (wt - 0.008, inner_w, 0.038),
            (xf, yc, rail_z), col=col, mat=m["trim"])

    leaf_w = (inner_w - mull) / 2
    bead = 0.022
    for i, sign in enumerate((-1, 1)):
        ly = yc + sign * (mull / 2 + leaf_w / 2)
        geo.box(f"Leaf{i}BeadF", (0.02, bead, inner_h),
                (xf + wt / 2 - 0.002, ly - leaf_w / 2 + bead / 2, zc),
                col=col, mat=m["trim"])
        geo.box(f"Leaf{i}BeadB", (0.02, bead, inner_h),
                (xf + wt / 2 - 0.002, ly + leaf_w / 2 - bead / 2, zc),
                col=col, mat=m["trim"])
        geo.box(f"Leaf{i}BeadT", (0.02, leaf_w, bead),
                (xf + wt / 2 - 0.002, ly, WIN_Z1 - fx - bead / 2),
                col=col, mat=m["trim"])
        geo.box(f"Leaf{i}BeadBot", (0.02, leaf_w, bead),
                (xf + wt / 2 - 0.002, ly, WIN_Z0 + fx + bead / 2),
                col=col, mat=m["trim"])

    # Short vertical handle on the centre post below the horizontal rail.
    geo.box("WindowHandle", (0.018, 0.018, 0.10),
            (xf + wt / 2 + 0.006, yc, rail_z - 0.10),
            col=col, mat=m["brass"])

    # Glass, one pane per leaf, sitting on the frame's inner face. A thin slab
    # rather than a plane so it never renders as a single-sided card.
    gx = xf - wt / 2 + 0.012
    for i, sign in enumerate((-1, 1)):
        geo.box(f"Glass{i}", (0.006, leaf_w - 2 * bead + 0.01,
                              inner_h - 2 * bead + 0.01),
                (gx, yc + sign * (mull / 2 + leaf_w / 2), zc),
                col=col, mat=m["glass"])


def build_curtains(m: dict) -> None:
    """A curtain on each side of the window, hung on a rod above the reveal.

    The rod is fixed to the inner wall face and stands 60 mm proud, so the
    panels hang in the room and cover the plaster either side of the opening,
    the way real curtains do. Panels are wide and deep-pleated: a narrow panel
    over a 2.4 m drop reads as a column, not as cloth, so the width is set from
    the opening it has to cover rather than from a guessed absolute.
    """
    col = geo.collection("Room")
    opening = WIN_Y1 - WIN_Y0
    # Each panel covers half the opening plus 120 mm of plaster, gathered at
    # roughly 1.5x its flat width so the pleats have somewhere to go.
    flat = opening / 2 + 0.12
    panel_w = flat * 0.66
    top = WIN_Z1 + 0.17
    bottom = 0.05
    hang_x = 0.058   # rod stand-off from the inner wall face

    for name, cy in (("CurtainNear", WIN_Y0 + 0.02 - panel_w / 2 + 0.06),
                     ("CurtainFar", WIN_Y1 - 0.02 + panel_w / 2 - 0.06)):
        # Local width runs along X, so the panel is turned 90 degrees about Z
        # to hang along the -X wall; its folds then displace into the room.
        geo.curtain(name, (panel_w, top - bottom),
                    location=(hang_x, cy, bottom), folds=9, amplitude=0.028,
                    rotation=(0.0, 0.0, math.pi / 2), col=col,
                    mat=m["curtain"])

    # Rod spanning both panels, with two brackets into the plaster.
    # Cover both gathered panels, including their outer edges.
    rod_y0, rod_y1 = WIN_Y0 - panel_w + 0.08, WIN_Y1 + panel_w - 0.08
    geo.cylinder("CurtainRod", 0.011, rod_y1 - rod_y0,
                 (hang_x, (rod_y0 + rod_y1) / 2, top + 0.02),
                 rotation=(math.pi / 2, 0, 0), col=col, mat=m["brass"],
                 segments=16)
    for i, by in enumerate((rod_y0 + 0.05, rod_y1 - 0.05)):
        geo.box(f"RodBracket{i}", (0.05, 0.02, 0.05),
                (hang_x - 0.03, by, top + 0.02), col=col, mat=m["brass"])
