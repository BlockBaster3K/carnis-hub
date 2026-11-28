#!/usr/bin/env python3
"""flesh_veins t1..t4 × 3 вариации — по концепту 3.8.2.

Геометрия узора (общая для ВСЕХ 12 текстур — «швы сходятся»):
  * полоса по 4 краям плитки (шов продолжается на соседнем блоке);
  * главная диагональ из левого-нижнего в правый-верхний угол;
  * ветвь от середины диагонали, уходящая на два края.

Один и тот же рисунок сети, разная плотность и насыщенность по тиру:
  t1 — 2 px, редкие волоски;       t2 — 3 px, волоски чаще;
  t3 — 4 px, стенки;               t4 — 5 px, узкие просветы плоти.

Альфа: всё, что не жила, — alpha=0 (cutout). Элемент модели лежит на
поверхности блока (z=0.1..0.2), поэтому сквозь прозрачные пиксели виден
базовый flesh_block — как требует концепт.
"""
from __future__ import annotations

import json
import math
import os
import sys

from PIL import Image

S = 16
OUT = sys.argv[1] if len(sys.argv) > 1 else "04-artist/patch381/assets"

# Палитра плоти (совпадает с flesh_veins.png старого пакета: 7 цветов).
PALETTE = [
    (0x4C, 0x0A, 0x16),  # 0 тёмный край жилы
    (0x56, 0x11, 0x1D),  # 1
    (0x60, 0x18, 0x24),  # 2
    (0x6A, 0x1F, 0x2B),  # 3
    (0x74, 0x26, 0x32),  # 4
    (0x7E, 0x2D, 0x39),  # 5
    (0x88, 0x34, 0x40),  # 6 светлый гребень
]

TIER = {
    # толщина жилы в пикселях: t1 тонкая, t4 почти перекрывает плоть
    1: dict(width=2),
    2: dict(width=3),
    3: dict(width=4),
    4: dict(width=5),
}

# Три вариации: точка-источник и три ветви, уходящие каждая в свой край карты.
# Ветви уходят ЗА границу плитки — на соседнем блоке они продолжаются, поэтому
# швы сходятся между любыми вариациями и любыми тирами.
VARIANT = {
    0: dict(anchor=(5.5, 10.5), ends=[(5.5, 0.0), (0.0, 14.5), (16.0, 8.5)]),
    1: dict(anchor=(9.5, 6.5), ends=[(15.5, 1.0), (1.0, 5.0), (6.0, 16.0)]),
    2: dict(anchor=(11.5, 11.5), ends=[(16.0, 3.0), (0.0, 0.5), (3.0, 16.0)]),
}


def seg_dist(px, py, x1, y1, x2, y2):
    """Расстояние от точки до отрезка."""
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def build(tier: int, variant: int):
    """Карта (расстояние до жилы, продольная координата, поперечная)."""
    width = TIER[tier]["width"]
    var = VARIANT[variant]
    ax, ay = var["anchor"]
    # у первой ветви чуть больше толщины — это «ствол», у остальных чуть меньше
    branches = [(ax, ay, ex, ey, 1.0) for ex, ey in var["ends"]]

    dist = [[99.0] * S for _ in range(S)]
    along = [[0.0] * S for _ in range(S)]
    cross = [[0.0] * S for _ in range(S)]

    longest = max(math.hypot(ex - ax, ey - ay) for ex, ey in var["ends"])

    for y in range(S):
        py = y + 0.5
        for x in range(S):
            px = x + 0.5
            best = 99.0
            best_t = 0.0
            best_len = longest
            for (x1, y1, ex, ey, k) in branches:
                dx, dy = ex - x1, ey - y1
                length = math.hypot(dx, dy)
                t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (length * length)))
                d = math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
                # ствол толще: эквивалентное расстояние меньше
                if d - (width / 2.0) * (k - 1) < best - 0.0001:
                    best = d / k
                    best_t = t
                    best_len = length
            dist[y][x] = best
            # 0 у источника, 1 на кончике
            along[y][x] = min(1.0, (best_t * best_len) / longest)
            cross[y][x] = 0.0
    return dist, along


