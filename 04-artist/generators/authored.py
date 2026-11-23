#!/usr/bin/env python3
"""
authored.py — единая авторская карта всех 12 текстур партии 1.
Каждая текстура: палитра + 16 строк по 16 символов. Никакой генерации.
Здесь же рендер превью и метрики. Финальные скрипты собираются из этих данных.
"""
import sys
sys.path.insert(0, '/home/user/carnis/tools')
from carnis_px import (to_image, seam_sheet, seam_metric, brightness_range)
from PIL import Image

S = 16

# ═══════════════════ ПАЛИТРЫ ═══════════════════
FLESH = {
    'd': (54, 22, 20), 's': (70, 32, 30), 'a': (88, 42, 39), 'b': (98, 47, 43),
    'c': (107, 53, 48), 'v': (121, 58, 52), 'V': (136, 71, 63), 'p': (150, 88, 77),
    'w': (126, 70, 66),
}
BONE = {
    'd': (60, 47, 45), 's': (72, 57, 55), 'a': (86, 70, 67), 'b': (101, 82, 77),
    'B': (138, 118, 113), 'p': (148, 126, 120), 'w': (122, 100, 94),
}
CHARRED = {
    'd': (40, 26, 22), 's': (56, 36, 31), 'a': (74, 48, 40), 'b': (90, 63, 55),
    'e': (124, 88, 76), 'w': (98, 70, 60),
}
REFRACTORY = {
    'd': (62, 44, 58), 's': (74, 53, 69), 'a': (90, 69, 85), 'b': (106, 85, 101),
    'c': (122, 101, 122), 'w': (132, 112, 130), 'r': (98, 74, 90),
}
STOMACH = {
    'd': (62, 68, 41), 's': (74, 80, 53), 'a': (90, 96, 64), 'b': (106, 112, 80),
    'c': (124, 130, 96), 'B': (138, 144, 112), 'w': (144, 150, 118), 'y': (128, 122, 74),
    'e': (46, 50, 30),
}
NERVE = {
    'd': (60, 46, 56), 's': (74, 58, 69), 'a': (90, 74, 85), 'b': (106, 90, 101),
    'N': (122, 138, 160), 'n': (148, 166, 188), 'y': (138, 96, 112), 'w': (110, 94, 105),
}
SINEW = {
    'd': (60, 26, 26), 's': (74, 32, 32), 'a': (106, 48, 48), 'b': (122, 64, 64),
    'r': (138, 80, 80), 't': (170, 128, 128), 'w': (146, 92, 92), 'k': (90, 40, 40),
}

# ═══════════════════ КАРТЫ ═══════════════════

flesh_block = [
"aaabaaaaasaaacba",
"bbabaaaababaabaa",
"aasaabbaaaasabaa",
"aaaadsaaaaaaabaa",
"awaaaaaaaaaaaaba",
"absabbaaawbabaaa",
"aaaaaaaasabbbaaa",
"babbaacaaasbasbs",
"asaaabaabbaaaaab",
"saaaabaaadawbaaa",
"abvaaavaabvaaasa",
"aaacvvaaVvaabaaa",
"aadbvaasaavaabbb",
"bbaaabaaaavaaasa",
"sabaaaacvaaaaaab",
"aasabasaaaasbaaa",
]

veins_t1 = [
"aaabaaaaasaaacba",
"bbabaaaababaabaa",
"aasaabbaaaasabaa",
"aaaadsaaaaaaabaa",
"awaaaaavvaaaaaba",
"absabbavvbabaaaa",
"aaaaaaaavvbbbaaa",
"babbaacaaavbasbs",
"asaaabaabbvaaaab",
"saaaabaaadawbaaa",
"abvaaavaabvaavsa",
"aaacvvaaVvaabaaa",
"aadbvaasaavaabbb",
"bbaaabaaaavaaasa",
"sabaaaacvaaaaaab",
"aasabasaaaasbaaa",
]
# заменить B на V (недостающий тон)
veins_t1 = [r.replace('B', 'V') for r in veins_t1]

