#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""geo_render.py — bone-aware изометрический рендерер GeckoLib geo + упаковщик UV.

Инструмент Художника. Поддерживает иерархию костей (pivot + rotation), per-face UV
(format 1.12.0) и box-UV, ближайший сэмплинг текстуры (тексель 1:1), painter's
algorithm, эмиссивный проход. Используется генераторами превью-дашбордов.

Только numpy + Pillow. Без случайной генерации.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

FACES = ("up", "down", "east", "west", "north", "south")
NORMALS = {"up": (0, 1, 0), "down": (0, -1, 0), "east": (1, 0, 0),
           "west": (-1, 0, 0), "north": (0, 0, -1), "south": (0, 0, 1)}


# ─────────────────────────── UV packing ───────────────────────────

def face_sizes(size):
    w, h, d = size
    return {"up": (w, d), "down": (w, d), "east": (d, h),
            "west": (d, h), "north": (w, h), "south": (w, h)}


def pack_uv(rects, tex_w=64, tex_h=64, pad=0):
    """Shelf-упаковка прямоугольников. rects: список (key, w, h).
    Возвращает {key: (u, v, w, h)} и (used_area, overflow_bool).
    Целочисленные размеры округляются вверх (тексель 1:1, без даунскейла)."""
    items = [(k, int(math.ceil(w - 1e-9)), int(math.ceil(h - 1e-9))) for k, w, h in rects]
    items.sort(key=lambda t: (-t[2], -t[1]))
    placed = {}
    x = y = shelf_h = 0
    used = 0
    overflow = False
    for k, w, h in items:
        if w <= 0 or h <= 0:
            placed[k] = (0, 0, 0, 0)
            continue
        if x + w > tex_w:
            x = 0
            y += shelf_h + pad
            shelf_h = 0
        if y + h > tex_h:
            overflow = True
        placed[k] = (x, y, w, h)
        used += w * h
        x += w + pad
        shelf_h = max(shelf_h, h)
    return placed, used, overflow


def uv_overlap(placed):
    """Число пар пересекающихся UV-прямоугольников (ненулевая площадь)."""
    keys = [k for k, r in placed.items() if r[2] > 0 and r[3] > 0]
    over = 0
    for i in range(len(keys)):
        u1, v1, w1, h1 = placed[keys[i]]
        for j in range(i + 1, len(keys)):
            u2, v2, w2, h2 = placed[keys[j]]
            if u1 < u2 + w2 and u2 < u1 + w1 and v1 < v2 + h2 and v2 < v1 + h1:
                over += 1
    return over


# ─────────────────────────── bone transforms ───────────────────────────

def _rot(axis, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def bone_world_matrices(bones):
    """bones: список dict(name,parent,pivot,rotation). Возвращает {name: 4x4}."""
    by_name = {b["name"]: b for b in bones}
    cache = {}

    def world(name):
        if name in cache:
            return cache[name]
        b = by_name[name]
        piv = np.array(b.get("pivot", [0, 0, 0]), dtype=float)
        rot = b.get("rotation", [0, 0, 0])
        R = _rot("x", rot[0]) @ _rot("y", rot[1]) @ _rot("z", rot[2])
        local = np.eye(4)
        local[:3, :3] = R
        local[:3, 3] = piv - R @ piv
        parent = b.get("parent")
        M = world(parent) @ local if parent else local
        cache[name] = M
        return M

    for b in bones:
        world(b["name"])
    return cache


def cube_corners(origin, size):
    x, y, z = origin
    w, h, d = size
    return {
        "up":    [(x, y + h, z), (x + w, y + h, z), (x + w, y + h, z + d), (x, y + h, z + d)],
        "down":  [(x, y, z + d), (x + w, y, z + d), (x + w, y, z), (x, y, z)],
        "east":  [(x + w, y + h, z), (x + w, y + h, z + d), (x + w, y, z + d), (x + w, y, z)],
        "north": [(x + w, y + h, z), (x, y + h, z), (x, y, z), (x + w, y, z)],
        "west":  [(x, y + h, z + d), (x, y + h, z), (x, y, z), (x, y, z + d)],
        "south": [(x, y + h, z + d), (x + w, y + h, z + d), (x + w, y, z + d), (x, y, z + d)],
    }


def _cube_uv(cube, size):
    uv = cube.get("uv")
    if isinstance(uv, dict):
        return {f: (uv[f]["uv"][0], uv[f]["uv"][1], uv[f]["uv_size"][0], uv[f]["uv_size"][1])
                for f in FACES if f in uv}
    u, v = uv
    w, h, d = size
    return {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d),
            "east": (u, v + d, d, h), "north": (u + d, v + d, w, h),
            "west": (u + d + w, v + d, d, h), "south": (u + d + w + d, v + d, w, h)}


