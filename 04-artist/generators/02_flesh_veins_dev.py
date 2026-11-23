#!/usr/bin/env python3
"""Dev: flesh_veins t1–t4, v2 — русла без прямых углов, с сужением."""
import sys
sys.path.insert(0, '/home/user/carnis/tools')
from carnis_px import to_image, seam_sheet, seam_metric, main_share

S = 16
PAL = {
    'd': (52, 24, 22), 's': (74, 34, 32), 'a': (90, 43, 40),
    'b': (102, 51, 47), 'c': (112, 56, 51),
    'v': (122, 64, 62), 'V': (146, 88, 86), 'p': (162, 106, 102),
    'w': (138, 80, 80),
}


def blank():
    return [[PAL['a']] * S for _ in range(S)]


def stamp(buf, st, ox, oy):
    for dx, dy, t in st:
        buf[(oy + dy) % S][(ox + dx) % S] = PAL[t]


def brush(buf, ctrl, tone='v', taper=None):
    """Русло по контрольным точкам. taper: список толщин на каждый
    сегмент (1 или 2). Шаг — по Брезенхему с плавным дрейфом."""
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(ctrl, ctrl[1:])):
        w = 1 if taper is None else taper[min(i, len(taper) - 1)]
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy))
        for st in range(steps + 1):
            x = round(x0 + dx * st / steps) % S
            y = round(y0 + dy * st / steps) % S
            buf[y][x] = PAL[tone]
            if w == 2:
                # утолщение — «вниз», но с заворотом
                buf[(y + 1) % S][x] = PAL[tone]


BLOB = [(-1, 0, 's'), (0, 0, 's'), (1, 0, 's'),
        (0, 1, 'd'), (1, 1, 'd'), (0, 2, 's')]
PORE = [(0, 0, 'd'), (0, 1, 's'), (-1, 0, 's')]
CLOUD = [(0, 0, 'b'), (1, 0, 'b'), (0, 1, 'b'), (1, 1, 'b'),
         (2, 1, 'b'), (1, 2, 'b'), (2, 2, 'b')]


def t1():
    """Одна тонкая жила, 1px, низкий контраст, дрейф 5 строк."""
    b = blank()
    for at in [(4, 12), (12, 4)]:
        stamp(b, CLOUD, *at)
    for at in [(2, 7), (14, 10)]:
        stamp(b, BLOB, *at)
    stamp(b, PORE, 9, 2)
    b[2][4] = PAL['c']          # одиночный гребень ткани
    b[3][4] = PAL['c']
    MAIN = [(0, 5), (2, 4), (4, 5), (6, 6), (8, 6), (10, 7), (12, 8),
            (14, 9), (15, 10)]
    BR = [(6, 6), (7, 8), (8, 9), (8, 11), (9, 12)]
    brush(b, MAIN, 'v')
    brush(b, BR, 'v')
    b[6][8] = PAL['V']          # один блик на жиле
    return b


def t2():
    """Ствол 2px на корне, 3 ветви, сужение к концам."""
    b = blank()
    for at in [(3, 11), (13, 2)]:
        stamp(b, CLOUD, *at)
    for at in [(1, 2), (15, 13)]:
        stamp(b, BLOB, *at)
    stamp(b, PORE, 10, 15)
    b[13][11] = PAL['c']; b[14][11] = PAL['c']
    TRUNK = [(0, 9), (2, 8), (4, 8), (6, 9), (8, 9), (10, 10), (12, 11),
             (14, 12), (15, 13)]
    brush(b, TRUNK, 'v', taper=[2, 2, 2, 1, 1, 1, 1, 1])
    B1 = [(4, 8), (5, 6), (5, 4), (6, 2), (6, 0)]
    B2 = [(10, 10), (11, 8), (12, 7), (13, 5)]
    B3 = [(8, 9), (8, 12), (9, 13), (9, 15)]
    brush(b, B1, 'v', taper=[1, 1, 1, 1])
    brush(b, B2, 'v', taper=[1, 1, 1])
    brush(b, B3, 'v', taper=[1, 1, 1])
    # влага и утолщение на стволе
    for (x, y) in [(2, 8), (10, 10)]:
        b[y][x] = PAL['V']
    b[8][2] = PAL['w']
    b[11][12] = PAL['V']
    return b