veins_t2 = [
"vabaaaaaasaaacba",
"vbabvaaababaabaa",
"vvsaabbaaasabaaa",
"avaadvsaavaaabaa",
"avaawaaaaavaabaa",
"avsabbaaawvabaaa",
"avabbaasavbbbaaa",
"abbaacaaavsbasbs",
"asaaabaaavaaabbb",
"saaaabaaadawbaaa",
"abvaaavaabvbaasa",
"aacvvaaVvavbabbb",
"aadbvaasaavabbba",
"bbaaabaaaavvaasa",
"sabaaaacvaaavvab",
"aasabasaaaasvbaa",
]

# t3: базовое зерно + толстые протоки (2 px), обрывающиеся
veins_t3 = [
"aaabaaaaasaaacba",
"bbabaaaababaabaa",
"aasaabbaaaasabaa",
"aaaadsaaaaaaabaa",
"awaaaaaaaaaaaaba",
"absabbaaawbabaaa",
"aaaaaaaasabbbaaa",
"babbaacaaasbasbs",
"asaaabaabbaaaaab",
"saaaabaaadawbaaa",
"abvaaavaabvaaasa",
"aaacvvaaVvaabaaa",
"aadbvaasaavaabbb",
"bbaaabaaaavaaasa",
"sabaaaacvaaaaaab",
"aasabasaaaasbaaa",
]
def _put(rows, pts):
    R = [list(r) for r in rows]
    for x, y, c in pts:
        R[y % 16][x % 16] = c
    return [''.join(r) for r in R]
def _band(rows, path, width=2, tone='v'):
    R = [list(r) for r in rows]
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            R[y % 16][x % 16] = tone
            if width >= 2: R[(y + 1) % 16][x % 16] = tone
            if width >= 3: R[y % 16][(x + 1) % 16] = tone
    return [''.join(r) for r in R]

veins_t3 = _band(veins_t3, [(0, 2), (3, 2), (4, 3), (7, 3), (8, 4)], 2)
veins_t3 = _band(veins_t3, [(4, 3), (5, 6), (6, 7), (9, 8), (10, 10), (13, 11), (14, 13), (15, 15)], 2)
veins_t3 = _band(veins_t3, [(8, 4), (11, 5), (12, 6)], 2)
veins_t3 = _band(veins_t3, [(10, 10), (11, 12), (14, 13)], 2)
veins_t3 = _band(veins_t3, [(0, 9), (2, 9), (3, 10)], 2)
veins_t3 = _put(veins_t3, [(2, 2, 'V'), (7, 3, 'V'), (5, 6, 'V'), (11, 5, 'V'), (9, 8, 'V'),
                           (13, 11, 'V'), (14, 13, 'V'), (5, 6, 'p'), (10, 10, 'p'), (2, 2, 'p'),
                           (6, 7, 'w'), (12, 6, 'w'), (15, 15, 'w'), (3, 13, 's'), (7, 12, 's')])

# t4: сплошная ткань жил — зерно в рампе жилы
veins_t4 = [
"VpVbbvvaaVVVVVvv",
"wVVVabvaaVVpwbbv",
"VVVpwbsvbbpVVVba",
"aVVVVbbvbabVVbaa",
"aaVVVVbbbadvvaba",
"vvavvbbavbbbsvav",
"vvavbbbasvbaavdv",
"bvvvvVVVvvbbbbbb",
"bavsbVpwVvvaVVwa",
"bdavbbVVpVbbVpVw",
"bbbbaavVVVVvvVpb",
"VVVabvsaabbbbbVV",
"VppVbvaabVVVvvbb",
"aVwVbbbaapwVVbbb",
"vvVVVvvabbVVpVbb",
"vaaVVaavvabVVbba",
]

# ── bone_flesh: серо-бордовая хрящевая масса + бледные костные включения
bone_flesh = [
    'pBBasaaaaaaaaaaa',
    'BwBBaabbaaabbaaa',
    'BBBBBabaaaabaBBa',
    'aBBBsaaawbaaaaaa',
    'asssaaaBbaaaaaaa',
    'aaaaaaaBaaaaaaaa',
    'bbdabbasapBBBsaa',
    'baaabaaaaBpwBBsa',
    'BBaaaaaaaaBBBBsa',
    'aaaaaadasaaBBssa',
    'aaaaaaaaasassabb',
    'aapBBasaaaaaaaba',
    'aaBpwBsbbbaaadaa',
    'bbaBBBsbaaaaaaBB',
    'aaaaBBsaBaaaaaaa',
    'aaaaasaaaBaaaaaa',
]

