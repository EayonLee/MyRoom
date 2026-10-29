"""The room shell: floor, four walls with their openings, ceiling, trim.

Everything here is architecture - nothing you could carry out of the room.
Walls grow outward from the inner planes x = 0, x = W, y = 0, y = D and z = 0,
so the room side of every wall is a known plane.
"""
from __future__ import annotations

import bpy

from lib import geo

from . import dims
from .dims import D, DOOR_CLEAR_H, DOOR_X0, DOOR_X1, H, W, WALL


def build_floor(m: dict) -> None:
    col = geo.collection("Room")
    geo.box("Floor", (W + 2 * WALL, D + 2 * WALL, 0.12),
            (W / 2, D / 2, -0.06), col=col, mat=m["floor"])


def build_walls(m: dict) -> None:
    col = geo.collection("Room")

    # Keep a real opening through the entrance wall, rather than placing a
    # door-shaped panel on top of a continuous wall.
    geo.wall_x("WallFront", -WALL, W + WALL, 0.0, WALL, 0.0, H,
               [(DOOR_X0, DOOR_X1, 0.0, DOOR_CLEAR_H)],
               m["plaster"], col, outward=-1)
    geo.wall_x("WallBack", -WALL, W + WALL, D, WALL, 0.0, H, [],
               m["plaster"], col, outward=1)
    geo.wall_y("WallLeft", 0.0, D, 0.0, WALL, 0.0, H,
               [(dims.WIN_Y0, dims.WIN_Y1, dims.WIN_Z0, dims.WIN_Z1)],
               m["plaster"], col, outward=-1)
    geo.wall_y("WallRight", 0.0, D, W, WALL, 0.0, H, [], m["plaster"], col,
               outward=1)


def build_ceiling(m: dict) -> bpy.types.Object:
    col = geo.collection("Room")
    return geo.box("Ceiling", (W + 2 * WALL, D + 2 * WALL, 0.12),
                   (W / 2, D / 2, H + 0.06), col=col, mat=m["plaster_warm"])


def build_skirting(m: dict) -> None:
    """Tile skirting: 90 mm tall, 14 mm proud, its own thin band."""
    col = geo.collection("Room")
    t, h = 0.014, 0.09
    for name, size, loc in [
        ("SkirtFrontLeft", (DOOR_X0, t, h), (DOOR_X0 / 2, t / 2, h / 2)),
        ("SkirtFrontRight", (W - DOOR_X1, t, h),
         ((W + DOOR_X1) / 2, t / 2, h / 2)),
        ("SkirtBack", (W, t, h), (W / 2, D - t / 2, h / 2)),
        ("SkirtLeft", (t, D - 2 * t, h), (t / 2, D / 2, h / 2)),
        ("SkirtRight", (t, D - 2 * t, h), (W - t / 2, D / 2, h / 2)),
    ]:
        geo.box(name, size, loc, col=col, mat=m["trim"])


def build_cornice(m: dict) -> None:
    """Stucco cornice: two stacked bands under the ceiling, per the article."""
    col = geo.collection("Room")
    bands = [
        (0.030, 0.055, H - 0.055),
        (0.016, 0.030, H - 0.100),
    ]
    for i, (depth, height, z) in enumerate(bands):
        for name, size, loc in [
            (f"Cornice{i}F", (W, depth, height), (W / 2, depth / 2, z)),
            (f"Cornice{i}B", (W, depth, height), (W / 2, D - depth / 2, z)),
            (f"Cornice{i}L", (depth, D - 2 * depth, height),
             (depth / 2, D / 2, z)),
            (f"Cornice{i}R", (depth, D - 2 * depth, height),
             (W - depth / 2, D / 2, z)),
        ]:
            geo.box(name, size, loc, col=col, mat=m["trim"])
