"""Geometry helpers for the room build.

Units are metres, Z-up, matching Blender's native convention.
Everything here avoids bpy.ops so it stays deterministic in background mode.
"""
from __future__ import annotations

import math

import bmesh
import bpy


def clear_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def _link(obj: bpy.types.Object, col: bpy.types.Collection | None) -> bpy.types.Object:
    target = col or bpy.context.scene.collection
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    target.objects.link(obj)
    return obj


def box(name, size, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0),
        col=None, mat=None, uv_scale=1.0):
    """Axis-aligned box centred on `location` with full extents `size`."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    me.update()
    auto_uv(me, uv_scale)
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    if mat is not None:
        obj.data.materials.append(mat)
    return _link(obj, col)


def cylinder(name, radius, depth, location=(0.0, 0.0, 0.0),
             rotation=(0.0, 0.0, 0.0), segments=32, col=None, mat=None,
             radius_top=None, uv_scale=1.0):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius if radius_top is None else radius_top,
        depth=depth,
    )
    bm.to_mesh(me)
    bm.free()
    me.update()
    auto_uv(me, uv_scale)
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    if mat is not None:
        obj.data.materials.append(mat)
    return _link(obj, col)


def curtain(name, size, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0),
            folds=7, amplitude=0.035, thickness=0.012, col=None, mat=None):
    """A hanging fabric panel, pleated across its width.

    Local space: width along X, height along +Z from the origin at the bottom
    centre, folds displaced along Y. Solidify gives the sheet real thickness so
    it does not disappear when seen from behind.
    """
    w, h = size
    nx = max(8, folds * 8)
    nz = 6
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rows = []
    for j in range(nz + 1):
        z = h * j / nz
        row = []
        for i in range(nx + 1):
            t = i / nx
            x = -w / 2 + w * t
            # Folds loosen toward the hem, the way gravity pulls the cloth.
            fall = 0.72 + 0.28 * (1.0 - j / nz)
            y = amplitude * fall * math.sin(2.0 * math.pi * folds * t)
            row.append(bm.verts.new((x, y, z)))
        rows.append(row)
    for j in range(nz):
        for i in range(nx):
            bm.faces.new((rows[j][i], rows[j][i + 1],
                          rows[j + 1][i + 1], rows[j + 1][i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    me.update()
    auto_uv(me, 1.0)
    obj = bpy.data.objects.new(name, me)
    obj.location = location
    obj.rotation_euler = rotation
    if mat is not None:
        obj.data.materials.append(mat)
    _link(obj, col)
    mod = obj.modifiers.new("solidify", "SOLIDIFY")
    mod.thickness = thickness
    mod.offset = 0.0
    return obj


def auto_uv(me: bpy.types.Mesh, scale: float = 1.0) -> None:
    """Cheap deterministic box projection, so every surface has UVs from day one."""
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uvs = me.uv_layers[0].data
    for poly in me.polygons:
        n = poly.normal
        axis = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if axis == 0:
                u, w = co.y, co.z
            elif axis == 1:
                u, w = co.x, co.z
            else:
                u, w = co.x, co.y
            uvs[li].uv = (u * scale, w * scale)


def bevel(obj, width=0.004, segments=2, angle=45.0):
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = angle * 0.017453292519943295
    mod.harden_normals = True
    mod.miter_outer = "MITER_ARC"
    return mod


def shade_flat(obj) -> None:
    for poly in obj.data.polygons:
        poly.use_smooth = False


def shade_smooth(obj) -> None:
    for poly in obj.data.polygons:
        poly.use_smooth = True


def wall_x(name, x0, x1, y, thickness, z0, z1, openings, mat, col=None,
           outward=-1):
    """Wall running along X. Its inner face sits at `y`.

    `outward` is +1 when the solid should grow toward +Y, -1 toward -Y.

    `openings` is a list of (u0, u1, oz0, oz1) in wall-local X / world Z.
    Panels are plain boxes, so each opening keeps a real reveal depth.
    """
    pieces = []
    cursor = x0
    for u0, u1, oz0, oz1 in sorted(openings, key=lambda o: o[0]):
        if u0 > cursor:
            pieces.append((cursor, u0, z0, z1))
        if oz0 > z0:
            pieces.append((u0, u1, z0, oz0))
        if oz1 < z1:
            pieces.append((u0, u1, oz1, z1))
        cursor = max(cursor, u1)
    if cursor < x1:
        pieces.append((cursor, x1, z0, z1))

    centre_y = y + outward * thickness / 2
    objs = []
    for i, (px0, px1, pz0, pz1) in enumerate(pieces):
        w, h = px1 - px0, pz1 - pz0
        if w <= 1e-6 or h <= 1e-6:
            continue
        objs.append(box(
            f"{name}_{i}",
            (w, thickness, h),
            ((px0 + px1) / 2, centre_y, (pz0 + pz1) / 2),
            col=col, mat=mat,
        ))
    return objs


def wall_y(name, y0, y1, x, thickness, z0, z1, openings, mat, col=None,
           outward=1):
    """Wall running along Y. Inner face at `x`, `outward` gives the grow axis."""
    pieces = []
    cursor = y0
    for u0, u1, oz0, oz1 in sorted(openings, key=lambda o: o[0]):
        if u0 > cursor:
            pieces.append((cursor, u0, z0, z1))
        if oz0 > z0:
            pieces.append((u0, u1, z0, oz0))
        if oz1 < z1:
            pieces.append((u0, u1, oz1, z1))
        cursor = max(cursor, u1)
    if cursor < y1:
        pieces.append((cursor, y1, z0, z1))

    centre_x = x + outward * thickness / 2
    objs = []
    for i, (py0, py1, pz0, pz1) in enumerate(pieces):
        d, h = py1 - py0, pz1 - pz0
        if d <= 1e-6 or h <= 1e-6:
            continue
        objs.append(box(
            f"{name}_{i}",
            (thickness, d, h),
            (centre_x, (py0 + py1) / 2, (pz0 + pz1) / 2),
            col=col, mat=mat,
        ))
    return objs
