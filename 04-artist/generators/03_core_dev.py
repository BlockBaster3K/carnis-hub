#!/usr/bin/env python3
"""Dev v3: вертикальные волнистые волокна как ядро; flesh_block + veins t1-t4."""
import sys
sys.path.insert(0, '/home/user/carnis/tools')
from carnis_px import to_image, seam_sheet, seam_metric, main_share
from PIL import Image

S = 16
# рамп плоти (тени коричневые, света розовые — по гайду)
RAM = {
    '1': (62, 26, 23),    # провал
    '2': (74, 34, 32),    # тень
    '3': (90, 43, 40),    # база
    '4': (101, 50, 45),   # подъём
    '5': (112, 56, 51),   # свет
    '6': (138, 80, 80),   # влага
    'v': (122, 64, 62),   # жила
    'V': (140, 84, 82),   # жила светлая
    'p': (156, 100, 96),  # пульс
}

# ── Ручные таблицы волокнистой основы ──────────────────────────────
# границы пучков по x (ширины 3,4,4,3,2)
BOUNDS = [0, 3, 7, 11, 14]
# горизонтальный дрейф границ по y (плавная волна, без скачков)
DRIFT = [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0, 0]
# подсветка волокна в каждом пучке: список (y0, y1, tone, смещение в пучке)
LIT = [
    [(1, 4, '4', 1), (7, 9, '4', 0), (12, 15, '4', 1)],          # пучок 0
    [(0, 1, '5', 2), (4, 8, '4', 2), (12, 13, '4', 1)],          # пучок 1
    [(2, 3, '4', 1), (6, 9, '5', 2), (13, 14, '4', 2)],          # пучок 2
    [(0, 2, '4', 1), (5, 6, '4', 0), (10, 13, '5', 1)],          # пучок 3
    [(3, 5, '4', 0), (9, 10, '4', 1), (14, 15, '4', 0)],         # пучок 4
]
# поперечные связки (1px тень поперёк пучка) — ручные
CROSS = [(5, 0), (10, 2), (3, 3), (13, 4)]
# провалы у границ (ямки)
PITS = [(2, 6), (8, 3), (12, 11)]
# влажные точки на свете
WET = [(4, 7), (13, 10)]


def base_flesh():
    b = [['3'] * S for _ in range(S)]
    # тень по границам пучков (дрейф)
    for y in range(S):
        for xb in BOUNDS:
            b[y][(xb + DRIFT[y]) % S] = '2'
    # подсветка волокон
    for bi, specs in enumerate(LIT):
        x0 = BOUNDS[bi]
        x1 = BOUNDS[bi + 1] if bi + 1 < len(BOUNDS) else S
        wid = (x1 - x0) % S or (x1 - x0)
        for y0, y1, tone, off in specs:
            for y in range(y0, y1 + 1):
                x = (x0 + DRIFT[y] + off) % S
                if b[y][x] == '3':
                    b[y][x] = tone
    # поперечные связки
    for y, bi in CROSS:
        x0 = BOUNDS[bi]
        for k in range(2):
            x = (x0 + DRIFT[y] + 1 + k) % S
            if b[y][x] in ('3', '4'):
                b[y][x] = '2'
    # ямки
    for x, y in PITS:
        b[y][x] = '1'
    return b


def veins(b, systems):
    """systems: список (контрольные точки, толщина, тона по длине)."""
    for ctrl, w in systems:
        for (x0, y0), (x1, y1) in zip(ctrl, ctrl[1:]):
            steps = max(abs(x1 - x0), abs(y1 - y0))
            for i in range(steps + 1):
                x = int(round(x0 + (x1 - x0) * i / steps)) % S
                y = int(round(y0 + (y1 - y0) * i / steps)) % S
                b[y][x] = 'v'
                if w == 2:
                    b[(y + 1) % S][x] = 'v'
    return b


