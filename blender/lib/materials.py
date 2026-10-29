"""Procedural materials only - no image textures anywhere.

The article is explicit that wood, plaster, plastic and metal surfaces are
noise functions rather than photographs, so every material here is built from
texture nodes driven by object coordinates.
"""
from __future__ import annotations

import bpy


def _new(name: str) -> tuple[bpy.types.Material, bpy.types.NodeTree]:
    mat = bpy.data.materials.get(name)
    if mat is not None:
        bpy.data.materials.remove(mat)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for node in list(nt.nodes):
        nt.nodes.remove(node)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (280, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, nt


def _coords(nt, scale=1.0, rotation=(0.0, 0.0, 0.0)):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-700, 0)
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    mp.inputs["Rotation"].default_value = rotation
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    return mp


def _ramp(nt, stops, location=(0, 0)):
    node = nt.nodes.new("ShaderNodeValToRGB")
    node.location = location
    ramp = node.color_ramp
    ramp.elements[0].position = stops[0][0]
    ramp.elements[0].color = (*stops[0][1], 1.0)
    ramp.elements[1].position = stops[-1][0]
    ramp.elements[1].color = (*stops[-1][1], 1.0)
    for pos, rgb in stops[1:-1]:
        el = ramp.elements.new(pos)
        el.color = (*rgb, 1.0)
    return node


def _bump(nt, height_socket, strength, distance=0.02, location=(0, -300)):
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = location
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    nt.links.new(height_socket, bump.inputs["Height"])
    return bump


