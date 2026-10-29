"""Adjustable first-pass furniture blockout, in room metres (Z-up).

Each visible part is a separately named mesh, so later interaction work can
replace or target individual objects without rebuilding the room shell.
"""
from __future__ import annotations

import bpy

from lib import geo


def build(m: dict) -> None:
    col = geo.collection("Layout")

    def box(name, size, pos, material="wood"):
        return geo.box(name, size, pos, col=col, mat=m[material])

    def cyl(name, radius, depth, pos, material="wood", **kwargs):
        return geo.cylinder(name, radius, depth, pos, col=col,
                            mat=m[material], segments=16, **kwargs)

    # Main desk follows the window wall. The TV faces into the room (+X).
    box("MainDesk_Top", (0.95, 2.20, 0.055), (0.60, 2.40, 0.735))
    for x in (0.22, 0.98):
        for y in (1.38, 3.42):
            box(f"MainDesk_Leg_{x}_{y}", (0.065, 0.065, 0.70),
                (x, y, 0.35))

    # The CRT and player are distinct groups of parts, not one static mass.
    box("CDPlayer_Body", (0.37, 0.60, 0.095), (0.48, 2.40, 0.81), "door")
    box("CDPlayer_Tray", (0.008, 0.31, 0.035), (0.669, 2.36, 0.81), "bakelite")
    box("TV_Body", (0.34, 0.57, 0.43), (0.47, 2.40, 1.0725), "door")
    box("TV_Screen", (0.012, 0.47, 0.30), (0.646, 2.40, 1.10), "bakelite")
    for i in range(4):
        box(f"TV_Button_{i + 1}", (0.015, 0.030, 0.018),
            (0.648, 2.25 + i * 0.065, 0.905), "bakelite")

    # Desk lamp and plant to the left of the screen; document stack to the right.
    cyl("DeskLamp_Base", 0.09, 0.018, (0.55, 1.85, 0.771), "bakelite")
    cyl("DeskLamp_Stem", 0.012, 0.32, (0.55, 1.85, 0.94), "brass")
    cyl("DeskLamp_Shade", 0.105, 0.12, (0.55, 1.85, 1.16), "door",
        radius_top=0.05)
    cyl("DeskPlant_Pot", 0.105, 0.18, (0.52, 1.53, 0.852), "door",
        radius_top=0.13)
    # A few broad upright leaves establish a readable silhouette, not foliage detail.
    plant_mat = bpy.data.materials.new("M_Layout_Foliage")
    plant_mat.diffuse_color = (0.19, 0.32, 0.16, 1.0)
    plant_mat.use_nodes = True
    plant_mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.19, 0.32, 0.16, 1.0)
    for i, (dx, dy, tilt) in enumerate(((0, 0, 0), (0.07, 0.02, 0.35),
                                         (-0.06, -0.02, -0.35), (0.01, 0.07, 0.2))):
        geo.box(f"DeskPlant_Leaf_{i}", (0.045, 0.075, 0.29),
                (0.52 + dx, 1.53 + dy, 1.065), rotation=(0, tilt, 0),
                col=col, mat=plant_mat)
    for i in range(3):
        box(f"Documents_Stack_{i}", (0.27, 0.33, 0.025),
            (0.57, 3.10, 0.775 + i * 0.025), "trim")

    # Computer sits left of the window desk, facing the entrance wall.
    # Keep its footprint clear of the door on the other side of that wall.
    box("ComputerDesk_Top", (1.35, 0.70, 0.055), (1.05, 0.45, 0.735))
    for x in (0.47, 1.63):
        for y in (0.17, 0.73):
            box(f"ComputerDesk_Leg_{x}_{y}", (0.065, 0.065, 0.70),
                (x, y, 0.35))
    box("Computer_MonitorBase", (0.25, 0.20, 0.045), (1.02, 0.32, 0.785), "door")
    box("Computer_Monitor", (0.43, 0.30, 0.38), (1.02, 0.32, 0.9975), "door")
    box("Computer_Screen", (0.34, 0.012, 0.27), (1.02, 0.476, 1.015), "bakelite")
    box("Computer_Keyboard", (0.46, 0.17, 0.035), (1.02, 0.70, 0.78), "door")
    box("Computer_Tower", (0.17, 0.36, 0.38), (1.55, 0.37, 0.95), "door")

    # Chair: pulled back enough to keep the keyboard accessible.
    box("Chair_Seat", (0.46, 0.45, 0.07), (1.50, 1.35, 0.48), "bakelite")
    box("Chair_Back", (0.46, 0.07, 0.48), (1.50, 1.54, 0.73), "bakelite")
    cyl("Chair_Post", 0.035, 0.40, (1.50, 1.35, 0.24), "steel")
    box("Chair_Base_X", (0.54, 0.055, 0.045), (1.50, 1.35, 0.055), "steel")
    box("Chair_Base_Y", (0.055, 0.54, 0.045), (1.50, 1.35, 0.055), "steel")

    # The bookcase turns out from the window wall at the desk's far end.
    box("Bookshelf_Left", (0.045, 0.38, 1.72), (0.17, 3.76, 0.86))
    box("Bookshelf_Right", (0.045, 0.38, 1.72), (1.01, 3.76, 0.86))
    for i, z in enumerate((0.04, 0.48, 0.90, 1.32, 1.70)):
        box(f"Bookshelf_Shelf_{i}", (0.88, 0.38, 0.035), (0.59, 3.76, z))
    box("SideTable_Top", (0.48, 0.48, 0.05), (0.95, 4.43, 0.57))
    for x in (0.77, 1.13):
        for y in (4.25, 4.61):
            box(f"SideTable_Leg_{x}_{y}", (0.045, 0.045, 0.54), (x, y, 0.27))
    cyl("FloorLamp_Base", 0.16, 0.035, (1.50, 4.53, 0.018), "bakelite")
    cyl("FloorLamp_Stem", 0.018, 1.48, (1.50, 4.53, 0.775), "steel")
    cyl("FloorLamp_Shade", 0.16, 0.21, (1.50, 4.53, 1.62), "door", radius_top=0.085)
