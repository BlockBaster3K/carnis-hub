#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cerebral_nexus_showcase.py — витрина модели: hero-рендер + turntable-GIF (360° + idle).

Выход:
  04-artist/previews/cerebral_nexus_hero.png      (720x720, 3/4 ракурс, свечение Р-3)
  04-artist/previews/cerebral_nexus_turntable.gif (36 кадров, 420x420, вращение + idle-пульс)

Запуск: .venv/bin/python 04-artist/generators/cerebral_nexus_showcase.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04-artist/tools"))
import geo_render as gr  # noqa: E402

ART = ROOT / "04-artist"


def load_anim():
    return json.loads((ART / "animations/cerebral_nexus.animation.json").read_text(encoding="utf-8"))["animations"]


def sample_channel(kf, t):
    """Линейная интерполяция ключей {time_str: [x,y,z]} по времени t (циклически для loop)."""
    keys = sorted(float(k) for k in kf)
    if t <= keys[0]:
        return kf["%.2f" % keys[0]]
    if t >= keys[-1]:
        return kf["%.2f" % keys[-1]]
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        if a <= t <= b:
            f = (t - a) / (b - a) if b > a else 0.0
            va, vb = kf["%.2f" % a], kf["%.2f" % b]
            return [va[j] + (vb[j] - va[j]) * f for j in range(len(va))]
    return kf["%.2f" % keys[-1]]


def idle_pose(anim, t):
    a = anim["animation.cerebral_nexus.idle"]
    L = a["animation_length"]
    tt = t % L
    out = {}
    for bn, ch in a["bones"].items():
        out[bn] = {kind: sample_channel(kf, tt) for kind, kf in ch.items()}
    return out


def vignette(im, strength=0.55):
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-w * 0.25, -h * 0.25, w * 1.25, h * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(w * 0.12))
    dark = Image.new("RGB", (w, h), (10, 8, 12))
    base = im.convert("RGB")
    comp = Image.composite(base, dark, mask.point(lambda v: int(v * (1 - strength) + 255 * strength)))
    return comp


def main():
    bones, cubes, desc = gr.load_geo(ART / "models/cerebral_nexus.geo.json")
    tex = Image.open(ART / "textures/cerebral_nexus.png").convert("RGBA")
    glow = Image.open(ART / "textures/cerebral_nexus_glowmask.png").convert("RGBA")
    anim = load_anim()
    prev = ART / "previews"; prev.mkdir(parents=True, exist_ok=True)

    # hero
    hero = gr.render_model(bones, cubes, tex, glow, yaw_deg=33, canvas=720, px_per_unit=15.0, glow_boost=1.05)
    hero = vignette(hero, 0.5)
    hd = ImageDraw.Draw(hero)
    hd.text((24, 22), "CARNIS · cerebral_nexus", fill=(225, 205, 200), font=font(22))
    hd.text((24, 52), "Церебральный Нексус Улья · BlockEntity · 45 кубов · Р-3 #FF5C39", fill=(150, 135, 140), font=font(14))
    hero.save(prev / "cerebral_nexus_hero.png")
    print("hero:", hero.size)

    # turntable: 36 кадров, один оборот + один цикл idle
    frames = []
    N = 36
    for i in range(N):
        yaw = i * (360 / N)
        t = i * (3.0 / N)
        pose = idle_pose(anim, t)
        fr = gr.render_model(bones, cubes, tex, glow, yaw_deg=yaw, canvas=420, px_per_unit=8.8, glow_boost=1.0, anim=pose)
        frames.append(fr.convert("RGB"))
    frames[0].save(prev / "cerebral_nexus_turntable.gif", save_all=True, append_images=frames[1:],
                   duration=90, loop=0, optimize=True)
    print("turntable:", N, "frames ->", (prev / "cerebral_nexus_turntable.gif").stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
