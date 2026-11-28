#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cerebral_nexus.py — генератор боевого ТЗ: Церебральный Нексус Улья (BlockEntity).

Канон репозитория: format_version 1.12.0 (per-face UV), палитра PALETTE.md (7 цветов),
эмиссив Р-3 (255,92,57). 45 кубов, основание Y=0, габарит ~24x24, высота ~38.
Лицо -Z, спина +Z. D5-чистая геометрия в raw-пространстве (повороты костей Д5 игнорирует).

Выход:
  04-artist/models/cerebral_nexus.geo.json
  04-artist/textures/cerebral_nexus.png
  04-artist/textures/cerebral_nexus_glowmask.png   (канон репозитория; алиас GENESIS _e.png)
  04-artist/animations/cerebral_nexus.animation.json
  04-artist/previews/cerebral_nexus_preview.png
  04-artist/deliverables/Carnis_3.9.1_cerebral_nexus.zip

Запуск: .venv/bin/python 04-artist/generators/cerebral_nexus.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04-artist/tools"))
import geo_render as gr  # noqa: E402

ART = ROOT / "04-artist"
TEX_W = TEX_H = 64
BASELINE = [(84, 40, 54), (104, 47, 64), (157, 80, 94), (161, 90, 96),
            (179, 106, 105), (196, 126, 119), (209, 144, 130)]
GLOW = (255, 92, 57)

# ─────────────────────────── кости ───────────────────────────
BONES = [
    dict(name="root", pivot=[0, 0, 0]),
    dict(name="spinal_column_base", parent="root", pivot=[0, 2.5, 0], rotation=[8, 0, 0]),
    dict(name="spinal_column_mid", parent="spinal_column_base", pivot=[0, 14, 0], rotation=[0, 12, -6]),
    dict(name="spinal_column_top", parent="spinal_column_mid", pivot=[0, 24, 0]),
    dict(name="cerebrum_core", parent="spinal_column_top", pivot=[0, 28, -0.5]),
    dict(name="lobe_frontal_l1", parent="cerebrum_core", pivot=[-3, 33, -5]),
    dict(name="lobe_frontal_l2", parent="cerebrum_core", pivot=[-2.8, 29.5, -5]),
    dict(name="lobe_frontal_r1", parent="cerebrum_core", pivot=[3, 33, -5]),
    dict(name="lobe_frontal_r2", parent="cerebrum_core", pivot=[3, 29.5, -5]),
    dict(name="lobe_parietal_l", parent="cerebrum_core", pivot=[-3, 35, 0]),
    dict(name="lobe_parietal_r", parent="cerebrum_core", pivot=[3, 35, 0]),
    dict(name="lobe_temporal_l", parent="cerebrum_core", pivot=[-5, 29.5, 0]),
    dict(name="lobe_temporal_r", parent="cerebrum_core", pivot=[5, 29.5, 0]),
    dict(name="lobe_occipital_core", parent="cerebrum_core", pivot=[0, 31, 4]),
    dict(name="neural_fissure_depths", parent="cerebrum_core", pivot=[0, 32, -5]),
    dict(name="ganglia_stalks", parent="spinal_column_top", pivot=[0, 27, 0]),
    dict(name="bone_cage", parent="spinal_column_top", pivot=[0, 26, 0]),
]
# жгуты: base -> tip
for i, (gx, gz) in enumerate([(-3, -3), (3, -3), (-3, 2), (3, 2)], 1):
    BONES.append(dict(name=f"ganglion_{i}_base", parent="ganglia_stalks", pivot=[gx, 27.5, gz]))
    BONES.append(dict(name=f"ganglion_{i}_tip", parent=f"ganglion_{i}_base", pivot=[gx, 25, gz],
                      rotation=[4 if i % 2 else -4, 0, 3 if i < 3 else -3]))
