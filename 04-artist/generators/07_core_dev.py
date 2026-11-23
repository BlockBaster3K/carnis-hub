#!/usr/bin/env python3
"""Dev v7: ручная карта flesh_block, финальная композиция.
Крупные лоскуты света, Y-трещины, ямки, мембранная жила с вилкой."""
import sys
sys.path.insert(0, '/home/user/carnis/tools')
from carnis_px import to_image, seam_sheet, seam_metric
from PIL import Image

S = 16
RAM = {
    'd': (58, 24, 21),
    's': (76, 35, 33),
    'a': (90, 43, 40),
    'b': (101, 50, 46),
    'c': (112, 56, 51),
    'v': (122, 64, 62),
    'V': (142, 86, 84),
    'w': (134, 78, 76),
}
MAP = [
    "aaaaaaasaaaaaaaa",
    "abbbbbasaaaaaaaa",
    "abbcbwsaaaaaaaaa",
    "abbbbbsaaaaaasaa",
    "abbbbsaaaaaaaaas",
    "aaaassaaabbbbaaa",
    "aaaasaaaabcccbaa",
    "aaaasaaavvccbbaa",
    "vvaaaaaavaabwbaa",
    "aaVvvaavaaaabaaa",
    "aaaaavvVvvaaaaaa",
    "abbbaaaaaavvVvaa",
    "abcbaaaaasaaaaav",
    "aabbbaaasaaasbba",
    "aaaaaaaaaasdabbb",
    "aaaaaaasaaaaaabb",
]

def paint():
    return [[c for c in row] for row in MAP]

def report(name, g):
    rgb = [[RAM[c] for c in row] for row in g]
    to_image(rgb).resize((160, 160), Image.NEAREST).save(f"/home/user/carnis/previews/v7_{name}.png")
    seam_sheet(rgb).resize((288, 288), Image.NEAREST).save(f"/home/user/carnis/previews/v7seam_{name}.png")
    print(name, "seam:", seam_metric(rgb))
    from collections import Counter
    cnt = Counter(c for row in g for c in row)
    print("  доли:", {k: round(100 * v / 256) for k, v in cnt.most_common()})
    return rgb

if __name__ == "__main__":
    if __name__ == "__main__":
        g = paint()
        bad = [i for i, r in enumerate(MAP) if len(r) != 16]
        if bad:
            print("!! строки неверной длины:", bad, [len(MAP[i]) for i in bad])
        else:
            report('flesh_block', g)