def plaster(name="M_Plaster", base=(0.78, 0.74, 0.66), roughness=0.85):
    """Lime plaster: soft tonal drift plus fine grain."""
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, 1.0)

    broad = nt.nodes.new("ShaderNodeTexNoise")
    broad.location = (-480, 120)
    broad.inputs["Scale"].default_value = 2.2
    broad.inputs["Detail"].default_value = 6.0
    broad.inputs["Roughness"].default_value = 0.55
    nt.links.new(mp.outputs["Vector"], broad.inputs["Vector"])

    tint = _ramp(nt, [
        (0.20, tuple(c * 0.90 for c in base)),
        (0.55, base),
        (0.85, tuple(min(1.0, c * 1.06) for c in base)),
    ], location=(-240, 120))
    nt.links.new(broad.outputs["Fac"], tint.inputs["Fac"])
    nt.links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])

    grain = nt.nodes.new("ShaderNodeTexNoise")
    grain.location = (-480, -220)
    grain.inputs["Scale"].default_value = 160.0
    grain.inputs["Detail"].default_value = 8.0
    grain.inputs["Roughness"].default_value = 0.7
    nt.links.new(mp.outputs["Vector"], grain.inputs["Vector"])
    b = _bump(nt, grain.outputs["Fac"], 0.12, 0.006)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def wood(name="M_Wood", dark=(0.20, 0.11, 0.055), light=(0.42, 0.25, 0.13),
         scale=1.0, roughness=0.42, grain_axis="X"):
    """Wood: warped banding for grain, fine noise for pores."""
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, scale)

    warp = nt.nodes.new("ShaderNodeTexNoise")
    warp.location = (-700, 220)
    warp.inputs["Scale"].default_value = 3.5
    warp.inputs["Detail"].default_value = 5.0
    nt.links.new(mp.outputs["Vector"], warp.inputs["Vector"])

    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.location = (-480, 220)
    wave.wave_type = "BANDS"
    wave.bands_direction = grain_axis
    wave.inputs["Scale"].default_value = 14.0
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 3.0
    wave.inputs["Detail Scale"].default_value = 2.0
    nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
    nt.links.new(warp.outputs["Fac"], wave.inputs["Distortion"])

    tint = _ramp(nt, [
        (0.10, dark),
        (0.48, tuple((a + b) / 2 for a, b in zip(dark, light))),
        (0.90, light),
    ], location=(-240, 220))
    nt.links.new(wave.outputs["Fac"], tint.inputs["Fac"])
    nt.links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])

    pores = nt.nodes.new("ShaderNodeTexNoise")
    pores.location = (-480, -220)
    pores.inputs["Scale"].default_value = 220.0
    pores.inputs["Detail"].default_value = 6.0
    nt.links.new(mp.outputs["Vector"], pores.inputs["Vector"])
    b = _bump(nt, pores.outputs["Fac"], 0.18, 0.004)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def painted(name, color, roughness=0.5, bump_scale=180.0, bump_strength=0.10):
    """Lacquer over wood: flat colour, faint brush texture."""
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, 1.0)

    drift = nt.nodes.new("ShaderNodeTexNoise")
    drift.location = (-480, 150)
    drift.inputs["Scale"].default_value = 1.6
    drift.inputs["Detail"].default_value = 3.0
    nt.links.new(mp.outputs["Vector"], drift.inputs["Vector"])
    tint = _ramp(nt, [
        (0.15, tuple(c * 0.94 for c in color)),
        (0.85, tuple(min(1.0, c * 1.03) for c in color)),
    ], location=(-240, 150))
    nt.links.new(drift.outputs["Fac"], tint.inputs["Fac"])
    nt.links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])

    grain = nt.nodes.new("ShaderNodeTexNoise")
    grain.location = (-480, -240)
    grain.inputs["Scale"].default_value = bump_scale
    grain.inputs["Detail"].default_value = 5.0
    nt.links.new(mp.outputs["Vector"], grain.inputs["Vector"])
    b = _bump(nt, grain.outputs["Fac"], bump_strength, 0.003)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def parquet(name="M_Floor_Parquet", dark=(0.16, 0.085, 0.042),
            light=(0.40, 0.23, 0.115), roughness=0.34):
    """Parquet: staggered boards, each with its own grain and tone.

    A brick node gives the board layout and a per-board random colour, then a
    wave node cuts grain along each board. Without the brick split the floor
    reads as one flat varnished sheet, which is what a scanned texture would
    have cost us - noise does the job.
    """
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, 1.0)

    boards = nt.nodes.new("ShaderNodeTexBrick")
    boards.location = (-520, 220)
    boards.offset = 0.37
    boards.offset_frequency = 1
    boards.squash = 1.0
    boards.inputs["Scale"].default_value = 1.0
    boards.inputs["Mortar Size"].default_value = 0.0016
    boards.inputs["Brick Width"].default_value = 0.62
    boards.inputs["Row Height"].default_value = 0.115
    boards.inputs["Bias"].default_value = 0.0
    nt.links.new(mp.outputs["Vector"], boards.inputs["Vector"])

    # Per-board tone: the ramp walks the brick's own per-brick random value.
    tone = _ramp(nt, [
        (0.0, dark),
        (0.52, tuple((a + b) / 2 for a, b in zip(dark, light))),
        (1.0, light),
    ], location=(-280, 240))
    nt.links.new(boards.outputs["Color"], tone.inputs["Fac"])

    # Grain along the board, distorted so it does not read as stripes.
    warp = nt.nodes.new("ShaderNodeTexNoise")
    warp.location = (-760, -60)
    warp.inputs["Scale"].default_value = 5.0
    warp.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs["Vector"], warp.inputs["Vector"])

    grain = nt.nodes.new("ShaderNodeTexWave")
    grain.location = (-520, -60)
    grain.wave_type = "BANDS"
    grain.bands_direction = "Y"
    grain.inputs["Scale"].default_value = 22.0
    grain.inputs["Distortion"].default_value = 6.0
    grain.inputs["Detail"].default_value = 2.0
    nt.links.new(mp.outputs["Vector"], grain.inputs["Vector"])
    nt.links.new(warp.outputs["Fac"], grain.inputs["Distortion"])

    grain_mix = nt.nodes.new("ShaderNodeMixRGB")
    grain_mix.location = (-60, 240)
    grain_mix.blend_type = "MULTIPLY"
    grain_mix.inputs["Fac"].default_value = 0.22
    nt.links.new(tone.outputs["Color"], grain_mix.inputs["Color1"])
    nt.links.new(grain.outputs["Color"], grain_mix.inputs["Color2"])
    nt.links.new(grain_mix.outputs["Color"], bsdf.inputs["Base Color"])

    # Board joints plus a fine pore bump.
    pores = nt.nodes.new("ShaderNodeTexNoise")
    pores.location = (-520, -360)
    pores.inputs["Scale"].default_value = 260.0
    pores.inputs["Detail"].default_value = 6.0
    nt.links.new(mp.outputs["Vector"], pores.inputs["Vector"])
    joint = nt.nodes.new("ShaderNodeMath")
    joint.location = (-280, -360)
    joint.operation = "MAXIMUM"
    nt.links.new(boards.outputs["Fac"], joint.inputs[0])
    nt.links.new(pores.outputs["Fac"], joint.inputs[1])
    b = _bump(nt, joint.outputs["Value"], 0.28, 0.004)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def tile(name, color_a=(0.62, 0.66, 0.52), color_b=(0.72, 0.70, 0.58),
         mortar=(0.55, 0.52, 0.46), scale=1.0, glaze=0.18):
    """Kachelofen ceramic: brick layout with per-tile tonal variation."""
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, scale)

    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.location = (-420, 160)
    brick.offset = 0.5
    brick.squash = 1.0
    brick.inputs["Color1"].default_value = (*color_a, 1.0)
    brick.inputs["Color2"].default_value = (*color_b, 1.0)
    brick.inputs["Mortar"].default_value = (*mortar, 1.0)
    brick.inputs["Scale"].default_value = 5.0
    brick.inputs["Mortar Size"].default_value = 0.006
    brick.inputs["Bias"].default_value = 0.0
    brick.inputs["Brick Width"].default_value = 0.24
    brick.inputs["Row Height"].default_value = 0.24
    nt.links.new(mp.outputs["Vector"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])

    b = _bump(nt, brick.outputs["Fac"], 0.55, 0.008)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Roughness"].default_value = glaze
    return mat