# рёбра: base -> mid -> tip, изгиб внутрь к вершине
RIB_POS = []
for i in range(6):
    th = math.radians(i * 60)
    px, pz = 8.5 * math.cos(th), -0.5 + 8.5 * math.sin(th)
    RIB_POS.append((px, pz))
    rx, rz = math.cos(th), math.sin(th)
    BONES.append(dict(name=f"rib_{i+1}_base", parent="bone_cage", pivot=[px, 26, pz]))
    BONES.append(dict(name=f"rib_{i+1}_mid", parent=f"rib_{i+1}_base", pivot=[px, 32, pz],
                      rotation=[-rz * 18, 0, rx * 18]))
    BONES.append(dict(name=f"rib_{i+1}_tip", parent=f"rib_{i+1}_mid", pivot=[px, 36.5, pz],
                      rotation=[-rz * 22, 0, rx * 22]))

# ─────────────────────────── кубы ───────────────────────────
# (bone, origin, size, material, tag)  material: flesh|bone  tag: ''|fissure|ganglia_tip
CUBES = []
# кратер: 4 перекрывающихся пластины-кольца, основание строго Y=0, толщины разные (D5)
CUBES += [
    ("root", [-12, 0, -12], [24, 1.2, 5.5], "flesh", ""),    # north rim
    ("root", [-12, 0, 6.5], [24, 1.6, 5.5], "flesh", ""),    # south rim
    ("root", [-12, 0, -7], [5.5, 2.0, 14], "flesh", ""),     # west rim
    ("root", [6.5, 0, -7], [5.5, 2.4, 14], "flesh", ""),     # east rim
]
# позвоночный ствол (компактное сечение)
CUBES += [
    ("spinal_column_base", [-1.5, 2.5, -1.5], [3.0, 11.0, 3.0], "flesh", ""),
    ("spinal_column_mid", [-1.5, 13.5, -1.5], [3.0, 10.0, 3.0], "flesh", ""),
    ("spinal_column_top", [-2.0, 23.5, -2.0], [4.0, 4.0, 4.0], "flesh", ""),
]
# мозг: центр + асимметричные доли + фиссуры (12 кубов)
CUBES += [
    ("cerebrum_core", [-4.0, 27, -4.0], [8.0, 7.0, 7.5], "flesh", ""),
    ("lobe_frontal_l1", [-4.6, 31, -5.6], [4.0, 3.6, 2.8], "flesh", ""),
    ("lobe_frontal_l2", [-4.2, 28, -6.0], [3.6, 3.0, 2.4], "flesh", ""),
    ("lobe_frontal_r1", [0.6, 31.4, -5.4], [4.4, 3.4, 3.0], "flesh", ""),
    ("lobe_frontal_r2", [0.9, 28.2, -5.8], [3.8, 2.8, 2.6], "flesh", ""),
    ("lobe_parietal_l", [-4.8, 33.6, -2.6], [4.6, 3.2, 5.6], "flesh", ""),
    ("lobe_parietal_r", [0.2, 34.2, -2.2], [5.0, 3.0, 6.0], "flesh", ""),
    ("lobe_temporal_l", [-5.6, 27.6, -2.0], [2.4, 3.6, 4.6], "flesh", ""),
    ("lobe_temporal_r", [3.8, 28.0, -1.6], [2.6, 3.8, 5.0], "flesh", ""),
    ("lobe_occipital_core", [-3.2, 29.0, 3.0], [6.4, 4.6, 2.8], "flesh", ""),
    ("neural_fissure_depths", [-0.4, 30.0, -5.2], [0.8, 4.6, 1.8], "flesh", "fissure"),
    ("neural_fissure_depths", [-3.6, 32.8, -4.8], [7.2, 0.7, 1.4], "flesh", "fissure"),
]
# жгуты: 4 x (base->tip), свисают под ядром (целочисленные)
for i, (gx, gz) in enumerate([(-3, -3), (3, -3), (-3, 2), (3, 2)], 1):
    CUBES.append((f"ganglion_{i}_base", [gx - 0.5, 25.0, gz - 0.5], [1, 3, 1], "flesh", ""))
    CUBES.append((f"ganglion_{i}_tip", [gx - 0.5, 22.0, gz - 0.5], [1, 3, 1], "flesh", "ganglia_tip"))
