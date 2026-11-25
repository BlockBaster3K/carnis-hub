"""
tendrils_tune.py — подстройка раскладки вариантов под геометрические ограничения.

Ищет небольшие сдвиги узлов и повороты отростков, при которых:
  * нет узких перешейков (толщина штриха по медиальной оси ≥ 9 px);
  * нет непрерывной линии длиннее 30 px (лимит ТЗ — 32);
  * ничего не срезано краем плитки;
  * покрытие остаётся в диапазоне, близком к исходной текстуре (33–46 %).

Поиск детерминированный (свой хеш-шум), результат печатается как готовый
фрагмент спецификации VARIANTS для tendrils_gen.py.

Запуск:  python3 tools/tendrils_tune.py [сколько_проб_на_вариант]
"""

from __future__ import annotations

import copy
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tendrils_gen as gen  # noqa: E402
import tendrils_geom as geom  # noqa: E402


def render_mask(spec):
    scene = gen._build(spec, 0)
    scene.clipped = 0
    mask = [[False] * gen.SIZE for _ in range(gen.SIZE)]
    for y in range(gen.SIZE):
        for x in range(gen.SIZE):
            f = scene.field(x + 0.5, y + 0.5)
            if f <= 0:
                if x < gen.MARGIN or y < gen.MARGIN \
                        or x > gen.SIZE - 1 - gen.MARGIN or y > gen.SIZE - 1 - gen.MARGIN:
                    scene.clipped += 1
                    continue
                mask[y][x] = True
    return mask, scene.clipped


def metrics(mask):
    d = geom.distance_to_holes(mask, gen.SIZE)
    skel = geom.prune(geom.thin(mask, gen.SIZE), 4.0, gen.SIZE)
    branches, _ends = geom.skeleton_branches(skel, gen.SIZE)
    longest = 0.0
    min_width = None
    for br in branches:
        path = br["path"]
        longest = max(longest, br["length"])
        inner = path[2:-2] if len(path) > 4 else path
        for (x, y) in inner:
            w = geom.width_at(d, y, x)
            min_width = w if min_width is None else min(min_width, w)
    coverage = sum(1 for y in range(gen.SIZE) for x in range(gen.SIZE) if mask[y][x]) / (gen.SIZE ** 2)
    # равномерность заполнения: разброс покрытия по 3×3 подплиткам
    sub = []
    k = gen.SIZE // 3
    for gy in range(3):
        for gx in range(3):
            c = sum(1 for y in range(gy * k, (gy + 1) * k) for x in range(gx * k, (gx + 1) * k)
                    if mask[y][x]) / (k * k)
            sub.append(c)
    spread = max(sub) - min(sub)
    return {"longest": longest, "min_width": min_width or 0.0,
            "coverage": coverage, "spread": spread, "sub": sub}


def score(m, clipped):
    sc = 0.0
    if clipped:
        sc += 1000.0 + clipped
    if m["min_width"] < 9.0:
        sc += 300.0 * (9.0 - m["min_width"])
    if m["longest"] > 30.0:
        sc += 60.0 * (m["longest"] - 30.0)
    cov = m["coverage"]
    if cov < 0.38:
        sc += 300.0 * (0.38 - cov)
    elif cov > 0.46:
        sc += 300.0 * (cov - 0.46)
    if m.get("spread", 0.0) > 0.30:
        sc += 120.0 * (m["spread"] - 0.30)
    sc -= 12.0 * min(m["min_width"], 14.0)
    sc -= 0.5 * max(0.0, 30.0 - m["longest"])
    return sc


def hashf(i, j, seed):
    v = (i * 0x1F1F1F1F + j * 0x9E3779B9 + seed * 0x85EBCA6B) & 0xFFFFFFFF
    v = ((v ^ (v >> 15)) * 0x2545F491) & 0xFFFFFFFF
    v = ((v ^ (v >> 13)) * 0x27D4EB2F) & 0xFFFFFFFF
    return ((v ^ (v >> 16)) & 0xFFFFFFFF) / 4294967295.0


def perturb(spec, trial, seed):
    out = copy.deepcopy(spec)
    for ni, node in enumerate(out["nodes"]):
        cx, cy = node["c"]
        dx = round((hashf(trial, ni * 3 + 1, seed) - 0.5) * 5.0)
        dy = round((hashf(trial, ni * 3 + 2, seed) - 0.5) * 5.0)
        node["c"] = (cx + dx, cy + dy)
        tend = []
        for ti, (phi, length, r0) in enumerate(node["tendrils"]):
            dphi = (hashf(trial, ni * 11 + ti * 3 + 7, seed) - 0.5) * 14.0
            dlen = round((hashf(trial, ni * 11 + ti * 3 + 8, seed) - 0.5) * 5.0)
            tend.append((round(phi + dphi, 2), max(11.0, length + dlen), r0))
        node["tendrils"] = tend
    return out


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    result = {}
    for vi, spec in enumerate(gen.VARIANTS):
        best = copy.deepcopy(spec)
        mask, clipped = render_mask(best)
        best_m = metrics(mask)
        best_s = score(best_m, clipped)
        for t in range(trials):
            cand = perturb(spec, t, 7919 * (vi + 1))
            m2, c2 = render_mask(cand)
            s2 = score(metrics(m2), c2)
            if s2 < best_s - 1e-9:
                best_s, best, best_m, clipped = s2, cand, metrics(m2), c2
        result[spec["name"]] = {
            "spec": best,
            "score": round(best_s, 3),
            "longest": round(best_m["longest"], 2),
            "min_width": round(best_m["min_width"], 2),
            "coverage": round(best_m["coverage"], 4),
            "clipped": clipped,
        }
        print(f"{spec['name']}: score={best_s:.2f} длиннейшая={best_m['longest']:.1f} "
              f"мин. толщина={best_m['min_width']:.1f} покрытие={best_m['coverage'] * 100:.1f}% "
              f"срезано={clipped}")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tuned.json"),
              "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print("записан tuned.json")


if __name__ == "__main__":
    main()