# ─────────────────────────── render ───────────────────────────

def render_model(bones, cubes, tex, glow=None, yaw_deg=35.0, canvas=300,
                 px_per_unit=7.0, glow_boost=1.0, anim=None):
    """cubes: список dict(bone,origin,size,uv). anim: {bone: {'rotation':..,'scale':..,'position':..}}
    Применяет иерархию костей + опциональную позу анимации. Возвращает RGBA Image."""
    world = bone_world_matrices(bones)
    by_name = {b["name"]: b for b in bones}
    if anim:
        # пересчёт world с учётом анимационных дельт (поворот/масштаб относительно pivot)
        cache = {}

        def world_anim(name):
            if name in cache:
                return cache[name]
            b = by_name[name]
            piv = np.array(b.get("pivot", [0, 0, 0]), dtype=float)
            rot = list(b.get("rotation", [0, 0, 0]))
            scl = np.ones(3)
            pos = np.zeros(3)
            a = anim.get(name, {})
            rot = [rot[i] + a.get("rotation", [0, 0, 0])[i] for i in range(3)]
            scl = np.array(a.get("scale", [1, 1, 1]))
            pos = np.array(a.get("position", [0, 0, 0]))
            R = _rot("x", rot[0]) @ _rot("y", rot[1]) @ _rot("z", rot[2])
            S = np.diag(scl)
            local = np.eye(4)
            local[:3, :3] = R @ S
            local[:3, 3] = piv - R @ S @ piv + pos
            parent = b.get("parent")
            M = world_anim(parent) @ local if parent else local
            cache[name] = M
            return M

        for b in bones:
            world_anim(b["name"])
        world = cache

    yaw = math.radians(yaw_deg)
    cy, sy = math.cos(yaw), math.sin(yaw)
    view = np.array([0.62, 0.72, 0.62])
    faces = []
    for c in cubes:
        M = world[c["bone"]]
        rects = _cube_uv(c, c["size"])
        corners = cube_corners(c["origin"], c["size"])
        for f in FACES:
            if f not in rects:
                continue
            n = np.array(NORMALS[f], dtype=float)
            rn = (M[:3, :3] @ n)
            rnx = rn[0] * cy + rn[2] * sy
            rnz = -rn[0] * sy + rn[2] * cy
            if rnx * view[0] + rn[1] * view[1] + rnz * view[2] <= 0:
                continue
            proj = []
            depth = 0.0
            for p in corners[f]:
                wp = M @ np.array([p[0], p[1], p[2], 1.0])
                x, y, z = wp[0], wp[1], wp[2]
                rx = x * cy + z * sy
                rz = -x * sy + z * cy
                proj.append(((rx - rz) * 0.866, (rx + rz) * 0.5 - y))
                depth += rx + rz + y
            faces.append((depth / 4.0, proj, rects[f], f))
    if not faces:
        return Image.new("RGBA", (canvas, canvas), (24, 22, 26, 255))
    faces.sort(key=lambda t: t[0])
    pts = [p for _, pp, _, _ in faces for p in pp]
    minx = min(p[0] for p in pts); maxx = max(p[0] for p in pts)
    miny = min(p[1] for p in pts); maxy = max(p[1] for p in pts)
    scale = min(px_per_unit, (canvas - 24) / max(maxx - minx, maxy - miny, 1e-6))
    ox = canvas / 2 - (minx + maxx) / 2 * scale
    oy = canvas / 2 - (miny + maxy) / 2 * scale + (maxy - miny) * 0.04

    out = np.zeros((canvas, canvas, 4), dtype=np.uint8)
    out[:, :, :3] = (24, 22, 26)
    out[:, :, 3] = 255
    tarr = np.asarray(tex.convert("RGBA"))
    tw, th = tex.size
    garr = np.asarray(glow.convert("RGBA")) if glow is not None else None
    span = max(maxy - miny, 1e-6)
    eps = 1e-6
    for _, pp, (ru, rv, rw, rh), f in faces:
        if rw <= 0 or rh <= 0:
            continue
        screen = [(p[0] * scale + ox, p[1] * scale + oy) for p in pp]
        p0 = np.array(screen[0]); p1 = np.array(screen[1]); p3 = np.array(screen[3])
        mat = np.array([p1 - p0, p3 - p0]).T
        if abs(np.linalg.det(mat)) < 1e-9:
            continue
        inv = np.linalg.inv(mat)
        xs = [p[0] for p in screen]; ys = [p[1] for p in screen]
        x0 = max(0, int(math.floor(min(xs)))); x1 = min(canvas - 1, int(math.ceil(max(xs))))
        y0 = max(0, int(math.floor(min(ys)))); y1 = min(canvas - 1, int(math.ceil(max(ys))))
        if x1 < x0 or y1 < y0:
            continue
        shade = 0.66 + 0.34 * max(0.0, min(1.0, 1.0 - (pp[0][1] - miny) / span))
        if f == "up":
            shade = min(1.0, shade + 0.12)
        gx = np.arange(x0, x1 + 1) + 0.5
        gy = np.arange(y0, y1 + 1) + 0.5
        GX, GY = np.meshgrid(gx, gy)
        dx = GX - p0[0]; dy = GY - p0[1]
        a = inv[0, 0] * dx + inv[0, 1] * dy
        b = inv[1, 0] * dx + inv[1, 1] * dy
        inside = (a >= -eps) & (a <= 1 + eps) & (b >= -eps) & (b <= 1 + eps)
        if not inside.any():
            continue
        uu = np.clip((ru + a * rw).astype(int), 0, tw - 1) % tw
        vv = np.clip((rv + b * rh).astype(int), 0, th - 1) % th
        samp = tarr[vv, uu]
        vis = inside & (samp[:, :, 3] > 0)
        if not vis.any():
            continue
        rgb = samp[:, :, :3].astype(float) * shade
        if garr is not None:
            gs = garr[vv, uu]
            gm = vis & (gs[:, :, 3] > 0)
            if gm.any():
                rgb[gm] = np.minimum(255.0, rgb[gm] * 0.35 + gs[gm, :3].astype(float) * glow_boost)
        sub = out[y0:y1 + 1, x0:x1 + 1]
        sub[vis, :3] = rgb[vis].astype(np.uint8)
        sub[vis, 3] = 255
    img = Image.fromarray(out, "RGBA")
    draw = ImageDraw.Draw(img)
    for _, pp, (ru, rv, rw, rh), f in faces:
        if rw <= 0 or rh <= 0:
            continue
        screen = [(p[0] * scale + ox, p[1] * scale + oy) for p in pp]
        draw.line(screen + [screen[0]], fill=(12, 9, 12, 255), width=1)
    return img


def load_geo(path):
    import json
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    g = d["minecraft:geometry"][0]
    bones = [{"name": b["name"], "parent": b.get("parent"),
              "pivot": b.get("pivot", [0, 0, 0]), "rotation": b.get("rotation", [0, 0, 0])}
             for b in g["bones"]]
    cubes = []
    for b in g["bones"]:
        for c in b.get("cubes", []):
            cubes.append({"bone": b["name"], "origin": c["origin"], "size": c["size"], "uv": c["uv"]})
    return bones, cubes, g["description"]
