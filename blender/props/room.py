"""The room: a 1990s Berlin journalist's flat, geometry only.

    Blender -b -P blender/props/room.py -- --out public/assets/room.glb --render build/room.png

Room runs 3.6 m (X) by 4.8 m (Y) by 2.6 m (Z). Interior faces are exactly on
x = 0, x = W, y = 0, y = D and z = 0; walls grow outward from those planes.

The -X wall carries a centered two-leaf casement window with curtains. The
entrance, ceiling and separately named furniture blockout complete the scene.
"""
from __future__ import annotations

import argparse
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "blender"))

from lib import geo  # noqa: E402
from lib import materials  # noqa: E402
from props import dims, layout, room_back, shell, views, window  # noqa: E402
from props.dims import D, H, W  # noqa: E402


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=os.path.join(ROOT, "public/assets/room.glb"))
    p.add_argument("--blend", default="")
    p.add_argument("--render", default="")
    p.add_argument("--render-top", default="")
    p.add_argument("--views", default="",
                   help="comma-separated inspection views, or 'all'")
    p.add_argument("--views-dir", default=os.path.join(ROOT, "build"))
    p.add_argument("--samples", type=int, default=96)
    p.add_argument("--res", type=int, default=1280)
    return p.parse_args(argv)


def look_at(obj, target) -> None:
    """Point the camera's -Z axis at `target`, keeping +Y as up."""
    from mathutils import Vector

    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_camera() -> bpy.types.Object:
    """Hero framing: eye height in the +X corner with the window on the left."""
    cam = views.build("eye")
    bpy.context.scene.camera = cam
    return cam


def build_lights() -> None:
    """Warm, dim interior with a cold night outside the window.

    Matches the reference still: the room is lit almost entirely by one warm
    practical off to the side, the window is a cool blue-black rectangle, and
    the plaster keeps a narrow tonal range. Nothing here is bright.
    """
    col = geo.collection("Lights")

    # The warm practical. Its source is off-frame, so the falloff across the
    # plaster is what you read, not the lamp itself.
    key_data = bpy.data.lights.new("KeyLight", type="AREA")
    key_data.energy = 22.0
    key_data.size = 0.50
    key_data.color = (1.0, 0.58, 0.26)
    key = bpy.data.objects.new("KeyLight", key_data)
    key.location = (W - 0.75, 0.80, 1.55)
    col.objects.link(key)
    look_at(key, (W - 1.20, 1.05, 0.75))

    # Night sky beyond the glass: cool, weak, only enough to grade the reveal
    # and read the frame in silhouette.
    fill_data = bpy.data.lights.new("WindowFill", type="AREA")
    fill_data.energy = 11.0
    fill_data.size = 1.9
    fill_data.shape = "RECTANGLE"
    fill_data.size_y = 1.25
    fill_data.color = (0.30, 0.42, 0.75)
    fill = bpy.data.objects.new("WindowFill", fill_data)
    # Keep the night fill from appearing as a bright rectangle through glass.
    fill.visible_camera = False
    fill.visible_glossy = False
    fill.visible_transmission = False
    fill.location = (-0.30, (dims.WIN_Y0 + dims.WIN_Y1) / 2,
                     (dims.WIN_Z0 + dims.WIN_Z1) / 2)
    col.objects.link(fill)
    look_at(fill, (W, (dims.WIN_Y0 + dims.WIN_Y1) / 2 + 0.30, 0.85))

    world = bpy.data.worlds.new("RoomWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.012, 0.017, 0.032, 1.0)
    bg.inputs["Strength"].default_value = 0.45
    bpy.context.scene.world = world


def render(path: str, samples: int, res: int) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = res
    scene.render.resolution_y = int(res * 0.625)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.10
    os.makedirs(os.path.dirname(path), exist_ok=True)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[room] render -> {path}")


def main() -> None:
    args = parse_args()
    geo.clear_scene()
    m = materials.build_all()

    shell.build_floor(m)
    shell.build_walls(m)
    shell.build_ceiling(m)
    shell.build_skirting(m)
    shell.build_cornice(m)
    window.build_window(m)
    window.build_curtains(m)
    room_back.build_door(m)
    layout.build(m)
    build_camera()
    build_lights()

    faces = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
    print(f"[room] mesh objects: "
          f"{len([o for o in bpy.data.objects if o.type == 'MESH'])}, "
          f"faces: {faces}")

    # Save the .blend before flattening, so the procedural graphs survive.
    if args.blend:
        os.makedirs(os.path.dirname(args.blend), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=args.blend)
        print(f"[room] blend -> {args.blend}")

    if args.render:
        render(args.render, args.samples, args.res)

    if args.render_top:
        scene = bpy.context.scene
        previous = scene.camera
        top = views.build_top()
        scene.camera = top

        # Open-top view: lifts the ceiling slab so the plan reads from above.
        ceiling = bpy.data.objects.get("Ceiling")
        if ceiling is not None:
            ceiling.hide_render = True

        # One soft overhead light so the plaster reads evenly and any seam
        # between wall planes shows up as a silhouette.
        top_data = bpy.data.lights.new("TopLight", type="AREA")
        top_data.energy = 260.0
        top_data.size = 5.0
        top_data.color = (1.0, 0.97, 0.92)
        top_light = bpy.data.objects.new("TopLight", top_data)
        top_light.location = (W / 2, D / 2, H + 2.6)
        geo.collection("Lights").objects.link(top_light)

        render(args.render_top, args.samples, args.res)

        bpy.data.objects.remove(top_light, do_unlink=True)
        bpy.data.objects.remove(top, do_unlink=True)
        if ceiling is not None:
            ceiling.hide_render = False
        scene.camera = previous

    if args.views:
        render_views(args)

    # glTF carries no node graphs: bake Base Color to constants before export.
    materials.flatten_for_gltf()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=args.out,
        export_format="GLB",
        export_apply=True,
        use_selection=False,
        export_cameras=True,
        export_lights=False,
        export_yup=True,
    )
    print(f"[room] glb -> {args.out}")


def render_views(args) -> None:
    """Render each requested inspection view; the room is left untouched."""
    names = list(views.VIEWS) if args.views == "all" else [
        n.strip() for n in args.views.split(",") if n.strip()
    ]
    scene = bpy.context.scene
    previous = scene.camera
    for name in names:
        if name not in views.VIEWS:
            print(f"[room] no view named {name!r}")
            continue
        cam = views.build(name)
        scene.camera = cam
        path = os.path.join(args.views_dir, f"view_{name}.png")
        render(path, args.samples, args.res)
        scene.camera = previous
        bpy.data.objects.remove(cam, do_unlink=True)
    scene.camera = previous


if __name__ == "__main__":
    main()