# ── charred_flesh: обугленная плоть, трещины с живой тканью на дне
charred_flesh = [
"ssssdassaaasssaa",
"sssaadsssadasssa",
"sssbbeasaadaasda",
"asabbawabbaeaadd",
"daddaaeabsssdabb",
"aeadssadeasseaab",
"adassssdawabbwaa",
"adwasaaaeadbadda",
"ssseaaasssadasss",
"sssawdassssdaass",
"asaaabdasaaaedsa",
"aaaaabaaadasssda",
"aabbsssaaaeasssa",
"aabassssddawasaa",
"ssaaasdeassddaaa",
"sssaaabbaasabbaa",
]

# ── refractory_flesh: гладкая серо-пурпурная кожа/рог, крупные плоскости
refractory_flesh = [
"bbbbwbsaaaaaaaaa",
"baacabsaaaaaaaaa",
"baaaasaasbbbbbbb",
"bbbbbsaasbaaacab",
"aaasaassabaaaaab",
"aasaaaaasbbbbbbb",
"asaaaaadrsaaaaaa",
"assaaaarasaaaaaa",
"aaasaaaaassaaaaa",
"aabbbbbbbsaaaada",
"aabaaacasaabbbbb",
"aawaaaaabaabaaab",
"aabbbcbbbaabwaab",
"aaaaaaaaaaabaaab",
"aaaaaaaaaasbbbbb",
"aaaaaaaaassaaaas",
]

# ── stomach_pool_top: поверхность желудочного сока
stomach_pool_top = [
"abaaaaaaaaaaaaaa",
"abcaaaaaaaaaaaaa",
"abbaaBacbaaaasaa",
"aabaBwBabyaaasaa",
"aabaaBaaabbaaaaa",
"aabbsssaabaaaaaa",
"ayabsbaaabaaBaac",
"aaabbbaaabbBwBaa",
"aasbbaaaaacbBaaa",
"aaaabaaaaabbbaaa",
"aaaBbcaaaabssaaa",
"aaaabbaaaabsaaya",
"dBawaBbaaaabaaaa",
"aaaaabayaaabbaaa",
"aaaBaaaaaaabdaaa",
"aaaaaaaaaaabaaaa",
]

# ── stomach_pool_side: складчатая стенка; верх темнее (стык с жидкостью)
stomach_pool_side = [
"ssssssssssssssss",
"sddssddssddssdds",
"bbsybsabsaysabsy",
"abbyabyabsybsabs",
"abbsabsabsybsabs",
"bbsabsabsabsacca",
"bbcccsabsabsabsa",
"bsabsabsabsabsab",
"sabsabsabsabsabb",
"sabsabsabccbsabb",
"absawsabsabsabbs",
"absabsabsabsabbs",
"sabsabsabsawsabb",
"sabsabsabsabsabb",
"bsabsabswbsabsab",
"bsabsabsabsabsab",
]

# ── stomach_pool_bottom: тёмный осадок с зеленоватым оттенком
stomach_pool_bottom = [
"ssssssssssssssss",
"sssssssssaaaasss",
"saaaasyysaddasss",
"saddassssaawassb",
"saawassssssssbss",
"bssssssssbssssss",
"sssyssssssssysss",
"sysssssssssssssy",
"ssbssssssssbssss",
"ssssaaaassssaaaa",
"ssssaddassssadda",
"ssssaaawssssaawa",
"aaaassbsssssaaaa",
"eeaasysseaaasses",
"aaaassssaddassss",
"aaaassssaaaassss",
]