def t3():
    """Сеть: 2 ствола + 3 перемычки, аневризмы, > 50% площади под жилами."""
    b = blank()
    for at in [(6, 5), (12, 12)]:
        stamp(b, CLOUD, *at)
    stamp(b, BLOB, 2, 1); stamp(b, BLOB, 14, 8)
    stamp(b, PORE, 3, 14)
    T1 = [(0, 3), (2, 4), (4, 4), (6, 5), (8, 5), (10, 6), (12, 7),
          (14, 7), (16, 8)]
    T2 = [(0, 12), (2, 11), (4, 11), (6, 10), (8, 10), (10, 9),
          (12, 9), (14, 8), (16, 7)]
    C1 = [(4, 4), (5, 6), (5, 8), (5, 10), (6, 10)]
    C2 = [(10, 6), (10, 8), (11, 9), (12, 9)]
    C3 = [(8, 5), (9, 3), (10, 2), (10, 0)]
    for T in (T1, T2):
        brush(b, T, 'v', taper=[2, 2, 2, 2, 1, 1, 1, 1])
    for C in (C1, C2, C3):
        brush(b, C, 'v')
    # аневризмы (2×2) на трёх стыках
    for (x, y) in [(5, 8), (11, 9), (9, 3)]:
        b[y][x] = PAL['V']; b[(y + 1) % S][x] = PAL['V']
        b[y][(x + 1) % S] = PAL['V']; b[(y + 1) % S][(x + 1) % S] = PAL['V']
    b[8][5] = PAL['p']; b[9][11] = PAL['p']
    b[9][10] = PAL['w']; b[4][14] = PAL['w']
    return b


def t4():
    """Полное заражение: вся поверхность — ткань жил, масса ушла в швы."""
    b = [[PAL['v']] * S for _ in range(S)]
    SEAMS = [(0, 6), (1, 6), (2, 7), (5, 1), (6, 1), (6, 2), (9, 11),
             (10, 11), (10, 12), (13, 3), (14, 3), (3, 14), (4, 14),
             (14, 6), (15, 7), (7, 5), (8, 5)]
    for (x, y) in SEAMS:
        b[y][x] = PAL['a']
    for (x, y) in [(7, 8), (8, 8), (7, 9), (8, 9)]:
        b[y][x] = PAL['s']          # рана
    MASS = [(1, 3), (2, 3), (2, 4), (3, 4), (11, 1), (12, 1), (12, 2),
            (13, 2), (5, 9), (6, 9), (6, 10), (7, 10), (13, 13),
            (14, 13), (14, 14), (0, 12), (1, 12), (1, 13), (9, 4),
            (10, 4), (10, 5), (6, 13), (7, 13), (2, 9), (3, 9)]
    for (x, y) in MASS:
        b[y][x] = PAL['V']
    for (x, y) in [(2, 3), (12, 1), (6, 9), (14, 13), (10, 4), (1, 12),
                   (7, 13), (3, 9)]:
        b[y][x] = PAL['p']
    for (x, y) in [(8, 8), (15, 0), (0, 7), (3, 14), (13, 3), (5, 5)]:
        b[y][x] = PAL['w']
    return b


if __name__ == "__main__":
    for name, fn in [("t1", t1), ("t2", t2), ("t3", t3), ("t4", t4)]:
        buf = fn()
        to_image(buf).resize((320, 320), resample=0).save(
            f"/home/user/carnis/previews/veins_{name}_x20.png")
        seam_sheet(buf).resize((384, 384), resample=0).save(
            f"/home/user/carnis/previews/veins_{name}_seam.png")
        print(name, "seam:", seam_metric(buf), "mass%:", main_share(buf, PAL['a']))
