"""
tendrils_geom.py — общие пиксельные метрики для `creeping_tendrils`.

Используются и генератором (для контроля формы), и валидатором
(для независимой проверки готовых PNG). Модуль ничего не знает
о содержимом вариантов и работает только по маске прозрачности.
"""

from __future__ import annotations

import math
from collections import deque

SQRT2 = 1.4142135623730951


def distance_to_holes(mask, size=None):
    """d[y][x] — расстояние (в пикселях) до ближайшего прозрачного пикселя.

    Расстояние считается между центрами пикселей, поэтому у полосы шириной W
    центральный пиксель получает d = (W-1)/2, а width_at() даёт ровно W.
    """
    h = size or len(mask)
    w = size or len(mask[0])
    INF = 1e9
    d = [[0.0 if not mask[y][x] else INF for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if not mask[y][x]:
                continue
            best = d[y][x]
            for dy, dx in ((-1, 0), (-1, -1), (-1, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w:
                    v = d[yy][xx] + (1.0 if (dy == 0 or dx == 0) else SQRT2)
                    if v < best:
                        best = v
            d[y][x] = best
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            if not mask[y][x]:
                continue
            best = d[y][x]
            for dy, dx in ((1, 0), (1, -1), (1, 1), (0, 1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w:
                    v = d[yy][xx] + (1.0 if (dy == 0 or dx == 0) else SQRT2)
                    if v < best:
                        best = v
            d[y][x] = best
    return d


def width_at(d, y, x):
    """Ширина штриха в пикселях: 2·d + 1."""
    return 2.0 * d[y][x] + 1.0


def thin(mask, size=None):
    """Скелетизация Чжан-Суэна: 1-пиксельный скелет маски."""
    h = size or len(mask)
    w = size or len(mask[0])
    img = [list(row) for row in mask]
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            removals = []
            for y in range(1, h - 1):
                for x in range(1, w - 1):
                    if not img[y][x]:
                        continue
                    p2 = img[y - 1][x]; p3 = img[y - 1][x + 1]
                    p4 = img[y][x + 1]; p5 = img[y + 1][x + 1]
                    p6 = img[y + 1][x]; p7 = img[y + 1][x - 1]
                    p8 = img[y][x - 1]; p9 = img[y - 1][x - 1]
                    b = sum(1 for v in (p2, p3, p4, p5, p6, p7, p8, p9) if v)
                    if b < 2 or b > 6:
                        continue
                    seq = (p2, p3, p4, p5, p6, p7, p8, p9)
                    a = sum(1 for i in range(8) if not seq[i] and seq[(i + 1) % 8])
                    if a != 1:
                        continue
                    if step == 0:
                        if p2 and p4 and p6:
                            continue
                        if p4 and p6 and p8:
                            continue
                    else:
                        if p2 and p4 and p8:
                            continue
                        if p2 and p6 and p8:
                            continue
                    removals.append((x, y))
            if removals:
                changed = True
                for (x, y) in removals:
                    img[y][x] = False
    return img


def skel_neighbours(skel, size=None):
    h = size or len(skel)
    w = size or len(skel[0])
    neigh = {}
    for y in range(h):
        for x in range(w):
            if not skel[y][x]:
                continue
            ns = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and skel[yy][xx]:
                        ns.append((xx, yy))
            neigh[(x, y)] = ns
    return neigh


def prune(skel, min_len=4.0, size=None):
    """Убирает короткие отростки скелета (шум на границе маски)."""
    h = size or len(skel)
    w = size or len(skel[0])
    skel = [list(row) for row in skel]
    changed = True
    while changed:
        changed = False
        neigh = skel_neighbours(skel, h)
        ends = [p for p, ns in neigh.items() if len(ns) == 1]
        for end in ends:
            if not skel[end[1]][end[0]]:
                continue
            path = [end]
            prev, cur = None, end
            while True:
                nxt = [q for q in neigh.get(cur, []) if q != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
                if len(neigh.get(cur, [])) != 2:
                    break
            length = 0.0
            for i in range(len(path) - 1):
                dx = path[i + 1][0] - path[i][0]
                dy = path[i + 1][1] - path[i][1]
                length += 1.0 if (dx == 0 or dy == 0) else SQRT2
            if length < min_len and len(path) > 1:
                for (x, y) in path[:-1]:
                    skel[y][x] = False
                changed = True
    return skel


def skeleton_branches(skel, size=None):
    """Ветви скелета: пути между узлами (ветвление/конец) и их длины."""
    h = size or len(skel)
    w = size or len(skel[0])
    neigh = skel_neighbours(skel, h)
    node = {p for p, ns in neigh.items() if len(ns) != 2}
    ends = {p for p, ns in neigh.items() if len(ns) == 1}
    visited = set()
    branches = []
    for start in sorted(node):
        for nb in neigh[start]:
            path = [start, nb]
            prev, cur = start, nb
            while cur not in node:
                nxt = [q for q in neigh.get(cur, []) if q != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
            key = tuple(sorted(path))
            if key in visited:
                continue
            visited.add(key)
            length = 0.0
            for i in range(len(path) - 1):
                dx = path[i + 1][0] - path[i][0]
                dy = path[i + 1][1] - path[i][1]
                length += 1.0 if (dx == 0 or dy == 0) else SQRT2
            branches.append({"path": path, "length": length})
    return branches, ends


def components(mask):
    """Связные компоненты по 8-связности (произвольный размер)."""
    h = len(mask)
    w = len(mask[0])
    seen = [[False] * w for _ in range(h)]
    comps = []
    for y in range(h):
        for x in range(w):
            if not mask[y][x] or seen[y][x]:
                continue
            stack = [(x, y)]
            seen[y][x] = True
            cells = []
            while stack:
                cx, cy = stack.pop()
                cells.append((cx, cy))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h \
                                and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((nx, ny))
            comps.append(cells)
    return comps


def sliver_points(mask, min_width=8.0, size=None):
    """Узкие перешейки: точки скелета с шириной < min_width, которые не являются
    концом штриха (то есть не скруглённой оконечностью)."""
    h = size or len(mask)
    w = size or len(mask[0])
    d = distance_to_holes(mask, h)
    skel = prune(thin(mask, h), 4.0, h)
    branches, ends = skeleton_branches(skel, h)
    out = []
    for y in range(h):
        for x in range(w):
            if not skel[y][x]:
                continue
            if width_at(d, y, x) >= min_width:
                continue
            near_end = any(abs(ex - x) <= 3 and abs(ey - y) <= 3 for (ex, ey) in ends)
            if near_end:
                continue
            out.append((x, y, round(width_at(d, y, x), 2)))
    return out, d
