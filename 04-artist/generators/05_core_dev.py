#!/usr/bin/env python3
"""Dev v5: фасцикулы (пучки волокон) вместо сплошных полос.
Пучок = прямоугольный регион с волокнами и своей фазой волны.
Между пучками — борозды. Перегородки поперёк. Жилы — диагонали."""
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
# фасцикул: x0,x1 (вкл.), y0,y1 (вкл.), phase — фаза волны
FASC = [
    (0, 5, 0, 8, 0),      # левый верх
    (0, 6, 10, 15, 5),    # левый низ, другая фаза
    (7, 12, 0, 15, 3),    # центральный — длинный
    (14, 15, 1, 13, 8),   # правый узкий
]
# волновая функция: смещение по y — ручная синусоида (период 16)
WAVE = [0, 1, 2, 2, 1, 0, -1, -2, -2, -1, 0, 1, 2, 2, 1, 0]


def w(y, phase):
    return WAVE[(y + phase) % S]


def base():
    g = [['2'] * S for _ in range(S)]      # борозды по умолчанию
    for (x0, x1, y0, y1, ph) in FASC:
        for y in range(y0, y1 + 1):
            off = w(y, ph)
            # пучок длиной L: чередование тень/тело/свет
            L = x1 - x0
            for i in range(L + 1):
                x = (x0 + i + off) % S
                if i == L:
                    g[y][x] = '2'                 # правая граница — тень
                elif i == 0:
                    g[y][x] = '4'                 # левый край — свет
                else:
                    g[y][x] = '3'
            # внутреннее волокно посередине — тень
            if L >= 3:
                xm = (x0 + L // 2 + w(y, ph + 2)) % S
                if g[y][xm] == '3':
                    g[y][xm] = '2'
            # световой мазок у верхней трети пучка
            if y0 + 1 <= y <= y0 + 3 and L >= 2:
                xs = (x0 + 1 + off) % S
                if g[y][xs] == '3':
                    g[y][xs] = '5'
    # поперечные перегородки в местах стыка пучков
    for (y, xa, xb) in [(9, 0, 6), (0, 0, 5), (14, 14, 15), (0, 14, 15)]:
        for x in range(xa, xb + 1):
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
    to_image(rgb).resize((96, 96), Image.NEAREST).save(f"/home/user/carnis/previews/v5_{name}.png")
    seam_sheet(rgb).resize((288, 288), Image.NEAREST).save(f"/home/user/carnis/previews/v5seam_{name}.png")
    print(name, seam_metric(rgb))


def flesh_block():
    g = base()
    vein(g, [(0, 11), (2, 11), (3, 12), (5, 12), (6, 13), (8, 13), (9, 14),
             (11, 14), (12, 15)])
    vein(g, [(6, 13), (6, 10), (7, 9)])
    g[12][3] = 'V'
    return g


if __name__ == "__main__":
    finish(flesh_block(), 'flesh_block')
