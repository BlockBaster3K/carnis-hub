#!/usr/bin/env python3
"""Автоматический чекер glowmask по правилу Р-3 (T-3186).
Проверяет:
  - ровно 1 непрозрачный цвет (255, 92, 57)
  - альфа только {0, 255}
  - размер == размеру тела
  - свечения вне силуэта тела = 0 px
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image

GLOW = (255, 92, 57)

def check_pair(body_im: Image.Image, glow_im: Image.Image, name: str) -> tuple[bool, str]:
    b = body_im.convert("RGBA")
    g = glow_im.convert("RGBA")
    if b.size != g.size:
        return False, f"  {name:32s} РАЗМЕР {g.size} != {b.size}"
    bpx = list(b.getdata())
    gpx = list(g.getdata())
    alphas = {p[3] for p in gpx}
    if not alphas.issubset({0, 255}):
        return False, f"  {name:32s} АЛЬФА {sorted(alphas)} != {{0,255}}"
    opaque_cols = {p[:3] for p in gpx if p[3] > 0}
    outside = sum(1 for bp, gp in zip(bpx, gpx) if gp[3] > 0 and bp[3] == 0)
    ok = (opaque_cols == {GLOW}) and (outside == 0)
    n_glow = sum(1 for p in gpx if p[3] > 0)
    return ok, f"  {name:32s} {g.size[0]}x{g.size[1]} glow_px={n_glow:4d} colors={len(opaque_cols)} {sorted(opaque_cols)} outside={outside} {'OK' if ok else 'ЗАМЕЧАНИЕ'}"

if __name__ == "__main__":
    print("Use check_pair(body_im, glow_im, name)")