def flesh_block():
    b = base_flesh()
    # главная прожилка: пересекает волокна поперёк, с развилкой
    veins(b, [
        ([(0, 4), (2, 5), (4, 5), (6, 6), (8, 6), (10, 7), (12, 7),
          (14, 8), (15, 8)], 1),
        ([(8, 6), (9, 9), (10, 10), (10, 12)], 1),
    ])
    for x, y in [(4, 5), (10, 7)]:
        b[y][x] = 'V'
    return b


def t1():
    b = base_flesh()
    veins(b, [([(0, 6), (3, 6), (5, 7), (7, 7), (9, 6), (11, 7), (13, 8),
               (15, 8)], 1),
              ([(9, 6), (10, 9), (11, 11)], 1)])
    b[7][5] = 'V'
    return b


def t2():
    b = base_flesh()
    veins(b, [([(0, 6), (3, 6), (5, 7), (7, 7), (9, 6), (11, 7), (13, 8),
               (15, 8)], 2)])
    veins(b, [([(5, 7), (6, 4), (7, 2), (7, 0)], 1),
              ([(11, 7), (12, 10), (13, 12), (13, 15)], 1),
              ([(7, 7), (6, 10), (5, 12)], 1)])
    for x, y in [(3, 6), (9, 6), (13, 8)]:
        b[y][x] = 'V'
    b[6][3] = 'p'
    return b


def t3():
    b = base_flesh()
    veins(b, [([(0, 3), (3, 4), (6, 4), (9, 5), (12, 5), (15, 6)], 2),
              ([(0, 12), (3, 11), (6, 11), (9, 10), (12, 10), (15, 9)], 2)])
    veins(b, [([(6, 4), (7, 7), (8, 9), (9, 10)], 2),
              ([(12, 5), (11, 8), (12, 10)], 2),
              ([(3, 4), (2, 7), (3, 11)], 1),
              ([(9, 5), (9, 2), (10, 0)], 1)])
    for x, y in [(7, 7), (8, 9), (11, 8)]:
        b[y][x] = 'V'; b[y][(x + 1) % S] = 'V'
    b[7][7] = 'p'; b[9][8] = 'p'
    return b


def t4():
    """Сплошная ткань жил: рамп жил вместо рамп плоти, волокна читаются."""
    b = [['v'] * S for _ in range(S)]
    for y in range(S):
        for xb in BOUNDS:
            b[y][(xb + DRIFT[y]) % S] = '3'      # швы-тени между наплывами
    for bi, specs in enumerate(LIT):
        x0 = BOUNDS[bi]
        for y0, y1, tone, off in specs:
            for y in range(y0, y1 + 1):
                x = (x0 + DRIFT[y] + off) % S
                if b[y][x] == 'v':
                    b[y][x] = 'V'
    for x, y in [(4, 7), (13, 10), (7, 2)]:
        b[y][x] = 'p'
    for x, y in [(2, 6), (8, 3)]:
        b[y][x] = '1'
    return b


def bimg(name):
    fn = {'flesh_block': flesh_block, 't1': t1, 't2': t2, 't3': t3, 't4': t4}[name]
    b = fn()
    return [[RAM[c] for c in row] for row in b], b


if __name__ == "__main__":
    names = ['flesh_block', 't1', 't2', 't3', 't4']
    sheet = Image.new('RGBA', (96 * 5, 96))
    for i, n in enumerate(names):
        rgb, chars = bimg(n)
        im = to_image(rgb).resize((96, 96), Image.NEAREST)
        sheet.paste(im, (i * 96, 0))
        print(n, "seam:", seam_metric(rgb), "mass%:", main_share(rgb, RAM['3']))
    sheet.save("/home/user/carnis/previews/core5.png")
    # отдельные симы для 3х3
    for n in names:
        rgb, _ = bimg(n)
        seam_sheet(rgb).resize((384, 384), Image.NEAREST).save(
            f"/home/user/carnis/previews/seam_{n}.png")
