"""
tendrils_gen.py — генератор набора вариантов `creeping_tendrils` (A3/A6), 64×64, cutout.

Архитектура (шестая итерация — после разбора исходной текстуры 16×16)
------------------------------------------------------------------------
Исходная `creeping_tendrils.png` — это плотная мясная ткань: 44,5 % покрытия,
короткие волокна разной длины, тёмный кант по краю, светлая сердцевина.
Новая вариация сохраняет эту природу, но:

* Плитка собрана как ОБЪЕДИНЕНИЕ ВОЛОКОН (капсулы с меняющимся радиусом)
  в знаковом поле (SDF):
  — «волокно» — короткий (18–28 px) мягкий канат: толщина 9–12 px,
    изгиб — по общему направлению ткани с разбросом ±35°;
  — «узел» — округлая масса, где волокна сходятся.
  Волокна перекрещиваются и смыкаются, поэтому непрерывная линия в скелете
  никогда не длиннее 32 px — узлы делят её на короткие ветви.
* Плотность 44–56 % покрытия — как в исходной текстуре; пустоты собраны
  в небольшие округлые «карманы», а не в широкие пустые дорожки.
* Кольцо прозрачности 1 px по внешнему краю — одинаково у ВСЕХ вариантов:
  верх/низ и лево/право побайтово совпадают, любая пара стыкуется.
* Варианты отличаются направлением ткани, густотой и разбросом волокон —
  не формой отдельного пятна. Сосед из другого варианта читается как
  «другое место той же ткани».
* Никаких волн, полос и параллельных направлений.
* Детерминированность: ни `random`, ни времени — только хеш-шум с явными seed.

Запуск:  python3 tools/tendrils_gen.py <каталог вывода>
"""

from __future__ import annotations

import json
import math
import os
import sys

from PIL import Image

SIZE = 64
BORDER = 1           # прозрачное кольцо по внешнему краю плитки (одинаково у всех)
SAFE = 1             # содержимое не ближе SAFE px к краю плитки

PAL = {
    "clear":   (0, 0, 0, 0),
    "deep":    (84, 40, 54, 255),
    "base":    (104, 47, 64, 255),
    "steady":  (161, 90, 96, 255),
    "mid":     (157, 80, 94, 255),
    "warm":    (179, 106, 105, 255),
    "light":   (196, 126, 119, 255),
    "hilite":  (209, 144, 130, 255),
}

# порядок тонов от тёмного к светлому (по воспринимаемой яркости)
TONE_ORDER = ["deep", "base", "mid", "steady", "warm", "light", "hilite"]

# упорядоченный дизеринг Байера 4×4 — мягкие переходы между тонами
BAYER4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)

MAX_STROKE = 30      # максимальная длина непрерывной линии, px (лимит ТЗ — 32)
MIN_STROKE = 8       # минимальная толщина штриха, px (лимит ТЗ — 8 = 2 px в 16×16)
LIGHT_DIR = (-0.55, -0.835)   # вектор «к свету» (сверху-слева)


def _hash(x, y, seed):
    n = (x * 0x1F1F1F1F + y * 0x9E3779B9 + seed * 0x85EBCA6B) & 0xFFFFFFFF
    n = ((n ^ (n >> 15)) * 0x2545F491) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 0x27D4EB2F) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967295.0


def _smooth(t):
    return t * t * (3.0 - 2.0 * t)


def vnoise(x, y, seed, scale):
    fx, fy = x / scale, y / scale
    x0, y0 = math.floor(fx), math.floor(fy)
    tx, ty = _smooth(fx - x0), _smooth(fy - y0)
    a = _hash(x0, y0, seed)
    b = _hash(x0 + 1, y0, seed)
    c = _hash(x0, y0 + 1, seed)
    d = _hash(x0 + 1, y0 + 1, seed)
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def fbm(x, y, seed, scale, octaves=3):
    tot, amp, norm, freq = 0.0, 1.0, 0.0, 1.0
    for o in range(octaves):
        tot += amp * vnoise(x * freq, y * freq, seed + o * 977, scale)
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return tot / norm


# ── примитив знакового поля ────────────────────────────────────────────
class Capsule:
    """Капсула: отрезок с линейно меняющимся радиусом и скруглёнными концами."""

    def __init__(self, p0, p1, r0, r1):
        self.p0, self.p1 = p0, p1
        self.r0, self.r1 = r0, r1

    def sdf(self, x, y):
        ax, ay = self.p0
        bx, by = self.p1
        vx, vy = bx - ax, by - ay
        s2 = vx * vx + vy * vy
        if s2 <= 1e-12:
            t = 0.0
        else:
            t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / s2))
        r = self.r0 + (self.r1 - self.r0) * t
        return math.hypot(x - (ax + t * vx), y - (ay + t * vy)) - r


