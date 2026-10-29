"""Inspection cameras: one per wall, plus the plan view.

Every camera is placed in Blender metres (Z-up). They exist so a geometry
change can be judged from the angle that shows it best, rather than only from
the single hero framing.
"""
from __future__ import annotations

import bpy

from .dims import D, H, W, WALL


def look_at(obj, target) -> None:
    from mathutils import Vector

    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _camera(name: str, loc, target, lens: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36.0
    cam = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    look_at(cam, target)
    return cam


# name -> (location, look-at target, focal length)
VIEWS = {
    # Principal interactive viewpoints, in the same Z-up coordinates as the
    # layout. All three look into the room rather than through the shell.
    "desk": ((2.45, 2.40, 1.42), (0.45, 2.40, 1.10), 28.0),
    "computer": ((1.80, 2.05, 1.42), (1.05, 0.45, 1.05), 28.0),
    "side": ((0.55, 1.10, 1.42), (0.95, 3.20, 1.05), 26.0),
    # Hero: eye height in the +X corner, window wall on the left.
    "eye": ((W - 0.52, 0.62, 1.45), (0.85, D * 0.66, 1.12), 26.0),
    # Entrance door and the tiled stove, seen from inside the window bay.
    "back": ((0.95, 2.05, 1.55), (W - 0.55, 0.35, 1.05), 24.0),
    # Window wall straight on, to check reveal depth and the casement leaves.
    "window": ((2.35, (1.55 + 3.25) / 2, 1.55), (0.0, 2.40, 1.50), 30.0),
    # Down the long axis from the door, the flat's own sightline.
    "axis": ((W * 0.55, 0.35, 1.62), (W * 0.35, D, 1.20), 22.0),
}


def build(name: str) -> bpy.types.Object:
    loc, target, lens = VIEWS[name]
    return _camera(f"Cam_{name}", loc, target, lens)


def build_top() -> bpy.types.Object:
    """Plan view: orthographic straight down, +Y up the page.

    A perspective camera looking up from below the floor flips the plan, so
    this one sits directly overhead with an ortho scale that just fits the
    room plus its wall thickness.
    """
    data = bpy.data.cameras.new("Cam_top")
    data.type = "ORTHO"
    # Blender's ortho scale is the horizontal span at our landscape aspect.
    # Include the full long axis vertically, plus wall thickness and margin.
    data.ortho_scale = (D + 2 * WALL + 0.60) * 1.6
    cam = bpy.data.objects.new("Cam_top", data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (W / 2, D / 2, H + 2.4)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    return cam