# костяные рёбра: 6 x (base->mid->tip), сужение 2->1->1 (целочисленные)
for i, (px, pz) in enumerate(RIB_POS, 1):
    CUBES.append((f"rib_{i}_base", [px - 1.0, 26.0, pz - 1.0], [2, 6, 2], "bone", ""))
    CUBES.append((f"rib_{i}_mid", [px - 0.5, 31.5, pz - 0.5], [1, 5, 1], "bone", ""))
    CUBES.append((f"rib_{i}_tip", [px - 0.5, 35.5, pz - 0.5], [1, 4, 1], "bone", ""))


def build_cubes_jittered():
    """Уникальный суб-воксельный джиттер ломает случайные компланарности Д5.
    Кратер: Y строго 0 (земля), джиттер только X/Z. Прочие: XYZ."""
    out = []
    for k, (bone, origin, size, mat, tag) in enumerate(CUBES):
        o = list(origin)
        jx, jz = k * 0.0071, k * 0.0083
        o[0] = round(o[0] + jx, 4)
        o[2] = round(o[2] + jz, 4)
        if bone != "root":
            o[1] = round(o[1] + k * 0.0053, 4)
        out.append(dict(bone=bone, origin=o, size=list(size), material=mat, tag=tag, idx=k))
    return out


def make_geo(cubes, uvmap):
    bones_json = []
    for b in BONES:
        bj = {"name": b["name"], "pivot": b["pivot"]}
        if "parent" in b:
            bj["parent"] = b["parent"]
        if b.get("rotation"):
            bj["rotation"] = b["rotation"]
        bcubes = []
        for c in cubes:
            if c["bone"] != b["name"]:
                continue
            uv = {}
            for f in gr.FACES:
                u, v, w, h = uvmap[(c["idx"], f)]
                uv[f] = {"uv": [u, v], "uv_size": [w, h]}
            bcubes.append({"origin": c["origin"], "size": c["size"], "uv": uv})
        if bcubes:
            bj["cubes"] = bcubes
        bones_json.append(bj)
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.carnis.cerebral_nexus",
                "texture_width": TEX_W, "texture_height": TEX_H,
                "visible_bounds_width": 3, "visible_bounds_height": 3.5,
                "visible_bounds_offset": [0, 1.25, 0],
            },
            "bones": bones_json,
        }],
    }