class Blob:
    """Округлая масса с неровным краем."""

    def __init__(self, c, r, seed):
        self.c = c
        self.r = r
        self.seed = seed

    def sdf(self, x, y):
        dx = x - self.c[0]
        dy = y - self.c[1]
        d = math.hypot(dx, dy)
        wob = 0.10 * (fbm(x, y, self.seed, 11.0) - 0.5) * 2.0
        return d - (self.r * (1.0 + wob))


class Scene:
    """Объединение примитивов + освещение + запись в буфер."""

    def __init__(self, prims, seed):
        self.prims = prims
        self.seed = seed

    def field(self, x, y):
        best = 1e9
        for p in self.prims:
            d = p.sdf(x, y)
            if d < best:
                best = d
        return best

    def render(self):
        px = [[PAL["clear"]] * SIZE for _ in range(SIZE)]
        self.clipped = 0
        for y in range(SIZE):
            for x in range(SIZE):
                fx, fy = x + 0.5, y + 0.5
                f = self.field(fx, fy)
                if f > 0.0:
                    continue
                if x < SAFE or y < SAFE or x > SIZE - 1 - SAFE or y > SIZE - 1 - SAFE:
                    self.clipped += 1
                    continue
                depth = -f
                e = 0.7
                gx = self.field(fx + e, fy) - self.field(fx - e, fy)
                gy = self.field(fx, fy + e) - self.field(fx, fy - e)
                gn = math.hypot(gx, gy)
                if gn < 1e-6:
                    nx, ny = 0.0, 0.0
                else:
                    nx, ny = gx / gn, gy / gn
                lit = nx * LIGHT_DIR[0] + ny * LIGHT_DIR[1]
                px[y][x] = self._shade(depth, lit, fx, fy)
        return px

    def _shade(self, depth, lit, fx, fy):
        """Тон: тёмный кант по краю, тёплая сердцевина, светлая кромка со света.

        Переходы широкие и ровные — как в исходной текстуре 16×16; дизеринг
        работает только в самом узком переходе, чтобы не было «гравия».
        """
        mott = fbm(fx, fy, self.seed + 77, 13.0)
        level = 0.52 + 0.26 * lit
        level += 0.06 * (mott - 0.5)
        # мягкий тёмный кант по краю фигуры
        level -= 0.30 * max(0.0, 1.0 - depth / 4.5) ** 1.6
        # тёплое подсвечивание со стороны света — без резкой кромки
        level += 0.14 * max(0.0, lit - 0.1)
        n = len(TONE_ORDER)
        t = max(0.0, min(0.9999, level)) * (n - 1)
        lo = int(t)
        frac = t - lo
        if frac > 0.62:
            lo += 1
        elif frac > 0.38 and BAYER4[int(fy) % 4][int(fx) % 4] < 8:
            lo += 1
        return PAL[TONE_ORDER[min(lo, n - 1)]]


# ── построение варианта ────────────────────────────────────────────────
def _fibres(spec):
    """Раскладка волокон варианта: изогнутые мягкие канаты + массы-узлы.

    Каждое волокно — дуга из двух отрезков: так ткань не читается как
    набор параллельных «костей», а стена остаётся волокнистой.
    """
    seed = spec["seed"]
    prims = []
    lo, hi = SAFE + 4.0, SIZE - 1 - SAFE - 4.0
    base_dir = spec["dir"]
    for i in range(spec["fibres"]):
        h1 = _hash(i, 1, seed)
        h2 = _hash(i, 2, seed)
        h3 = _hash(i, 3, seed)
        h4 = _hash(i, 4, seed)
        h5 = _hash(i, 5, seed)
        # старт — по полосам, чтобы волокна распределялись по всей плитке
        band = (i + 0.5) / spec["fibres"]
        cx = lo + (hi - lo) * (h1 * 0.75 + 0.12)
        cy = lo + (hi - lo) * band
        ang = base_dir + (h2 - 0.5) * spec["spread"]
        length = spec["len_min"] + (spec["len_max"] - spec["len_min"]) * h3
        r0 = spec["r_min"] + (spec["r_max"] - spec["r_min"]) * h4
        # изгиб: дуга, уходящая в сторону от общего направления
        bend = (h5 - 0.5) * spec.get("bend", 9.0)
        a2 = ang + (h2 - 0.5) * 0.9
        p0 = (cx, cy)
        pm = (cx + math.cos(ang) * length * 0.5 - math.sin(ang) * bend,
              cy + math.sin(ang) * length * 0.5 + math.cos(ang) * bend)
        p1 = (pm[0] + math.cos(a2) * length * 0.5,
              pm[1] + math.sin(a2) * length * 0.5)
        # прижимаем к рабочему полю
        def cl(p):
            return (min(max(p[0], lo), hi), min(max(p[1], lo), hi))
        p0, pm, p1 = cl(p0), cl(pm), cl(p1)
        prims.append(Capsule(p0, pm, r0, r0 * 0.95))
        prims.append(Capsule(pm, p1, r0 * 0.95, r0 * 0.86))
    for j in range(spec["nodes"]):
        h1 = _hash(j, 11, seed)
        h2 = _hash(j, 12, seed)
        h3 = _hash(j, 13, seed)
        c = (lo + (hi - lo) * h1, lo + (hi - lo) * h2)
        prims.append(Blob(c, spec["node_r"] * (0.8 + 0.4 * h3), seed + 500 * (j + 1)))
    return prims


