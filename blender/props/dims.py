"""Fixed dimensions of the flat, shared by the shell and every prop module.

Units are metres, Z-up. Interior faces sit exactly on x = 0, x = W, y = 0,
y = D and z = 0; walls grow outward from those planes, so every prop can be
placed against a known plane without re-deriving the shell.
"""
from __future__ import annotations

W, D, H = 3.6, 4.8, 2.6
WALL = 0.22

# Tall multi-pane casement in the -X wall, dead centre along it:
# (D - 1.70) / 2 = 1.55 m of plaster either side.
WIN_Y0, WIN_Y1 = 1.55, 3.25
WIN_Z0, WIN_Z1 = 0.92, 2.37

# How far the glass plane sits inside the reveal.
REVEAL = 0.11

# Door in the front wall (y = 0) - the half of the room behind the camera,
# seen only in free-look. The opening is 0.18 m from the +X corner.
DOOR_CLEAR_W, DOOR_CLEAR_H = 1.02, 2.20
DOOR_X1 = W - 0.22
DOOR_X0 = DOOR_X1 - DOOR_CLEAR_W