def d5_check(geo_path):
    spec = importlib.util.spec_from_file_location("geo_pairs_d5", ROOT / "02-reviewer/tools/geo_pairs_d5.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cubes = mod.load_cubes(str(geo_path))
    pairs = mod.classify(mod.find_pairs(cubes), cubes)
    visible = [p for p in pairs if p["class"] == "ВИДИМАЯ"]
    dead = mod.dead_cubes(cubes)
    return visible, dead, pairs, cubes


def hash_noise(x, y, salt=0):
    h = (x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def build_texture(cubes, uvmap):
    """Диффуз: синусоидальные извилины плоти + градиент минерализации кости.
    Квантильное разбиение тона на 7 цветов BASELINE (гарантия топ ≤35%, цветов ≥7).
    Эмиссив Р-3: только фиссуры и кончики жгутов, ровно (255,92,57)."""
    tone = np.full((TEX_H, TEX_W), np.nan)
    for c in cubes:
        seg = 0.0
        if c["material"] == "bone":
            seg = 0.12 if c["bone"].endswith("_base") else (0.40 if c["bone"].endswith("_mid") else 0.66)
        brain = c["bone"].startswith("lobe") or c["bone"] in ("cerebrum_core", "neural_fissure_depths")
        for f in gr.FACES:
            u, v, w, h = uvmap[(c["idx"], f)]
            for yy in range(h):
                for xx in range(w):
                    px, py = u + xx, v + yy
                    if not (0 <= px < TEX_W and 0 <= py < TEX_H):
                        continue
                    n = hash_noise(px, py, c["idx"])
                    if c["tag"] == "fissure":
                        t = 0.04 + n * 0.06
                    elif c["material"] == "bone":
                        t = seg + (yy / max(h - 1, 1)) * 0.22 + (n - 0.5) * 0.10
                        if hash_noise(px, py, 999) > 0.93:
                            t -= 0.18  # микропоры
                    elif brain:
                        t = (0.5 + 0.20 * math.sin(0.9 * xx + 0.4 * yy + c["idx"])
                             + 0.15 * math.sin(1.7 * yy + 0.3 * xx + 1.3)
                             + 0.09 * math.sin(2.6 * xx - 1.1 * yy) + (n - 0.5) * 0.10)
                    else:
                        t = (0.45 + 0.18 * math.sin(0.55 * xx + c["idx"] * 0.7)
                             + 0.10 * (yy / max(h - 1, 1)) + (n - 0.5) * 0.12)
                    tone[py, px] = max(0.0, min(1.0, t))
    mask = ~np.isnan(tone)
    vals = tone[mask]
    order = np.argsort(vals, kind="stable")
    ranks = np.empty(len(vals), dtype=int)
    ranks[order] = np.arange(len(vals)) * 7 // len(vals)
    idximg = np.zeros((TEX_H, TEX_W), dtype=int)
    idximg[mask] = ranks
    tex = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    tp = tex.load()
    for y in range(TEX_H):
        for x in range(TEX_W):
            if mask[y, x]:
                tp[x, y] = BASELINE[idximg[y, x]] + (255,)
    glow = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    gp = glow.load()
    for c in cubes:
        if c["tag"] not in ("fissure", "ganglia_tip"):
            continue
        for f in gr.FACES:
            u, v, w, h = uvmap[(c["idx"], f)]
            for yy in range(h):
                for xx in range(w):
                    px, py = u + xx, v + yy
                    if not (0 <= px < TEX_W and 0 <= py < TEX_H):
                        continue
                    if c["tag"] == "ganglia_tip" and f in ("north", "south", "east", "west") and yy < h * 0.45:
                        continue  # светим только нижнюю половину кончика
                    gp[px, py] = GLOW + (255,)
    return tex, glow


def _kf(times, fn):
    return {("%.2f" % t): fn(t) for t in times}


def build_animations():
    """20 fps, замкнутый idle. psychic_pulse и death — one-shot."""
    W = 2 * math.pi / 1.5  # период 1.5 с -> 2 цикла в idle 3.0 с (замыкание)
    W2 = 2 * math.pi / 3.0
    idle_t = [round(i * 0.05, 2) for i in range(61)]
    idle = {"loop": True, "animation_length": 3.0, "bones": {}}
    left = ["lobe_frontal_l1", "lobe_frontal_l2", "lobe_parietal_l", "lobe_temporal_l"]
    right = ["lobe_frontal_r1", "lobe_frontal_r2", "lobe_parietal_r", "lobe_temporal_r"]
    for b in left:
        idle["bones"][b] = {"scale": _kf(idle_t, lambda t: [round(1 + 0.05 * math.sin(W * t), 4)] * 3)}
    for b in right:
        idle["bones"][b] = {"scale": _kf(idle_t, lambda t: [round(1 + 0.05 * math.sin(W * t + math.pi + 0.4 * W), 4)] * 3)}
    idle["bones"]["cerebrum_core"] = {"scale": _kf(idle_t, lambda t: [round(1 + 0.025 * math.sin(W * t + 0.7), 4)] * 3)}
    idle["bones"]["spinal_column_mid"] = {"rotation": _kf(idle_t, lambda t: [round(1.2 * math.sin(W * t), 3), 0, round(0.8 * math.sin(W * t + 1.0), 3)])}
    for i in range(1, 5):
        ph = i * 0.9
        idle["bones"][f"ganglion_{i}_base"] = {"rotation": _kf(idle_t, lambda t, ph=ph: [round(2.5 * math.sin(W2 * t + ph), 3), 0, round(2.0 * math.sin(W2 * t + ph + 0.5), 3)])}
        idle["bones"][f"ganglion_{i}_tip"] = {"rotation": _kf(idle_t, lambda t, ph=ph: [round(6.0 * math.sin(W2 * t + ph - 0.4), 3), 0, round(5.0 * math.sin(W2 * t + ph + 0.2), 3)])}
    for i, (px, pz) in enumerate(RIB_POS, 1):
        rx, rz = px / 8.5, (pz + 0.5) / 8.5
        idle["bones"][f"rib_{i}_mid"] = {"rotation": _kf(idle_t, lambda t, rx=rx, rz=rz: [round(-rz * 1.5 * math.sin(W * t + i), 3), 0, round(rx * 1.5 * math.sin(W * t + i), 3)])}

    # psychic_pulse: сжатие+смыкание (0-0.6) -> выброс+раскрытие (0.6-0.8) -> релаксация (0.8-1.5)
    pp_t = [0.0, 0.3, 0.6, 0.7, 0.8, 1.0, 1.2, 1.5]
    pp = {"loop": False, "animation_length": 1.5, "bones": {}}
    core_s = {0.0: 1.0, 0.3: 0.94, 0.6: 0.86, 0.7: 1.16, 0.8: 1.10, 1.0: 1.04, 1.2: 1.0, 1.5: 1.0}
    pp["bones"]["cerebrum_core"] = {"scale": {("%.2f" % t): [round(core_s[t], 4)] * 3 for t in pp_t}}
    rib_amp = {0.0: 0, 0.3: 8, 0.6: 16, 0.7: -22, 0.8: -16, 1.0: -6, 1.2: 0, 1.5: 0}
    for i, (px, pz) in enumerate(RIB_POS, 1):
        rx, rz = px / 8.5, (pz + 0.5) / 8.5
        pp["bones"][f"rib_{i}_mid"] = {"rotation": {("%.2f" % t): [round(-rz * rib_amp[t], 3), 0, round(rx * rib_amp[t], 3)] for t in pp_t}}
        pp["bones"][f"rib_{i}_tip"] = {"rotation": {("%.2f" % t): [round(-rz * rib_amp[t] * 1.3, 3), 0, round(rx * rib_amp[t] * 1.3, 3)] for t in pp_t}}
    pp["bones"]["spinal_column_mid"] = {"rotation": {("%.2f" % t): [round(-3 * math.sin(math.pi * t / 1.5), 3), 0, 0] for t in pp_t}}

    # death: раскрытие+опадание рёбер, потеря тургора мозга (Y вниз, X/Z растекание)
    d_t = [0.0, 0.5, 1.0, 1.5, 2.0]
    death = {"loop": False, "animation_length": 2.0, "bones": {}}
    sy = {0.0: 1.0, 0.5: 0.85, 1.0: 0.70, 1.5: 0.60, 2.0: 0.55}
    sxz = {0.0: 1.0, 0.5: 1.08, 1.0: 1.16, 1.5: 1.22, 2.0: 1.25}
    # масштабируем только ядро: доли наследуют трансформ родителя (без двойного сжатия)
    death["bones"]["cerebrum_core"] = {"scale": {("%.2f" % t): [round(sxz[t], 4), round(sy[t], 4), round(sxz[t], 4)] for t in d_t}}
    droop = {0.0: 0, 0.5: -12, 1.0: -26, 1.5: -38, 2.0: -46}
    for i, (px, pz) in enumerate(RIB_POS, 1):
        rx, rz = px / 8.5, (pz + 0.5) / 8.5
        death["bones"][f"rib_{i}_mid"] = {"rotation": {("%.2f" % t): [round(rz * droop[t] * 0.5 + 6 * (t / 2), 3), 0, round(-rx * droop[t] * 0.5, 3)] for t in d_t}}
        death["bones"][f"rib_{i}_tip"] = {"rotation": {("%.2f" % t): [round(rz * droop[t] * 0.7 + 10 * (t / 2), 3), 0, round(-rx * droop[t] * 0.7, 3)] for t in d_t}}
    death["bones"]["spinal_column_base"] = {"rotation": {("%.2f" % t): [round(8 + 6 * (t / 2), 3), 0, round(4 * (t / 2), 3)] for t in d_t}}

    return {"format_version": "1.8.0", "animations": {
        "animation.cerebral_nexus.idle": idle,
        "animation.cerebral_nexus.psychic_pulse": pp,
        "animation.cerebral_nexus.death": death,
    }}


def build_preview(bones, cubes, tex, glow, path):
    geo_cubes = [{"bone": c["bone"], "origin": c["origin"], "size": c["size"], "uv": c["uv"]} for c in cubes]
    S = 200
    views = [gr.render_model(bones, geo_cubes, tex, glow, yaw_deg=y, canvas=S, px_per_unit=4.6, glow_boost=0.9) for y in range(0, 360, 45)]
    panels = []
    atlas = tex.resize((256, 256), Image.NEAREST)
    gmask = glow.resize((256, 256), Image.NEAREST)
    panels.append(("diffuse 64x64 (zoom)", atlas))
    panels.append(("glowmask R-3 (zoom)", gmask))
    brain = [c for c in geo_cubes if c["bone"].startswith("lobe") or c["bone"] in ("cerebrum_core", "neural_fissure_depths")]
    ribs = [c for c in geo_cubes if c["bone"].startswith("rib_")]
    gang = [c for c in geo_cubes if c["bone"].startswith("ganglion_")]
    panels.append(("cerebrum + fissure glow", gr.render_model(bones, brain, tex, glow, yaw_deg=25, canvas=256, px_per_unit=13, glow_boost=1.0)))
    panels.append(("bone cage (mineral gradient)", gr.render_model(bones, ribs, tex, None, yaw_deg=25, canvas=256, px_per_unit=11)))
    panels.append(("ganglia tips glow", gr.render_model(bones, gang, tex, glow, yaw_deg=25, canvas=256, px_per_unit=22, glow_boost=1.0)))
    W = S * 8
    H = S + 30 + 256 + 30
    dash = Image.new("RGB", (W, H), (18, 16, 20))
    d = ImageDraw.Draw(dash)
    for i, im in enumerate(views):
        dash.paste(im, (i * S, 0))
        d.text((i * S + 6, S + 6), "yaw %d" % (i * 45), fill=(210, 200, 200))
    x = 0
    for label, im in panels:
        dash.paste(im, (x, S + 30))
        d.text((x + 6, S + 30 + 258), label, fill=(210, 200, 200))
        x += 256 + 12
    d.text((6, H - 16), "cerebral_nexus | BlockEntity | 45 cubes | 24x24x39.7 | D5=0/0 | palette PALETTE.md | glow R-3 #FF5C39", fill=(150, 140, 145))
    dash.save(path)
    return dash.size


def build_anim_preview(bones, cubes, tex, glow, anim, path):
    geo_cubes = [{"bone": c["bone"], "origin": c["origin"], "size": c["size"], "uv": c["uv"]} for c in cubes]
    A = anim["animations"]

    def pose_at(name, t):
        out = {}
        for bn, ch in A[name]["bones"].items():
            out[bn] = {}
            for kind, kf in ch.items():
                key = "%.2f" % t
                if key in kf:
                    out[bn][kind] = kf[key]
        return out

    panels = [("idle t=0.0", "animation.cerebral_nexus.idle", 0.0),
              ("psychic_pulse compress t=0.6", "animation.cerebral_nexus.psychic_pulse", 0.6),
              ("psychic_pulse burst t=0.7", "animation.cerebral_nexus.psychic_pulse", 0.7),
              ("psychic_pulse relax t=1.5", "animation.cerebral_nexus.psychic_pulse", 1.5),
              ("death t=1.0", "animation.cerebral_nexus.death", 1.0),
              ("death t=2.0", "animation.cerebral_nexus.death", 2.0)]
    S = 260
    dash = Image.new("RGB", (S * len(panels), S + 30), (18, 16, 20))
    d = ImageDraw.Draw(dash)
    for i, (lab, name, t) in enumerate(panels):
        im = gr.render_model(bones, geo_cubes, tex, glow, yaw_deg=25, canvas=S, px_per_unit=5.6, glow_boost=0.9, anim=pose_at(name, t))
        dash.paste(im, (i * S, 0))
        d.text((i * S + 6, S + 6), lab, fill=(210, 200, 200))
    dash.save(path)
    return dash.size


def main():
    cubes = build_cubes_jittered()
    print("кубов: %d, костей: %d" % (len(cubes), len(BONES)))
    assert 35 <= len(cubes) <= 45, "бюджет кубов"

    # UV: все грани, тексель 1:1. Низ кратера (земля, не виден) — один общий регион.
    rects = [(("ground", "down"), 24, 6)]
    for c in cubes:
        fs = gr.face_sizes(c["size"])
        for f in gr.FACES:
            if c["bone"] == "root" and f == "down":
                continue
            rects.append(((c["idx"], f), fs[f][0], fs[f][1]))
    uvmap, used, overflow = gr.pack_uv(rects, TEX_W, TEX_H)
    ground_rect = uvmap[("ground", "down")]
    for c in cubes:
        if c["bone"] == "root":
            uvmap[(c["idx"], "down")] = ground_rect
    # общий регион земли намеренно разделён 4 гранями — исключаем дубли из проверки
    uniq = {k: v for k, v in uvmap.items() if not (isinstance(k[0], int) and cubes[k[0]]["bone"] == "root" and k[1] == "down")}
    over = gr.uv_overlap(uniq)
    print("UV: использовано %d/%d px (%.1f%%), overflow=%s, пересечений=%d" % (
        used, TEX_W * TEX_H, 100 * used / (TEX_W * TEX_H), overflow, over))

    geo = make_geo(cubes, uvmap)
    models = ART / "models"; models.mkdir(parents=True, exist_ok=True)
    geo_path = models / "cerebral_nexus.geo.json"
    geo_path.write_text(json.dumps(geo, ensure_ascii=False, indent=2), encoding="utf-8")

    visible, dead, pairs, d5cubes = d5_check(geo_path)
    print("Д5: видимых=%d, мёртвых=%d, всего пар=%d" % (len(visible), len(dead), len(pairs)))
    for p in visible[:12]:
        print("  ВИДИМАЯ #%d/%s + #%d/%s %s%s пл=%g площ=%g" % (
            p["i"], d5cubes[p["i"]]["bone"], p["j"], d5cubes[p["j"]]["bone"],
            p["axis"], "+" if p["sign"] > 0 else "-", p["plane"], p["area"]))
    for d in dead[:8]:
        print("  МЁРТВЫЙ #%d/%s внутри #%d/%s" % (
            d["inner"], d5cubes[d["inner"]]["bone"], d["outer"], d5cubes[d["outer"]]["bone"]))

    # габариты raw
    lo = np.min([c["origin"] for c in cubes], axis=0)
    hi = np.max([np.array(c["origin"]) + c["size"] for c in cubes], axis=0)
    print("raw габарит: X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]  (Ш×Г×В = %.1f×%.1f×%.1f)" % (
        lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], hi[0] - lo[0], hi[2] - lo[2], hi[1] - lo[1]))

    if overflow or over or visible or dead:
        print("ГЕОМЕТРИЯ/UV: ТРЕБУЕТ ДОРАБОТКИ")
        return 2
    print("ГЕОМЕТРИЯ/UV: ЧИСТО (Д5=0/0, UV без пересечений)")

    # прикрепляем UV к кубам для рендера
    for c in cubes:
        c["uv"] = {f: {"uv": list(uvmap[(c["idx"], f)][:2]), "uv_size": list(uvmap[(c["idx"], f)][2:])} for f in gr.FACES}

    tex, glow = build_texture(cubes, uvmap)
    texd = ART / "textures"; texd.mkdir(parents=True, exist_ok=True)
    tex.save(texd / "cerebral_nexus.png")
    glow.save(texd / "cerebral_nexus_glowmask.png")
    # алиас GENESIS _e.png (канон репозитория — _glowmask.png)
    glow.save(texd / "cerebral_nexus_e.png")
    opaque = [p[:3] for p in tex.get_flattened_data() if p[3] > 0]
    from collections import Counter
    cnt = Counter(opaque)
    top = cnt.most_common(1)[0]
    print("Текстура: цветов=%d, топ=%.1f%%, альфы=%s" % (
        len(cnt), 100 * top[1] / len(opaque), sorted({p[3] for p in tex.get_flattened_data()})))
    gop = {p for p in glow.get_flattened_data() if p[3] > 0}
    print("Glowmask: непрозрачных цветов=%d, px=%d, цвет=%s" % (len(gop), sum(1 for p in glow.get_flattened_data() if p[3] > 0), gop))

    anim = build_animations()
    adir = ART / "animations"; adir.mkdir(parents=True, exist_ok=True)
    (adir / "cerebral_nexus.animation.json").write_text(json.dumps(anim, ensure_ascii=False, indent=2), encoding="utf-8")
    # проверка замыкания idle
    idle = anim["animations"]["animation.cerebral_nexus.idle"]
    closed = all(list(ch.values())[0] == list(ch.values())[-1]
                 for b in idle["bones"].values() for ch in b.values())
    print("Анимации: %s | idle замкнут=%s" % (list(anim["animations"]), closed))

    prev = ART / "previews"; prev.mkdir(parents=True, exist_ok=True)
    size = build_preview(BONES, cubes, tex, glow, prev / "cerebral_nexus_preview.png")
    print("Превью: %s" % (size,))
    asize = build_anim_preview(BONES, cubes, tex, glow, anim, prev / "cerebral_nexus_anim.png")
    print("Аним-превью: %s" % (asize,))

    # пакет сдачи (drop-in по текущему пути регистрации entity/)
    deliver = ART / "deliverables"; deliver.mkdir(parents=True, exist_ok=True)
    zpath = deliver / "Carnis_3.9.1_cerebral_nexus.zip"
    base = "src/main/resources/assets/carnis/"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(geo_path, base + "geo/entity/cerebral_nexus.geo.json")
        z.write(texd / "cerebral_nexus.png", base + "textures/entity/cerebral_nexus.png")
        z.write(texd / "cerebral_nexus_glowmask.png", base + "textures/entity/cerebral_nexus_glowmask.png")
        z.write(adir / "cerebral_nexus.animation.json", base + "animations/entity/cerebral_nexus.animation.json")
        z.writestr("MANIFEST.txt", "cerebral_nexus BlockEntity rebuild | 45 cubes | 64x64 | D5=0/0 | R-3\n")
    print("Пакет: %s" % zpath)
    return 0


if __name__ == "__main__":
    sys.exit(main())