def _build(spec, index):
    seed = spec["seed"]
    return Scene(_fibres(spec), seed)


VARIANTS = [
    {
        # «вертикаль»: ткань тянется вверх, волокна плотные и короткие
        "name": "creeping_tendrils_a",
        "seed": 1101,
        "dir": -1.5708, "spread": 1.15,
        "fibres": 13, "len_min": 16.0, "len_max": 27.0, "bend": 9.0,
        "r_min": 4.6, "r_max": 6.0,
        "nodes": 3, "node_r": 7.5,
    },
    {
        # «диагональ»: направление по диагонали, волокна длиннее
        "name": "creeping_tendrils_b",
        "seed": 2202,
        "dir": -0.7854, "spread": 1.25,
        "fibres": 11, "len_min": 18.0, "len_max": 30.0, "bend": 11.0,
        "r_min": 4.6, "r_max": 6.1,
        "nodes": 3, "node_r": 8.0,
    },
    {
        # «горизонталь»: волокна почти поперечные, разброс больше
        "name": "creeping_tendrils_c",
        "seed": 3303,
        "dir": 0.1963, "spread": 1.35,
        "fibres": 12, "len_min": 17.0, "len_max": 29.0, "bend": 12.0,
        "r_min": 4.7, "r_max": 6.2,
        "nodes": 4, "node_r": 7.8,
    },
    {
        # «пятно»: меньше волокон, но крупнее массы-узлы
        "name": "creeping_tendrils_d",
        "seed": 4404,
        "dir": -1.1781, "spread": 1.45,
        "fibres": 9, "len_min": 15.0, "len_max": 26.0, "bend": 13.0,
        "r_min": 4.8, "r_max": 6.3,
        "nodes": 5, "node_r": 9.0,
    },
]


def generate(index):
    """Собрать вариант index: (изображение, статистика сборки)."""
    spec = VARIANTS[index]
    scene = _build(spec, index)
    px = scene.render()
    img = Image.new("RGBA", (SIZE, SIZE))
    img.putdata([px[y][x] for y in range(SIZE) for x in range(SIZE)])
    stats = {"clipped_px": scene.clipped}
    return img, stats


def params(index):
    spec = VARIANTS[index]
    return {
        "name": spec["name"],
        "seed": spec["seed"],
        "direction_deg": round(math.degrees(spec["dir"]), 1),
        "fibres": spec["fibres"],
        "nodes": spec["nodes"],
        "max_stroke_px": MAX_STROKE,
        "min_stroke_px": MIN_STROKE,
    }


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    meta = []
    for i, spec in enumerate(VARIANTS):
        img, stats = generate(i)
        path = os.path.join(out, spec["name"] + ".png")
        img.save(path)
        p = params(i)
        p["file"] = spec["name"] + ".png"
        p.update(stats)
        meta.append(p)
        print(f"{spec['name']}.png  {os.path.getsize(path)} Б  "
              f"срезано пикселей: {stats['clipped_px']}")
    with open(os.path.join(out, "PARAMS.json"), "w", encoding="utf-8") as fh:
        json.dump({"size": [SIZE, SIZE], "palette": {k: list(v) for k, v in PAL.items()},
                   "border_px": BORDER, "variants": meta},
                  fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
