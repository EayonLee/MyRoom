"""The half of the room behind the camera: entrance door, tiled stove, switch.

Seen only in reflections and in free-look, but it has to hold up when the
camera turns around, so it is modelled to the same standard as the window wall.
"""
from __future__ import annotations

import math

from lib import geo

from .dims import D, DOOR_CLEAR_H, DOOR_X0, DOOR_X1, H, W


def build_door(m: dict) -> None:
    """Four-panel door in a real opening in the front wall.

    The casing sits proud of the plaster and the leaf is set back inside the
    reveal, so the door reads as a hole with a frame rather than a decal.
    """
    col = geo.collection("Room")
    t = 0.045          # leaf thickness
    y = -0.075         # leaf sits behind the inner wall plane in the reveal
    w = DOOR_X1 - DOOR_X0
    cx = (DOOR_X0 + DOOR_X1) / 2
    casing = 0.075     # casing face width
    proud = 0.022      # how far the casing stands off the wall

    # Casing: two jambs and a head, standing proud of the plaster on the
    # room side (y = +proud/2 puts their front face at y = proud).
    geo.box("DoorCasingL", (casing, proud, DOOR_CLEAR_H + casing),
            (DOOR_X0 - casing / 2, proud / 2, (DOOR_CLEAR_H + casing) / 2),
            col=col, mat=m["trim"])
    geo.box("DoorCasingR", (casing, proud, DOOR_CLEAR_H + casing),
            (DOOR_X1 + casing / 2, proud / 2, (DOOR_CLEAR_H + casing) / 2),
            col=col, mat=m["trim"])
    geo.box("DoorCasingHead", (w + 2 * casing, proud, casing),
            (cx, proud / 2, DOOR_CLEAR_H + casing / 2), col=col, mat=m["trim"])

    # Leaf recessed in the masonry reveal.
    leaf_h = DOOR_CLEAR_H - 0.008
    geo.box("DoorLeaf", (w - 0.008, t, leaf_h),
            (cx, y, leaf_h / 2), col=col, mat=m["door"])

    # Four raised panels: two tall above, two tall below, split at the lock
    # rail. Panel reveals are 60 mm in from the leaf edge.
    inset = 0.075
    pw = w - 2 * inset
    panel_w = (pw - 0.05) / 2
    rail_z = 0.95
    panels = [
        (DOOR_X0 + inset + panel_w / 2, panel_w, rail_z + 0.05,
         leaf_h - 0.10 - (rail_z + 0.05)),
        (cx + 0.025 + panel_w / 2, panel_w, rail_z + 0.05,
         leaf_h - 0.10 - (rail_z + 0.05)),
        (DOOR_X0 + inset + panel_w / 2, panel_w, 0.10, rail_z - 0.15),
        (cx + 0.025 + panel_w / 2, panel_w, 0.10, rail_z - 0.15),
    ]
    for i, (px, pwid, pz, ph) in enumerate(panels):
        geo.box(f"DoorPanel{i}", (pwid, 0.014, ph),
                (px, y + t / 2, pz + ph / 2), col=col, mat=m["door"])
        geo.box(f"DoorPanel{i}Bevel", (pwid + 0.024, 0.008, ph + 0.024),
                (px, y + t / 2 + 0.002, pz + ph / 2), col=col,
                mat=m["door_shade"])

    # Brass lever on the near side of the lock rail, plus the keyhole escutcheon.
    geo.box("DoorLever", (0.115, 0.016, 0.018),
            (DOOR_X1 - 0.09, y + t / 2 + 0.016, rail_z + 0.02),
            col=col, mat=m["brass"])
    geo.cylinder("DoorRose", 0.028, 0.014,
                 (DOOR_X1 - 0.045, y + t / 2 + 0.008, rail_z + 0.02),
                 rotation=(math.pi / 2, 0, 0), col=col, mat=m["brass"],
                 segments=20)
    geo.box("DoorKeyhole", (0.012, 0.008, 0.028),
            (DOOR_X1 - 0.045, y + t / 2 + 0.008, rail_z - 0.06),
            col=col, mat=m["bakelite"])

def build_switch(m: dict) -> None:
    """Bakelite switch on the +X jamb, at the height a hand reaches for it."""
    col = geo.collection("Room")
    sx = DOOR_X1 + 0.20
    geo.box("SwitchPlate", (0.075, 0.016, 0.075),
            (sx, 0.008, 1.32), col=col, mat=m["bakelite"])
    geo.cylinder("SwitchDolly", 0.017, 0.022,
                 (sx, 0.024, 1.32), rotation=(math.pi / 2, 0, 0), col=col,
                 mat=m["bakelite"], segments=18)


def build_stove(m: dict) -> None:
    """Kachelofen in the +X / +Y corner: the tiled mass the room is built around.

    A real stove is a masonry block, so the body is one solid with a stepped
    plinth, a two-band crown and glazed ceramic all over.
    """
    col = geo.collection("Room")
    bx0, bx1 = W - 0.78, W - 0.02
    by0, by1 = D - 0.10, D - 0.86
    bw, bd = bx1 - bx0, by1 - by0
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    body_h = 1.86

    geo.box("Stove", (bw, bd, body_h), (cx, cy, body_h / 2),
            col=col, mat=m["tile"])
    geo.box("StovePlinth", (bw + 0.05, bd + 0.05, 0.11),
            (cx, cy + 0.025, 0.055), col=col, mat=m["bakelite"])

    # Crown: two stepped bands. The upper one oversails, as the moulded top
    # course of a stove always does.
    geo.box("StoveCrownLow", (bw + 0.03, bd + 0.03, 0.05),
            (cx, cy, body_h + 0.025), col=col, mat=m["tile"])
    geo.box("StoveCrownHigh", (bw + 0.07, bd + 0.07, 0.06),
            (cx, cy, body_h + 0.08), col=col, mat=m["bakelite"])

    # Firebox door on the -Y face, with its brass handle and a bed of embers
    # behind the draft slots.
    fy = by0 - 0.004
    geo.box("StoveDoor", (0.34, 0.016, 0.28),
            (cx, fy, 0.62), col=col, mat=m["bakelite"])
    geo.box("StoveDoorBezel", (0.38, 0.010, 0.32),
            (cx, fy + 0.003, 0.62), col=col, mat=m["brass"])
    geo.cylinder("StoveHandle", 0.010, 0.10,
                 (cx + 0.12, fy - 0.02, 0.62),
                 rotation=(0, math.pi / 2, 0), col=col, mat=m["brass"],
                 segments=14)
    geo.box("StoveEmber", (0.26, 0.004, 0.05),
            (cx, fy - 0.006, 0.60), col=col, mat=m["ember"])

    # A shelf of stove tiles: the small vent grille above the door.
    for i in range(5):
        geo.box(f"StoveVent{i}", (0.30, 0.012, 0.008),
                (cx, fy - 0.002, 0.84 + i * 0.026), col=col,
                mat=m["bakelite"])


def build_back(m: dict) -> None:
    build_door(m)
    build_switch(m)
    build_stove(m)
