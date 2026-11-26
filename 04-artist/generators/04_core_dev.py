#!/usr/bin/env python3
"""Dev v4: округлые мышечные волокна (тень по краю, свет по центру),
волновой дрейф ±2, жилы — ручные диагонали. flesh_block + t1–t4."""
import sys
sys.path.insert(0, '/home/user/carnis/tools')
from carnis_px import to_image, seam_sheet, seam_metric
from PIL import Image

S = 16
RAM = {
    '1': (60, 25, 22), '2': (74, 34, 32), '3': (90, 43, 40),
    '4': (103, 52, 47), '5': (116, 60, 55), '6': (138, 80, 80),
    'v': (120, 62, 60), 'V': (142, 86, 84), 'p': (158, 102, 98),
}

# волокна: левые границы пучков + дрейф по строкам (ручная волна ±2)
BOUNDS = [0, 3, 7, 11, 14]
DRIFT = [0, 1, 1, 2, 2, 1, 1, 0, -1, -1, -2, -2, -1, -1, 0, 0]
# световые мазки внутри пучков: (столбец пучка, y0, y1, тон)
LIT = {
    0: [(1, 2, 5, '4'), (2, 9, 12, '5')],
    1: [(1, 0, 3, '5'), (2, 7, 10, '4'), (1, 13, 15, '4')],
    2: [(2, 1, 4, '4'), (1, 6, 9, '5'), (2, 12, 14, '4')],
    3: [(1, 3, 6, '4'), (2, 10, 13, '5')],
    4: [(1, 0, 2, '4'), (0, 6, 9, '4'), (1, 13, 15, '5')],
}
# поперечные вдавления (тень поперёк пучка): (y, x)
CROSS = [(4, 2), (4, 5), (9, 9), (12, 12), (12, 15), (6, 13)]
PITS = [(7, 3), (13, 8), (2, 12)]          # глубокие ямки
WET = [(4, 5), (10, 13), (15, 8)]          # влажные блики


def base():
    """Строки символов: волокна."""
    g = [['3'] * S for _ in range(S)]
    for y in range(S):
        for xb in BOUNDS:
            g[y][(xb + DRIFT[y]) % S] = '2'          # стык — тень
            g[y][(xb + DRIFT[y] + 1) % S] = '4'      # скос к свету
    for bi, specs in LIT.items():
        x0 = BOUNDS[bi]
        for col, y0, y1, tone in specs:
            for y in range(y0, y1 + 1):
                x = (x0 + DRIFT[y] + col) % S
                if g[y][x] == '3':
                    g[y][x] = tone
    for y, x in CROSS:
        if g[y][x] in ('3', '4'):
            g[y][x] = '2'
    for x, y in PITS:
        g[y][x] = '1'
    return g


def vein(g, ctrl, tone='v'):
    for (x0, y0), (x1, y1) in zip(ctrl, ctrl[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(steps + 1):
            x = int(round(x0 + (x1 - x0) * i / steps)) % S
            y = int(round(y0 + (y1 - y0) * i / steps)) % S
            g[y][x] = tone
    return g


def finish(g, name):
    rgb = [[RAM[c] for c in row] for row in g]
    to_image(rgb).resize((96, 96), Image.NEAREST).save(f"/home/user/carnis/previews/v4_{name}.png")
    seam_sheet(rgb).resize((288, 288), Image.NEAREST).save(f"/home/user/carnis/previews/v4seam_{name}.png")
    print(name, seam_metric(rgb))
    return rgb


def flesh_block():
    g = base()
    vein(g, [(0, 2), (2, 3), (3, 4), (5, 5), (6, 6), (8, 7), (9, 8),
             (11, 9), (12, 10), (14, 11), (15, 12)])
    vein(g, [(9, 8), (10, 11), (11, 12), (11, 15)])
    g[5][5] = 'V'; g[9][11] = 'V'
    for x, y in WET:
        if g[y][x] in ('4', '5'):
            g[y][x] = '6'
    return g


def t1():
    g = base()
    vein(g, [(0, 6), (2, 6), (4, 7), (6, 7), (8, 8), (10, 8), (12, 9), (15, 9)])
    vein(g, [(6, 7), (6, 10), (7, 12), (7, 14)])
    g[7][4] = 'V'
    return g


def t2():
    g = base()
    vein(g, [(0, 5), (2, 6), (4, 6), (6, 7), (8, 7), (10, 8), (12, 8), (15, 9)])
    # параллельная ветвь
    vein(g, [(0, 11), (2, 10), (4, 10), (6, 9), (7, 9)])
    vein(g, [(6, 7), (6, 3), (7, 1), (7, 0)])
    vein(g, [(10, 8), (10, 12), (11, 14), (11, 15)])
    vein(g, [(7, 9), (8, 12), (8, 14)])
    for x, y in [(2, 6), (8, 7), (12, 8)]:
        g[y][x] = 'V'
    g[6][2] = 'p'; g[10][4] = '6'
    return g


def t3():
    g = base()
    vein(g, [(0, 3), (2, 4), (4, 4), (6, 5), (8, 6), (10, 6), (12, 7), (15, 8)])
    vein(g, [(0, 13), (2, 12), (4, 12), (6, 11), (8, 10), (10, 10), (12, 9), (15, 8)])
    vein(g, [(4, 4), (4, 8), (5, 10), (6, 11)])
    vein(g, [(8, 6), (8, 2), (9, 0)])
    vein(g, [(10, 10), (11, 13), (12, 15)])
    for x, y in [(4, 8), (8, 6), (10, 10)]:
        g[y][x] = 'V'; g[(y + 1) % S][x] = 'V'
    g[8][4] = 'p'; g[6][8] = 'p'; g[10][10] = 'p'
    return g


def t4():
    g = [['v'] * S for _ in range(S)]
    for y in range(S):
        for xb in BOUNDS:
            g[y][(xb + DRIFT[y]) % S] = '3'
    for bi, specs in LIT.items():
        x0 = BOUNDS[bi]
        for col, y0, y1, tone in specs:
            for y in range(y0, y1 + 1):
                x = (x0 + DRIFT[y] + col) % S
                if g[y][x] == 'v':
                    g[y][x] = 'V' if tone in ('4', '5') else 'p'
    for x, y in [(4, 5), (10, 13), (15, 8)]:
        g[y][x] = '6'
    for x, y in [(7, 3), (13, 8)]:
        g[y][x] = '1'
    return g


if __name__ == "__main__":
    names = ['flesh_block', 't1', 't2', 't3', 't4']
    sheet = Image.new('RGBA', (96 * 5, 96))
    out = {}
    for i, n in enumerate(names):
        out[n] = finish(globals()[n](), n)
        sheet.paste(to_image(out[n]).resize((96, 96), Image.NEAREST), (i * 96, 0))
    sheet.save("/home/user/carnis/previews/v4_all.png")
