"""
tendrils_lab.py — визуальный стенд: смешанные стены 3×3 и 5×5, проекция 16 px.

Использует генератор tendrils_gen.py. Ничего не сдаёт — только стенд оценки.

Запуск:  python3 tools/tendrils_lab.py <каталог вывода>
"""

from __future__ import annotations

import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tendrils_gen as gen  # noqa: E402

SIZE = gen.SIZE


def mix_pattern(n, seed):
    """Детерминированное псевдослучайное смешение вариантов."""
    def h(a, b):
        v = (a * 0x1F1F1F1F + b * 0x9E3779B9 + seed * 0x85EBCA6B) & 0xFFFFFFFF
        v = ((v ^ (v >> 15)) * 0x2545F491) & 0xFFFFFFFF
        v = ((v ^ (v >> 13)) * 0x27D4EB2F) & 0xFFFFFFFF
        return ((v ^ (v >> 16)) & 0xFFFFFFFF) / 4294967295.0
    return [[int(h(y * 16 + x, 3) * 4) % 4 for x in range(n)] for y in range(n)]


def wall(imgs, pat):
    n = len(pat)
    out = Image.new("RGBA", (SIZE * n, SIZE * n))
    for y in range(n):
        for x in range(n):
            out.paste(imgs[pat[y][x]], (x * SIZE, y * SIZE))
    return out


def to16(img):
    return img.resize((16, 16), Image.LANCZOS)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/lab"
    os.makedirs(out, exist_ok=True)
    imgs = [gen.generate(i)[0] for i in range(4)]

    strip = Image.new("RGBA", (4 * SIZE + 30, SIZE))
    for i, im in enumerate(imgs):
        strip.paste(im, (i * (SIZE + 10), 0))
    strip.save(f"{out}/tiles.png")
    for i, im in enumerate(imgs):
        to16(im).resize((256, 256), Image.NEAREST).save(f"{out}/tile16_{i}.png")

    for n in (3, 5):
        pat = mix_pattern(n, 977 + n)
        w = wall(imgs, pat)
        w.save(f"{out}/wall_{n}x{n}.png")
        w16 = wall([to16(im) for im in imgs], pat)
        w16.resize((320, 320), Image.NEAREST).save(f"{out}/wall_{n}x{n}_at16.png")
        w16.resize((320, 320), Image.BILINEAR).save(f"{out}/wall_{n}x{n}_at16_smooth.png")
        print("паттерн", n, pat)

    # горизонтальный срез через середину — видно, как ведут себя стыки
    w = wall(imgs, mix_pattern(5, 977 + 5))
    w.crop((0, 2 * SIZE + 20, 5 * SIZE, 2 * SIZE + 44)).resize((5 * SIZE * 3, 72), Image.NEAREST).save(
        f"{out}/seam_row.png")


if __name__ == "__main__":
    main()