def shade(dist, along, tier: int, variant: int):
    """Цвет по ДЛИНЕ жилы (светло у источника, темно к кончикам) + объём."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = img.load()
    half = TIER[tier]["width"] / 2.0
    for y in range(S):
        for x in range(S):
            d = dist[y][x] - half
            if d > 0.6:
                continue  # плоть, не жила
            # поперечная координата: 0 в центре, 1 у края
            c = min(1.0, max(0.0, (half - abs(d)) / max(half, 0.5)))
            edge = 1.0 - c
            # яркость вдоль: 6 у источника → 0 у кончика
            k = 6.0 * (1.0 - along[y][x])
            # край жилы на ступень темнее — даёт объём
            k -= 1.0 * edge
            # детерминированный шум: рвёт ровные переходы, добивает число цветов
            h = (x * 73856093) ^ (y * 19349663) ^ (tier * 83492791) ^ (variant * 2654435761)
            k += ((h >> 3) % 3) - 1
            if variant == 2:
                k += 0.6
            idx = int(round(k))
            idx = max(0, min(6, idx))
            px[x, y] = PALETTE[idx] + (255,)
    return img


def main():
    os.makedirs(os.path.join(OUT, "textures/block"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "models/block"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "blockstates"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "models/item"), exist_ok=True)

    report = []
    for tier in (1, 2, 3, 4):
        for variant in (0, 1, 2):
            dist, along = build(tier, variant)
            img = shade(dist, along, tier, variant)
            suffix = "" if variant == 0 else "_%d" % variant
            name = "flesh_veins_t%d%s" % (tier, suffix)
            img.save(os.path.join(OUT, "textures/block", name + ".png"), "PNG", optimize=True)

            # модель грани: элемент на поверхности (z 0.1..0.2) — виден базовый блок
            tex = "carnis:block/" + name
            model = {
                "render_type": "minecraft:cutout",
                "ambientocclusion": False,
                "textures": {"particle": tex, "vein": tex},
                "elements": [{
                    "from": [0, 0, 0.1], "to": [16, 16, 0.2],
                    "shade": False,
                    "faces": {
                        "north": {"texture": "#vein", "uv": [0, 0, 16, 16]},
                        "south": {"texture": "#vein", "uv": [0, 0, 16, 16]},
                    },
                }],
            }
            with open(os.path.join(OUT, "models/block", name + "_face.json"), "w",
                      encoding="utf-8", newline="\n") as f:
                json.dump(model, f, indent=2)
                f.write("\n")
            report.append(name)

    # Предметный спрайт — по одной текстуре на тир (вариация 0): в инвентаре
    # различать 12 почти одинаковых иконок незачем.
    for tier in (1, 2, 3, 4):
        tex = "carnis:block/flesh_veins_t%d" % tier
        item = {"parent": "minecraft:item/generated", "textures": {"layer0": tex}}
        with open(os.path.join(OUT, "models/item/flesh_veins_t%d.json" % tier), "w",
                  encoding="utf-8", newline="\n") as f:
            json.dump(item, f, indent=2)
            f.write("\n")

    # blockstate: 6 граней × 12 состояний (4 тира × 3 вариации) = 72 части.
    # Пишется здесь же, а не отдельным скриптом: blockstate ссылается на имена
    # моделей, которые генерируются выше, — держать это в одном месте значит
    # не дать им разойтись при следующей правке.
    faces = ["north", "east", "south", "west", "up", "down"]
    rot = {"north": None, "east": {"y": 90}, "south": {"y": 180},
           "west": {"y": 270}, "up": {"x": 270}, "down": {"x": 90}}
    multipart = []
    for tier in (1, 2, 3, 4):
        for variant in (0, 1, 2):
            suffix = "" if variant == 0 else "_%d" % variant
            model = "carnis:block/flesh_veins_t%d%s_face" % (tier, suffix)
            for face in faces:
                when = {face: "true", "tier": str(tier), "variant": str(variant)}
                apply = {"model": model, "uvlock": True}
                if rot[face]:
                    apply.update(rot[face])
                multipart.append({"when": when, "apply": apply})
    with open(os.path.join(OUT, "blockstates", "flesh_veins.json"), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump({"multipart": multipart}, f, indent=2)
        f.write("\n")
    print("готово:", len(report), "текстур,", len(multipart), "частей blockstate")


if __name__ == "__main__":
    main()