def metal(name, color=(0.72, 0.55, 0.26), roughness=0.32):
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, 1.0)

    wear = nt.nodes.new("ShaderNodeTexNoise")
    wear.location = (-480, -160)
    wear.inputs["Scale"].default_value = 90.0
    wear.inputs["Detail"].default_value = 6.0
    nt.links.new(mp.outputs["Vector"], wear.inputs["Vector"])
    b = _bump(nt, wear.outputs["Fac"], 0.05, 0.002)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def fabric(name="M_Curtain", base=(0.30, 0.145, 0.065), sheen=0.35,
           roughness=0.86):
    """Heavy wool curtain: deep warm red-brown, soft drifted sheen."""
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, 1.0)

    broad = nt.nodes.new("ShaderNodeTexNoise")
    broad.location = (-480, 130)
    broad.inputs["Scale"].default_value = 3.4
    broad.inputs["Detail"].default_value = 5.0
    nt.links.new(mp.outputs["Vector"], broad.inputs["Vector"])
    tint = _ramp(nt, [
        (0.15, tuple(c * 0.80 for c in base)),
        (0.60, base),
        (0.92, tuple(min(1.0, c * 1.28) for c in base)),
    ], location=(-240, 130))
    nt.links.new(broad.outputs["Fac"], tint.inputs["Fac"])
    nt.links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])

    weave = nt.nodes.new("ShaderNodeTexNoise")
    weave.location = (-480, -230)
    weave.inputs["Scale"].default_value = 320.0
    weave.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs["Vector"], weave.inputs["Vector"])
    b = _bump(nt, weave.outputs["Fac"], 0.22, 0.003)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Roughness"].default_value = roughness
    for socket, value in (("Sheen Weight", sheen), ("Sheen Roughness", 0.5)):
        if socket in bsdf.inputs:
            bsdf.inputs[socket].default_value = value
    return mat


def glass(name="M_Glass", tint=(0.42, 0.50, 0.62), roughness=0.045):
    """Night glass: almost clear, tinted cold, with a faint dusty smear.

    Cycles needs a real transmissive surface rather than a flat colour, or the
    panes read as dark cards and the window stops looking like an opening.
    """
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, 1.0)

    smear = nt.nodes.new("ShaderNodeTexNoise")
    smear.location = (-480, -180)
    smear.inputs["Scale"].default_value = 8.0
    smear.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs["Vector"], smear.inputs["Vector"])
    b = _bump(nt, smear.outputs["Fac"], 0.02, 0.002)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Base Color"].default_value = (*tint, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    for socket, value in (("Transmission Weight", 1.0), ("IOR", 1.52)):
        if socket in bsdf.inputs:
            bsdf.inputs[socket].default_value = value
    return mat


