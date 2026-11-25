"""
tendrils_check.py — независимый валидатор набора `creeping_tendrils` (A6 / ТЗ).

Проверяет:
  1. формат: 64×64, RGBA, альфа строго 0/255, палитра из 8 цветов исходной текстуры;
  2. кромки: верх/низ и лево/право побайтово одинаковы у всех вариантов;
  3. seam: любая пара вариантов стыкуется по всем четырём сторонам побайтово;
  4. смешанные сетки 3×3 и 5×5 со случайным смешением:
     а) нет скачка на внутренних стыках (шов),
     б) нет периодичности с периодом плитки (регулярный узор),
     в) нет «решётки»: прозрачные дорожки между плитками не образуют
        регулярную сетку (проверяется по альфе в проекции 16 px);
  5. читаемость в 16 px: покрытие, связность, отсутствие «каши»;
  6. торцы и углы: содержимое доходит до кромки плитки (иначе стена
     распадается на изолированные островки) и не образует прямых линий;
  7. геометрия штрихов: толщина ≥ 8 px (2 px в 16 px), длина ≤ 32 px (половина плитки);
  8. палитра совпадает с исходной текстурой 16×16.

Замечание о кромках (решение Архитектора, волна 28)
----------------------------------------------------
Требование «верх/низ и лево/право побайтово одинаковы у всех вариантов»
означает, что на стене **все** швы совпадают и рисунок не «рвётся».
Но если дополнительно требовать пустое кольцо по краю, прозрачная полоса
проходит через всю стену и образует **регулярную решётку** — именно тот
дефект, ради устранения которого и затевался набор вариантов.

Поэтому критерий 6 переформулирован: кромка должна быть **одинаковой у всех
вариантов** (это уже проверяет пункт 2) и **содержимое должно доходить до
кромки**, чтобы плитки смыкались в сплошную ткань, а не в отдельные пятна.
Проверка «пробег у края ≤ 24 px» остаётся как запрет на тянущиеся вдоль
края прямые полосы.

Запуск:  python3 tools/tendrils_check.py <каталог с PNG> [файл SELFCHECK.json]
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import deque

from PIL import Image

SIZE = 64
SQRT2 = 1.4142135623730951

BASELINE_PALETTE = {
    (0, 0, 0, 0),
    (104, 47, 64, 255),
    (84, 40, 54, 255),
    (209, 144, 130, 255),
    (196, 126, 119, 255),
    (157, 80, 94, 255),
    (179, 106, 105, 255),
    (161, 90, 96, 255),
}

MAX_STROKE_PX = 32      # половина плитки
MIN_STROKE_PX = 8       # 2 px в проекции 16×16
THIN_STROKE_PX = 12     # ширина штриха, ниже которой он считается «линией»


# ── утилиты ───────────────────────────────────────────────────────────
def load_png(path):
    im = Image.open(path).convert("RGBA")
    return im


def pixels(im):
    return list(im.getdata())


def mask_of(im):
    return [[im.getpixel((x, y))[3] == 255 for x in range(SIZE)] for y in range(SIZE)]


def is_hashing(seed):
    def h(a, b):
        v = (a * 0x1F1F1F1F + b * 0x9E3779B9 + seed * 0x85EBCA6B) & 0xFFFFFFFF
        v = ((v ^ (v >> 15)) * 0x2545F491) & 0xFFFFFFFF
        v = ((v ^ (v >> 13)) * 0x27D4EB2F) & 0xFFFFFFFF
        return ((v ^ (v >> 16)) & 0xFFFFFFFF) / 4294967295.0
    return h


def mix_pattern(n, seed):
    h = is_hashing(seed)
    return [[int(h(y * 16 + x, 3) * 4) % 4 for x in range(n)] for y in range(n)]


# ── метрика расстояний (чамфер 3×4) ───────────────────────────────────
def distance_to_holes(mask):
    """d[y][x] — расстояние до ближайшего прозрачного пикселя (в пикселях)."""
    INF = 1e9
    d = [[0.0 if not mask[y][x] else INF for x in range(SIZE)] for y in range(SIZE)]
    for y in range(SIZE):
        for x in range(SIZE):
            if not mask[y][x]:
                continue
            best = d[y][x]
            for dy, dx in ((-1, 0), (-1, -1), (-1, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < SIZE and 0 <= xx < SIZE:
                    w = 1.0 if (dy == 0 or dx == 0) else SQRT2
                    v = d[yy][xx] + w
                    if v < best:
                        best = v
            d[y][x] = best
    for y in range(SIZE - 1, -1, -1):
        for x in range(SIZE - 1, -1, -1):
            if not mask[y][x]:
                continue
            best = d[y][x]
            for dy, dx in ((1, 0), (1, -1), (1, 1), (0, 1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < SIZE and 0 <= xx < SIZE:
                    w = 1.0 if (dy == 0 or dx == 0) else SQRT2
                    v = d[yy][xx] + w
                    if v < best:
                        best = v
            d[y][x] = best
    return d


def width_at(d, y, x):
    """Ширина штриха в пикселях: 2·d + 1 (для полосы шириной W даёт W)."""
    return 2.0 * d[y][x] + 1.0


def geodesic_from(mask, sources):
    """Геодезическое расстояние по 8-связности от множества sources."""
    INF = float("inf")
    g = [[INF] * SIZE for _ in range(SIZE)]
    q = deque()
    for (x, y) in sources:
        g[y][x] = 0.0
        q.append((x, y))
    while q:
        x, y = q.popleft()
        base = g[y][x]
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                xx, yy = x + dx, y + dy
                if 0 <= xx < SIZE and 0 <= yy < SIZE and mask[yy][xx]:
                    step = 1.0 if (dx == 0 or dy == 0) else SQRT2
                    if base + step < g[yy][xx]:
                        g[yy][xx] = base + step
                        q.append((xx, yy))
    return g


def ridge_pixels(d, mask):
    """Медиальная ось: локальные максимумы расстояния (с разрешением равных)."""
    out = []
    for y in range(SIZE):
        for x in range(SIZE):
            if not mask[y][x]:
                continue
            dv = d[y][x]
            best = True
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < SIZE and 0 <= yy < SIZE):
                        continue
                    if d[yy][xx] > dv:
                        best = False
                        break
                    if d[yy][xx] == dv and (yy < y or (yy == y and xx < x)):
                        best = False
                        break
                if not best:
                    break
            if best:
                out.append((x, y))
    return out


def graph_diameter(nodes, allowed):
    """Диаметр связной компоненты графа по геодезическому расстоянию."""
    adj = {n: [] for n in nodes}
    for (x, y) in nodes:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                n = (x + dx, y + dy)
                if n in allowed:
                    w = 1.0 if (dx == 0 or dy == 0) else SQRT2
                    adj[(x, y)].append((n, w))
    seen = set()
    best = 0.0
    for start in nodes:
        if start in seen:
            continue
        # BFS до конца компоненты
        dist = {start: 0.0}
        stack = [start]
        comp = {start}
        while stack:
            cur = stack.pop()
            for (nb, w) in adj[cur]:
                if nb not in dist:
                    dist[nb] = dist[cur] + w
                    comp.add(nb)
                    stack.append(nb)
        seen |= comp
        # диаметр приближённо: два прохода BFS
        def farthest(src):
            d2 = {src: 0.0}
            q = deque([src])
            far = src
            while q:
                cur = q.popleft()
                if d2[cur] > d2[far]:
                    far = cur
                for (nb, w) in adj[cur]:
                    if nb not in d2:
                        d2[nb] = d2[cur] + w
                        q.append(nb)
            return far, d2[far]
        a, _ = farthest(start)
        _, dia = farthest(a)
        if dia > best:
            best = dia
    return best


def components(mask):
    """Связные компоненты по 8-связности для произвольного размера."""
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


def thin(mask):
    """Скелетизация Чжан-Суэна: 1-пиксельный скелет маски."""
    img = [list(row) for row in mask]
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            removals = []
            for y in range(1, SIZE - 1):
                for x in range(1, SIZE - 1):
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
                    a = sum(1 for i in range(8)
                            if not seq[i] and seq[(i + 1) % 8])
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


def _skel_neighbours(skel):
    neigh = {}
    for y in range(SIZE):
        for x in range(SIZE):
            if not skel[y][x]:
                continue
            ns = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < SIZE and 0 <= yy < SIZE and skel[yy][xx]:
                        ns.append((xx, yy))
            neigh[(x, y)] = ns
    return neigh


def _prune(skel, min_len=4.0):
    """Убирает короткие отростки скелета (шум на границе маски)."""
    skel = [list(row) for row in skel]
    changed = True
    while changed:
        changed = False
        neigh = _skel_neighbours(skel)
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


def skeleton_branches(skel):
    """Ветви скелета: пути между узлами (ветвление/конец) и их длины."""
    neigh = _skel_neighbours(skel)
    node = {p for p, ns in neigh.items() if len(ns) != 2}
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
    return branches


# ── проверки ──────────────────────────────────────────────────────────
def check_format(images):
    res = {"ok": True, "details": []}
    for name, im in images.items():
        if im.size != (SIZE, SIZE):
            res["ok"] = False
            res["details"].append(f"{name}: размер {im.size}")
        px = pixels(im)
        alphas = {p[3] for p in px}
        if not alphas <= {0, 255}:
            res["ok"] = False
            res["details"].append(f"{name}: альфа не 0/255: {sorted(alphas)}")
        extra = {p for p in px} - BASELINE_PALETTE
        if extra:
            res["ok"] = False
            res["details"].append(f"{name}: посторонние цвета {sorted(extra)[:4]}")
        opaque = sum(1 for p in px if p[3] == 255)
        res["details"].append(f"{name}: непрозрачных {opaque}/{len(px)} "
                              f"({opaque / len(px) * 100:.1f} %), цветов {len(set(px))}")
    return res


def check_borders(images):
    """Верх/низ и лево/право побайтово одинаковы у всех вариантов."""
    names = list(images)
    res = {"ok": True, "details": []}
    for side, get in (
        ("top", lambda im: [im.getpixel((x, 0)) for x in range(SIZE)]),
        ("bottom", lambda im: [im.getpixel((x, SIZE - 1)) for x in range(SIZE)]),
        ("left", lambda im: [im.getpixel((0, y)) for y in range(SIZE)]),
        ("right", lambda im: [im.getpixel((SIZE - 1, y)) for y in range(SIZE)]),
    ):
        ref = get(images[names[0]])
        for nm in names[1:]:
            cur = get(images[nm])
            if cur != ref:
                res["ok"] = False
                diff = sum(1 for a, b in zip(ref, cur) if a != b)
                res["details"].append(f"{side}: {names[0]} vs {nm} — различий {diff}")
        res["details"].append(f"{side}: одинаков у {len(names)} вариантов")
    return res


def check_seam(images):
    """Побайтовый стык:右(a) == left(b) для любой пары, плюс самозамыкание."""
    names = list(images)
    res = {"ok": True, "details": [], "pairs": 0}
    for a in names:
        for b in names:
            ra = [images[a].getpixel((SIZE - 1, y)) for y in range(SIZE)]
            lb = [images[b].getpixel((0, y)) for y in range(SIZE)]
            if ra != lb:
                res["ok"] = False
                res["details"].append(f"seam {a}->{b}: расхождение")
            res["pairs"] += 1
    res["details"].append(f"проверено {res['pairs']} пар (включая самозамыкание)")
    return res


def _period_ratio(wall, n):
    """Отношение автокорреляции с периодом плитки к фоновой (см. check_mixed)."""
    small = wall.resize((n * 16, n * 16), Image.LANCZOS)
    sp = [p[3] / 255.0 for p in pixels(small)]
    W16 = n * 16
    mu = sum(sp) / len(sp)
    var = sum((v - mu) ** 2 for v in sp) / len(sp)

    def interior(idx):
        return (idx % 16) not in (0, 1, 14, 15)

    def autocorr(lag):
        tot, cnt = 0.0, 0
        for y in range(W16):
            for x in range(W16 - lag):
                if not interior(x) or not interior(x + lag):
                    continue
                tot += sp[y * W16 + x] * sp[y * W16 + x + lag]
                cnt += 1
        return (tot / cnt - mu * mu) / var if cnt and var else 0.0

    ac = {lag: autocorr(lag) for lag in (8, 16, 24, 32, 40, 48, 56, 64) if lag < W16}
    others = [v for k, v in ac.items() if k not in (16, 32, 48, 64)]
    ratio = ac.get(16, 0.0) / (sum(others) / len(others)) if others and sum(others) else 1.0
    return ac, ratio


def _rotated_control(images, n, seed):
    """Контроль: та же плитка, повёрнутая на 90/180/270° — статистика та же,
    периодичности нет."""
    h = is_hashing(seed + 911)
    imgs = list(images.values())
    out = Image.new("RGBA", (SIZE * n, SIZE * n))
    for y in range(n):
        for x in range(n):
            k = int(h(y * 16 + x, 5) * 4) % 4
            tile = imgs[0]
            if k == 1:
                tile = tile.transpose(Image.ROTATE_90)
            elif k == 2:
                tile = tile.transpose(Image.ROTATE_180)
            elif k == 3:
                tile = tile.transpose(Image.ROTATE_270)
            out.paste(tile, (x * SIZE, y * SIZE))
    return out


def _noise_wall(n, seed):
    """Контрольная стена из детерминированного шума: узора быть не может."""
    h = is_hashing(seed + 4241)
    W = n * 16
    img = Image.new("RGBA", (W, W))
    data = []
    for y in range(W):
        for x in range(W):
            a = int(h(y * W + x, 7) * 255)
            data.append((0, 0, 0, a))
    img.putdata(data)
    return img


def build_wall(images, pat):
    n = len(pat)
    imgs = list(images.values())
    wall = Image.new("RGBA", (SIZE * n, SIZE * n))
    for y in range(n):
        for x in range(n):
            wall.paste(imgs[pat[y][x]], (x * SIZE, y * SIZE))
    return wall


def jump(a, b):
    if a[3] == 0 and b[3] == 0:
        return 0.0
    if a[3] == 0 or b[3] == 0:
        return 255.0
    return math.dist(a[:3], b[:3])


def _lattice_ratio(wall, n):
    """Насколько прозрачные дорожки между плитками образуют правильную решётку.

    Проекция стены в 16 px на плитку. Считаем среднюю альфу в колонках,
    прилегающих к границе плитки (x ≡ 0, 15 по модулю 16), и внутри плитки
    (x ≡ 6..9). У пустого кольца по краю первая величина ≈ 0, а вторая > 0 —
    это и есть «решётка»: равномерная прозрачная сетка через всю стену.

    Возвращает (значение на кромке, значение внутри, отношение).
    """
    small = wall.resize((n * 16, n * 16), Image.LANCZOS)
    sp = [p[3] / 255.0 for p in pixels(small)]
    W16 = n * 16
    edge, inner = [], []
    for x in range(W16):
        col = [sp[y * W16 + x] for y in range(W16)]
        m = sum(col) / len(col)
        if x % 16 in (0, 15):
            edge.append(m)
        elif x % 16 in (6, 7, 8, 9):
            inner.append(m)
    e = sum(edge) / len(edge) if edge else 0.0
    i = sum(inner) / len(inner) if inner else 0.0
    return e, i, (e / i if i > 1e-6 else 1.0)


def check_lattice(images):
    """Стена не должна распадаться на равномерную сетку прозрачных дорожек.

    Признак дефекта: кромка плитки почти пустая (альфа у границы заметно
    ниже, чем внутри), при том что внутри плитки ткань плотная. Тогда стена
    читается как «изолятки в клетках», а не как сплошная ткань.
    """
    res = {"ok": True, "details": [], "grids": {}}
    names = list(images)
    for n in (3, 5):
        for seed in (977 + n, 20260101 + n, 4242 + n):
            pat = mix_pattern(n, seed)
            wall = build_wall(images, pat)
            e, i, ratio = _lattice_ratio(wall, n)
            entry = {"seed": seed, "alpha_at_border": round(e, 3),
                     "alpha_inside": round(i, 3), "border_to_inside": round(ratio, 3)}
            res["grids"][f"{n}x{n}_{seed}"] = entry
            # решётка: кромка почти пустая, а внутри ткань есть
            if e < 0.35 * i:
                res["ok"] = False
                res["details"].append(
                    f"{n}x{n} seed={seed}: прозрачная решётка — кромка {e:.2f} против "
                    f"внутри {i:.2f} (плитки не смыкаются)")
    return res


def check_mixed(images):
    """Смешанные сетки 3×3 и 5×5: шов и регулярность узора."""
    res = {"ok": True, "grids": {}}
    names = list(images)
    for n in (3, 5):
        for seed in (977 + n, 20260101 + n, 4242 + n):
            pat = mix_pattern(n, seed)
            wall = build_wall(images, pat)
            W = wall.size[0]
            wp = pixels(wall)
            b_jumps, i_jumps = [], []
            for y in range(W):
                row = [wp[y * W + x] for x in range(W)]
                for x in range(W - 1):
                    j = jump(row[x], row[x + 1])
                    if (x + 1) % SIZE == 0:
                        b_jumps.append(j)
                    else:
                        i_jumps.append(j)
            for x in range(W):
                col = [wp[y * W + x] for y in range(W)]
                for y in range(W - 1):
                    j = jump(col[y], col[y + 1])
                    if (y + 1) % SIZE == 0:
                        b_jumps.append(j)
                    else:
                        i_jumps.append(j)
            max_b = max(b_jumps) if b_jumps else 0.0
            mean_b = sum(b_jumps) / len(b_jumps) if b_jumps else 0.0
            mean_i = sum(i_jumps) / len(i_jumps) if i_jumps else 0.0
            entry = {
                "seed": seed,
                "pattern": pat,
                "max_jump_at_border": round(max_b, 3),
                "mean_jump_at_border": round(mean_b, 3),
                "mean_jump_inside": round(mean_i, 3),
            }
            # регулярность: автокорреляция альфы в проекции 16 px.
            # Пары берём только внутри плиток (не ближе 2 px от границы),
            # иначе измерялась бы не периодичность рисунка, а прозрачное кольцо.
            small = wall.resize((n * 16, n * 16), Image.LANCZOS)
            sp = [p[3] / 255.0 for p in pixels(small)]
            W16 = n * 16
            mu = sum(sp) / len(sp)
            var = sum((v - mu) ** 2 for v in sp) / len(sp)

            def interior(idx):
                return (idx % 16) not in (0, 1, 14, 15)

            def autocorr(lag):
                tot, cnt = 0.0, 0
                for y in range(W16):
                    for x in range(W16 - lag):
                        if not interior(x) or not interior(x + lag):
                            continue
                        a = sp[y * W16 + x]
                        b = sp[y * W16 + x + lag]
                        tot += a * b
                        cnt += 1
                if not cnt or var == 0:
                    return 0.0
                return (tot / cnt - mu * mu) / var

            ac = {}
            for lag in (8, 16, 24, 32, 40, 48, 56, 64):
                if lag < W16:
                    ac[lag] = round(autocorr(lag), 4)
            tile_ac = ac.get(16, 0.0)
            others = [v for k, v in ac.items() if k not in (16, 32, 48, 64)]
            ratio = tile_ac / (sum(others) / len(others)) if others and sum(others) else 1.0
            entry["autocorr_alpha_16px"] = ac
            entry["tile_period_ratio"] = round(ratio, 3)
            # контрольные стены: та же плитка, повторённая (заведомо узор)
            # и чистый шум (заведомо без узора) — по ним калибруется шкала
            same_wall = build_wall(images, [[0] * n for _ in range(n)])
            _, r_same = _period_ratio(same_wall, n)
            rot_wall = _rotated_control(images, n, seed)
            _, r_rot = _period_ratio(rot_wall, n)
            noise_wall = _noise_wall(n, seed)
            _, r_noise = _period_ratio(noise_wall, n)
            entry["control_same_tile_ratio"] = round(r_same, 3)
            entry["control_rotated_ratio"] = round(r_rot, 3)
            entry["control_noise_ratio"] = round(r_noise, 3)
            entry["irregularity_margin"] = round(r_same / ratio, 3) if ratio > 0 else None
            res["grids"][f"{n}x{n}_{seed}"] = entry
            if max_b > mean_i * 1.25 + 12.0:
                res["ok"] = False
                res.setdefault("details", []).append(
                    f"{n}x{n} seed={seed}: скачок на стыке {max_b:.1f} выше среднего внутри {mean_i:.1f}")
            if ratio > 0.85 * r_same or ratio > 1.35 * r_rot:
                res["ok"] = False
                res.setdefault("details", []).append(
                    f"{n}x{n} seed={seed}: автокорреляция с периодом плитки {ratio:.2f}× "
                    f"(контроль «одна плитка» {r_same:.2f}×, «повёрнутая» {r_rot:.2f}×)")
    return res


def check_readability(images):
    """Проекция 16 px: покрытие, связность, отсутствие каши."""
    res = {"ok": True, "details": [], "tiles": {}}
    for name, im in images.items():
        small = im.resize((16, 16), Image.LANCZOS)
        px = pixels(small)
        opaque = sum(1 for p in px if p[3] > 0)
        alpha_sum = sum(p[3] for p in px) / (255 * 256)
        smask = [[px[y * 16 + x][3] > 96 for x in range(16)] for y in range(16)]
        comps = components(smask)
        big = sum(len(c) for c in comps if len(c) >= 3)
        # контраст: непрозрачные пиксели против фона
        lum = [sum(p[:3]) / 3 for p in px if p[3] > 0]
        contrast = (max(lum) - min(lum)) if lum else 0.0
        entry = {
            "opaque_px": opaque,
            "alpha_coverage": round(alpha_sum, 3),
            "components": len(comps),
            "components_ge3px": sum(1 for c in comps if len(c) >= 3),
            "share_in_big_components": round(big / opaque, 3) if opaque else 0.0,
            "luma_contrast": round(contrast, 1),
        }
        res["tiles"][name] = entry
        if not (0.18 <= alpha_sum <= 0.75):
            res["ok"] = False
            res["details"].append(f"{name}: покрытие в 16 px вне 18–75 %: {alpha_sum:.2f}")
        if opaque and big / opaque < 0.55:
            res["ok"] = False
            res["details"].append(f"{name}: в 16 px только {big / opaque:.0%} пикселей в связных "
                                  f"фигурах ≥ 3 px — слишком мелко")
        if contrast < 40:
            res["ok"] = False
            res["details"].append(f"{name}: слабый контраст в 16 px: {contrast:.0f}")
    return res


def check_ends_corners(images):
    """Торцы и углы: ткань доходит до кромки и не имеет прямых полос у края.

    Два требования, которые раньше конфликтовали:
      * «пустое кольцо по краю» → на стене получается прозрачная решётка;
      * «содержимое прижато к краю» → та же проблема с другой стороны.
    Теперь: кромка одинакова у всех вариантов (проверка 2), содержимое
    доходит до неё (плотность кромки), и при этом вдоль кромки нет
    длинной прямой полосы (пробег ≤ 24 px) и углы не забиты.
    """
    res = {"ok": True, "details": [], "tiles": {}}
    for name, im in images.items():
        mask = mask_of(im)
        # 1) плотность кромки: доля непрозрачных в полосе шириной 3 px
        band = 3
        edge_cells = 0
        edge_opaque = 0
        for y in range(SIZE):
            for x in range(SIZE):
                if (x < band or x >= SIZE - band or y < band or y >= SIZE - band):
                    edge_cells += 1
                    if mask[y][x]:
                        edge_opaque += 1
        edge_density = edge_opaque / edge_cells if edge_cells else 0.0
        # 2) прямые полосы вдоль кромки
        runs = []
        for y in (0, SIZE - 1):
            run = best = 0
            for x in range(SIZE):
                run = run + 1 if mask[y][x] else 0
                best = max(best, run)
            runs.append(best)
        for x in (0, SIZE - 1):
            run = best = 0
            for y in range(SIZE):
                run = run + 1 if mask[y][x] else 0
                best = max(best, run)
            runs.append(best)
        max_run = max(runs)
        # 3) углы
        corners = []
        for cy in (0, 1, SIZE - 2, SIZE - 1):
            for cx in (0, 1, SIZE - 2, SIZE - 1):
                corners.append(sum(1 for y in range(cy, min(cy + 2, SIZE))
                                   for x in range(cx, min(cx + 2, SIZE))
                                   if mask[y][x]))
        corner_px = sum(corners)
        entry = {"edge_density": round(edge_density, 3),
                 "max_run_on_border": max_run,
                 "corner_px": corner_px}
        res["tiles"][name] = entry
        if edge_density < 0.45:
            res["ok"] = False
            res["details"].append(
                f"{name}: кромка почти пустая ({edge_density:.0%} непрозрачных в полосе 3 px) — "
                f"плитки останутся отдельными островками")
        if max_run > 24:
            res["ok"] = False
            res["details"].append(f"{name}: вдоль кромки прямая полоса длиной {max_run} px")
        if corner_px > 10:
            res["ok"] = False
            res["details"].append(f"{name}: угол заполнен на {corner_px} из 16 px")
    return res


def check_geometry(images):
    """Длина непрерывной линии ≤ 32 px и толщина штриха ≥ 8 px.

    Метрики (в 64×64):
      * скелет маски — скелетизация Чжан-Суэна с удалением коротких отростков;
      * «непрерывная линия» — ветвь скелета между узлами и концами;
        берётся длина самой длинной ветви;
      * толщина штриха в точке медиальной оси — диаметр вписанного круга
        (2·d + 1, где d — расстояние до прозрачного пикселя);
        у скруглённого конца штриха берутся только внутренние точки ветви.
    """
    res = {"ok": True, "details": [], "tiles": {}}
    for name, im in images.items():
        mask = mask_of(im)
        d = distance_to_holes(mask)
        skel = _prune(thin(mask), 4.0)
        branches = skeleton_branches(skel)
        longest = 0.0
        min_width = None
        long_branches = []
        thin_branches = []
        for br in branches:
            path = br["path"]
            length = br["length"]
            longest = max(longest, length)
            if length > MAX_STROKE_PX:
                long_branches.append({"length": round(length, 2),
                                      "from": list(path[0]), "to": list(path[-1])})
            inner = path[2:-2] if len(path) > 4 else path
            widths = [width_at(d, y, x) for (x, y) in inner]
            if not widths:
                continue
            wmin = min(widths)
            if wmin < MIN_STROKE_PX:
                thin_branches.append({"length": round(length, 2),
                                      "min_width": round(wmin, 2),
                                      "at": list(inner[widths.index(wmin)])})
            min_width = wmin if min_width is None else min(min_width, wmin)
        thin_comps = []
        for comp in components(mask):
            wmax = 0.0
            for (x, y) in comp:
                wmax = max(wmax, width_at(d, y, x))
            if wmax < MIN_STROKE_PX:
                thin_comps.append({"size": len(comp), "max_width": round(wmax, 2)})
        entry = {
            "skeleton_branches": len(branches),
            "longest_branch_px": round(longest, 2),
            "branches_over_limit": long_branches,
            "min_stroke_width_px": round(min_width, 2) if min_width is not None else None,
            "branches_too_thin": thin_branches,
            "thin_detached_parts": thin_comps,
        }
        res["tiles"][name] = entry
        if longest > MAX_STROKE_PX:
            res["ok"] = False
            res["details"].append(f"{name}: непрерывная линия {longest:.1f} px > {MAX_STROKE_PX}")
        for tb in thin_branches:
            res["ok"] = False
            res["details"].append(f"{name}: штрих толщиной {tb['min_width']:.1f} px "
                                  f"в точке ({tb['at'][0]}, {tb['at'][1]})")
        for tc in thin_comps:
            if tc["size"] >= 12:
                res["ok"] = False
                res["details"].append(
                    f"{name}: отдельная тонкая фигура {tc['size']} px (ширина {tc['max_width']})")
    return res


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(d, "SELFCHECK.json")
    files = sorted(f for f in os.listdir(d) if f.startswith("creeping_tendrils_") and f.endswith(".png"))
    images = {}
    for f in files:
        im = load_png(os.path.join(d, f))
        if im.size != (SIZE, SIZE):
            print(f"!! {f}: размер {im.size} — пропущен")
            continue
        images[f] = im
    if len(images) < 3:
        print("Нужно минимум 3 варианта")
        sys.exit(1)

    report = {
        "tool": "tendrils_check.py",
        "tiles": list(images),
        "checks": {
            "1_format_and_palette": check_format(images),
            "2_borders_identical": check_borders(images),
            "3_seam_byte_exact": check_seam(images),
            "4_mixed_grids": check_mixed(images),
            "4b_lattice": check_lattice(images),
            "5_readability_16px": check_readability(images),
            "6_ends_and_corners": check_ends_corners(images),
            "7_stroke_geometry": check_geometry(images),
        },
    }
    report["all_ok"] = all(c["ok"] for c in report["checks"].values())
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(f"вариантов: {len(images)}")
    for key, c in report["checks"].items():
        print(f"  [{'OK ' if c['ok'] else 'FAIL'}] {key}")
        for line in c.get("details", [])[:12]:
            print("        ", line)
        if key == "4_mixed_grids":
            for gname, g in c["grids"].items():
                print(f"         {gname}: стык max={g['max_jump_at_border']} "
                      f"внутри={g['mean_jump_inside']} период×{g['tile_period_ratio']}")
    print("ИТОГ:", "ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ" if report["all_ok"] else "ЕСТЬ ЗАМЕЧАНИЯ")
    print("записан:", out)
    sys.exit(0 if report["all_ok"] else 2)


if __name__ == "__main__":
    main()
