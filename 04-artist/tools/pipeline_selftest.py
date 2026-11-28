#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pipeline_selftest.py — смоук-тест инструментария Художника (онбординг).

Проверяет замкнутый цикл: синтез текстуры -> палитра/альфа -> тексель 1:1 ->
сегментная цепочка -> изометрический рендер -> дашборд -> эмиссивная маска.

Ничего не моделирует: тестовый риг — три служебных куба (base/mid/tip),
текстура — синтетический свотч 16x16. Выходные PNG пишутся во временный
каталог (tempfile), репозиторий не засоряется.

Коды возврата: 0 — все ступени PASS, 2 — есть FAIL, 1 — ошибка запуска.
Запуск: .venv/bin/python 04-artist/tools/pipeline_selftest.py
"""
from __future__ import annotations

import importlib.util
import math
import sys
import tempfile
from pathlib import Path

try:
    import numpy as np
    import PIL
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover
    print("ОШИБКА: нужны Pillow и numpy (%s)" % exc)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[2]
RESULTS: list[tuple[str, bool, str]] = []

# BASELINE_PALETTE — источник правды: 04-artist/PALETTE.md §1
BASELINE = [(84, 40, 54), (104, 47, 64), (157, 80, 94), (161, 90, 96),
            (179, 106, 105), (196, 126, 119), (209, 144, 130)]
GLOW = (255, 92, 57)  # Р-3, 02-reviewer/alpha_rule.md часть II


def step(name: str, ok: bool, detail: str) -> None:
    RESULTS.append((name, ok, detail))
    print("  [%s] %-28s %s" % ("PASS" if ok else "FAIL", name, detail))


def pxdata(im: Image.Image) -> list:
    """Совместимость Pillow 13+: getdata deprecated, get_flattened_data — новый API."""
    if hasattr(im, "get_flattened_data"):
        return list(im.get_flattened_data())
    return list(im.getdata())


def det_noise(x: int, y: int) -> float:
    """Детерминированный шум без random (философия carnis_px.py)."""
    h = (x * 73856093) ^ (y * 19349663)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def synth_swatch(size: int = 16) -> Image.Image:
    """Свотч плоти: квантильное разбиение score на 7 цветов BASELINE (PALETTE.md §5)."""
    scores = []
    for y in range(size):
        for x in range(size):
            lum = 0.299 * 157 + 0.587 * 80 + 0.114 * 94
            score = lum + det_noise(x, y) * 40.0 + (y / size) * 25.0
            scores.append((score, x, y))
    scores.sort(key=lambda t: t[0])
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = im.load()
    n = len(scores)
    for i, (_, x, y) in enumerate(scores):
        px[x, y] = BASELINE[i * 7 // n] + (255,)
    return im


def load_shade_checker():
    p = ROOT / "04-artist/tools/shade_density.py"
    spec = importlib.util.spec_from_file_location("shade_density", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Изометрический рендер кубов (painter's algorithm, ортографическая проекция) ──

def box_uv_rects(uv, size):
    """Развертка box-UV [u,v] -> прямоугольники граней (Bedrock layout)."""
    w, h, d = size
    u, v = uv
    return {
        "up":    (u + d,         v,         w, d),
        "down":  (u + d + w,     v,         w, d),
        "east":  (u,             v + d,     d, h),
        "north": (u + d,         v + d,     w, h),
        "west":  (u + d + w,     v + d,     d, h),
        "south": (u + d + w + d, v + d,     w, h),
    }


def face_corners(origin, size):
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


NORMALS = {"up": (0, 1, 0), "down": (0, -1, 0), "east": (1, 0, 0),
           "west": (-1, 0, 0), "north": (0, 0, -1), "south": (0, 0, 1)}


def render_iso(cubes, tex: Image.Image, yaw_deg: float, px_per_unit: float = 10.0,
               canvas: int = 220) -> Image.Image:
    """cubes: список (origin, size, uv). Текстура сэмплируется NEAREST, 1 тексель = 1 px развертки."""
    yaw = math.radians(yaw_deg)
    cy, sy = math.cos(yaw), math.sin(yaw)
    view = (0.7, 0.9, 0.7)  # направление на камеру (после поворота yaw)
    faces = []
    for origin, size, uv in cubes:
        rects = box_uv_rects(uv, size)
        corners = face_corners(origin, size)
        for fname, pts in corners.items():
            nx, ny, nz = NORMALS[fname]
            rnx = nx * cy + nz * sy
            rnz = -nx * sy + nz * cy
            if rnx * view[0] + ny * view[1] + rnz * view[2] <= 0:
                continue  # задняя грань
            proj = []
            depth = 0.0
            for (x, y, z) in pts:
                rx = x * cy + z * sy
                rz = -x * sy + z * cy
                sx = (rx - rz) * 0.866
                syp = (rx + rz) * 0.5 - y
                proj.append((sx, syp))
                depth += rx + rz + y
            faces.append((depth / 4.0, proj, rects[fname]))
    faces.sort(key=lambda f: f[0])  # дальние -> ближние

    all_pts = [p for _, pts, _ in faces for p in pts]
    minx = min(p[0] for p in all_pts); maxx = max(p[0] for p in all_pts)
    miny = min(p[1] for p in all_pts); maxy = max(p[1] for p in all_pts)
    scale = min(px_per_unit, (canvas - 20) / max(maxx - minx, maxy - miny, 1e-6))
    ox = canvas / 2 - (minx + maxx) / 2 * scale
    oy = canvas / 2 - (miny + maxy) / 2 * scale

    out = Image.new("RGBA", (canvas, canvas), (24, 22, 26, 255))
    tex_px = tex.load()
    tw, th = tex.size
    draw = ImageDraw.Draw(out)
    for _, pts, (ru, rv, rw, rh) in faces:
        screen = [(p[0] * scale + ox, p[1] * scale + oy) for p in pts]
        # аффинная карта экранных координат -> UV (грань — параллелограмм)
        p0, p1, p3 = np.array(screen[0]), np.array(screen[1]), np.array(screen[3])
        e1, e2 = p1 - p0, p3 - p0
        mat = np.array([e1, e2]).T
        if abs(np.linalg.det(mat)) < 1e-9:
            continue
        inv = np.linalg.inv(mat)
        xs = [p[0] for p in screen]; ys = [p[1] for p in screen]
        x0, x1 = int(math.floor(min(xs))), int(math.ceil(max(xs)))
        y0, y1 = int(math.floor(min(ys))), int(math.ceil(max(ys)))
        shade = 0.72 + 0.28 * max(0.0, min(1.0, (pts[0][1] - miny) / max(maxy - miny, 1e-6)))
        for py in range(max(0, y0), min(canvas, y1 + 1)):
            for pxx in range(max(0, x0), min(canvas, x1 + 1)):
                ab = inv @ (np.array([pxx + 0.5, py + 0.5]) - p0)
                a, b = ab[0], ab[1]
                if -1e-6 <= a <= 1 + 1e-6 and -1e-6 <= b <= 1 + 1e-6:
                    u = int(ru + a * rw) % tw
                    v = int(rv + b * rh) % th
                    r, g, bl, al = tex_px[u, v]
                    if al == 0:
                        continue
                    out.putpixel((pxx, py), (int(r * shade), int(g * shade), int(bl * shade), 255))
        draw.line(screen + [screen[0]], fill=(10, 8, 10, 255), width=1)
    return out


def main() -> int:
    print("pipeline_selftest.py — смоук-тест инструментария Художника")
    print("Python %s | Pillow %s | numpy %s" % (
        sys.version.split()[0], PIL.__version__, np.__version__))
    tmp = Path(tempfile.mkdtemp(prefix="carnis_selftest_"))

    # 1. Синтез текстуры + палитра/альфа
    swatch = synth_swatch(16)
    swatch.save(tmp / "swatch.png")
    rgba = pxdata(swatch)
    alphas = {p[3] for p in rgba}
    opaque = [p[:3] for p in rgba if p[3] > 0]
    colors = set(opaque)
    top_share = max(opaque.count(c) for c in colors) / len(opaque)
    step("synth_palette", colors == set(BASELINE) and alphas == {255},
         "цветов=%d, альфы=%s, топ=%.1f%%" % (len(colors), sorted(alphas), top_share * 100))

    # 2. Порог светотени родным чекером проекта
    mod = load_shade_checker()
    ok, line = mod.check_image(swatch, "selftest_swatch", 0.35, 7)
    step("shade_density_gate", ok, line.strip())

    # 3. Тексель 1:1 — площадь UV-грани == площадь геометрической грани
    size = (6, 5, 4)
    rects = box_uv_rects((0, 0), size)
    areas_geo = {"up": 6 * 4, "down": 6 * 4, "east": 4 * 5, "north": 6 * 5, "west": 4 * 5, "south": 6 * 5}
    ok = all(abs(rects[f][2] * rects[f][3] - areas_geo[f]) < 1e-9 for f in rects)
    step("texel_density_1to1", ok, "6 граней, sum(UV)=%d == sum(geo)=%d" % (
        sum(r[2] * r[3] for r in rects.values()), sum(areas_geo.values())))

    # 4. Сегментная цепочка base->mid->tip с сужением (тестовый риг, не сущность)
    rig = [((-3, 0, -2), (6, 5, 4), (0, 0)),
           ((-1.5, 5, -1), (3, 4, 2), (0, 0)),
           ((-0.75, 9, -0.5), (1.5, 3, 1), (0, 0))]
    widths = [c[1][0] for c in rig]
    step("segmentation_chain", len(rig) == 3 and widths[0] > widths[1] > widths[2],
         "base->mid->tip, ширина %s" % widths)

    # 5. Изометрический рендер, 4 ракурса + зум-панель -> единый дашборд
    views = [render_iso(rig, swatch, yaw) for yaw in (0, 90, 180, 270)]
    zoom = swatch.resize((220, 220), Image.NEAREST)
    dash = Image.new("RGB", (220 * 4, 220 * 2 + 30), (18, 16, 20))
    d = ImageDraw.Draw(dash)
    for i, v in enumerate(views):
        dash.paste(v, (i * 220, 0))
        d.text((i * 220 + 8, 222), "yaw %d" % (i * 90), fill=(210, 200, 200))
    dash.paste(zoom, (0, 250))
    d.text((8, 472), "swatch 16x16 zoom x13.75 (NEAREST)", fill=(210, 200, 200))
    dash_path = tmp / "selftest_dashboard.png"
    dash.save(dash_path)
    step("iso_render_dashboard", dash.size == (880, 470) and dash_path.stat().st_size > 0,
         "%s, %d Б" % (dash.size, dash_path.stat().st_size))

    # 6. Эмиссивная маска: один цвет (255,92,57), альфа 0/255 (дисциплина Р-3)
    mask = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    mp = mask.load()
    for (x, y) in [(7, 2), (8, 2), (7, 3), (8, 3)]:
        mp[x, y] = GLOW + (255,)
    mask.save(tmp / "swatch_glowmask.png")
    mop = {p for p in pxdata(mask) if p[3] > 0}
    step("emissive_mask_R3", mop == {GLOW + (255,)} and {p[3] for p in pxdata(mask)} <= {0, 255},
         "непрозрачных цветов=%d, px=%d" % (len(mop), sum(1 for p in pxdata(mask) if p[3] > 0)))

    failed = [n for n, ok, _ in RESULTS if not ok]
    print("\nВременный каталог: %s" % tmp)
    if failed:
        print("ИТОГ: FAIL — %s" % ", ".join(failed))
        return 2
    print("ИТОГ: ВСЕ СТУПЕНИ PASS (%d/%d)" % (len(RESULTS), len(RESULTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