# ── nerve_pillar: вертикальные волокна, внизу толще (корни), вверху тоньше
nerve_pillar = [
"asNaaaasNaasNaaa",
"asNabaasNaasNaaa",
"asNyaaaasNabNaaa",
"aasnaaaasNsNaaaa",
"absNaaaasNsNaaaa",
"aasNaaaasNbNyaaa",
"aasNaaasNNasnaab",
"aaasNaabNNasNaaa",
"aaasNNasnNasNaaa",
"aaasNNasNyaasNba",
"aaasNNbNNaaasNaa",
"aasnNasNNaaasNaa",
"aabNNasNNaasNyaa",
"aasNNasnNaasNNaa",
"aasNNNNNNNasNNNa",
"aasNNNNNNNasNNNa",
]

# ── nerve_pillar_top: срез ствола, концентрические кольца
nerve_pillar_top = [
"aaaaaaaNNaaaaaaa",
"aaaasssNNsssaaaa",
"aaasNNNssNNNsaaa",
"aasyyssssssNNsaa",
"asNNsNNNNNNsNwsa",
"asNsNNnnnnNNsNsa",
"asNsNnyyyynNsNsa",
"NNssNnynnynNssNa",
"NNssNnynnynNssNa",
"asNsNnyyyynNsNsa",
"asNsNNnnnnNNsNsa",
"asNNsNNNNNNwNNsa",
"aawNNssssssNNsaa",
"aaasNNNssNNNsaaa",
"aaaasssNNsssaaaa",
"aaaaaaassaaaaaaa",
]

# ── sinew_spikes: мясистая поверхность с направленными рёбрами
sinew_spikes = [
"asrbststaasrrsra",
"astbststabstrrsa",
"asrbsrsrbbsrwsra",
"asrasrsrbbbsrrra",
"basrsrrabaasrrra",
"bbswasrasaasrrra",
"abskaskaaaksrrsr",
"aasrasrbaaasrrsr",
"aasrasraaasrrasw",
"aabsrsrwabsrrasr",
"rabsrrsrabsrraas",
"raksrrsrbksrraks",
"raasrrsrbsrraaas",
"rbaswrsrasrrbbas",
"rbasrrsrasrrbbas",
"raasrrbsrsrraabs",
]

TEXTURES = [
    ("flesh_block", FLESH, flesh_block),
    ("flesh_veins_t1", FLESH, veins_t1),
    ("flesh_veins_t2", FLESH, veins_t2),
    ("flesh_veins_t3", FLESH, veins_t3),
    ("flesh_veins_t4", FLESH, veins_t4),
    ("bone_flesh", BONE, bone_flesh),
    ("charred_flesh", CHARRED, charred_flesh),
    ("refractory_flesh", REFRACTORY, refractory_flesh),
    ("stomach_pool_top", STOMACH, stomach_pool_top),
    ("stomach_pool_side", STOMACH, stomach_pool_side),
    ("stomach_pool_bottom", STOMACH, stomach_pool_bottom),
    ("nerve_pillar", NERVE, nerve_pillar),
    ("nerve_pillar_top", NERVE, nerve_pillar_top),
    ("sinew_spikes", SINEW, sinew_spikes),
]


def build(pal, rows):
    for i, r in enumerate(rows):
        assert len(r) == 16, f"row {i}: {len(r)}"
        for ch in r:
            assert ch in pal, f"row {i}: неизвестный тон {ch!r}"
    return [[pal[ch] for ch in r] for r in rows]


if __name__ == "__main__":
    sheet = Image.new('RGBA', (7 * 96, 2 * 96))
    for idx, (name, pal, rows) in enumerate(TEXTURES):
        g = build(pal, rows)
        to_image(g).resize((96, 96), Image.NEAREST).save(f"/home/user/carnis/previews/A_{name}.png")
        seam_sheet(g).resize((192, 192), Image.NEAREST).save(f"/home/user/carnis/previews/AS_{name}.png")
        h, v = seam_metric(g)
        lo, hi = brightness_range(g)
        x = (idx % 7) * 96
        y = (idx // 7) * 96
        sheet.paste(to_image(g).resize((96, 96), Image.NEAREST), (x, y))
        print(f"{name:22s} seam h/v = {h:>4} / {v:>4}   lum {lo}..{hi}")
    sheet.save("/home/user/carnis/previews/A_all.png")