def bakelite(name="M_Bakelite", color=(0.075, 0.048, 0.036)):
    """Period-correct phenolic plastic: dark, slightly oily sheen."""
    mat, nt = _new(name)
    bsdf = nt.nodes["Principled BSDF"]
    mp = _coords(nt, 1.0)

    cloud = nt.nodes.new("ShaderNodeTexNoise")
    cloud.location = (-480, -180)
    cloud.inputs["Scale"].default_value = 60.0
    cloud.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs["Vector"], cloud.inputs["Vector"])
    b = _bump(nt, cloud.outputs["Fac"], 0.04, 0.002)
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.28
    return mat


def glow(name, color, strength=6.0):
    """Emissive strip, used for the light leaking under the door."""
    mat, nt = _new(name)
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.location = (280, 0)
    emit.inputs["Color"].default_value = (*color, 1.0)
    emit.inputs["Strength"].default_value = strength
    out = nt.nodes["Material Output"]
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def build_all() -> dict[str, bpy.types.Material]:
    return {
        "plaster": plaster("M_Plaster_Wall", (0.80, 0.76, 0.67)),
        "plaster_warm": plaster("M_Plaster_Ceiling", (0.86, 0.84, 0.78), 0.9),
        "floor": parquet(),
        "door": painted("M_Door_Lacquer", (0.74, 0.71, 0.62), 0.44),
        "trim": painted("M_Trim_Paint", (0.83, 0.81, 0.74), 0.42),
        "wood": wood("M_Wood_Prop", (0.19, 0.10, 0.05), (0.38, 0.21, 0.10),
                     scale=1.4, roughness=0.40),
        "tile": tile("M_Kachelofen"),
        "curtain": fabric(),
        "brass": metal("M_Brass", (0.70, 0.53, 0.25), 0.34),
        "steel": metal("M_Steel", (0.55, 0.56, 0.57), 0.28),
        "bakelite": bakelite(),
        "lamp_glow": glow("M_DoorGlow", (1.0, 0.86, 0.62), 8.0),
        "ember": glow("M_StoveEmber", (1.0, 0.34, 0.09), 3.0),
        "door_shade": painted("M_Door_Shadow", (0.55, 0.52, 0.45), 0.55),
        "glass": glass(),
    }


# Mean base colours for export. glTF cannot carry procedural node graphs, so a
# mesh exported straight from these materials falls back to white unless the
# Base Color socket holds a constant. These are the mid-points of the ramps.
FLAT_COLORS = {
    "M_Plaster_Wall": (0.80, 0.76, 0.67),
    "M_Plaster_Ceiling": (0.86, 0.84, 0.78),
    "M_Floor_Parquet": (0.28, 0.157, 0.078),
    "M_Door_Lacquer": (0.74, 0.71, 0.62),
    "M_Trim_Paint": (0.83, 0.81, 0.74),
    "M_Wood_Prop": (0.285, 0.155, 0.075),
    "M_Kachelofen": (0.67, 0.68, 0.55),
    "M_Curtain": (0.30, 0.145, 0.065),
    "M_Door_Shadow": (0.55, 0.52, 0.45),
    "M_Bakelite": (0.075, 0.048, 0.036),
    "M_Brass": (0.70, 0.53, 0.25),
    "M_Steel": (0.55, 0.56, 0.57),
    "M_Glass": (0.42, 0.50, 0.62),
}


def flatten_for_gltf() -> None:
    """Replace procedural Base Color inputs with constants, for export only.

    Call after rendering and before exporting the GLB. Cycles renders keep the
    full noise/ramp graphs because the .blend is saved before this runs.
    """
    for name, rgb in FLAT_COLORS.items():
        mat = bpy.data.materials.get(name)
        if mat is None or not mat.use_nodes:
            continue
        bsdf = next(
            (n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
            None,
        )
        if bsdf is None:
            continue
        socket = bsdf.inputs["Base Color"]
        for link in list(socket.links):
            mat.node_tree.links.remove(link)
        socket.default_value = (*rgb, 1.0)
