#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""glow_check.py — приёмка A4-p7 (палитра существ) по ТЗ 3.7.0 §2.3.

Проверяет 8 файлов из 04-artist/deliverables/Carnis_3.7.0_A4p7_palette.zip:
    4 тела      infected_{creeper,skeleton,spider,zombie}.png
    4 glowmask  infected_{...}_glowmask.png

Критерии (все измеримые, из ТЗ §2.3):
  1. размеры 64x32 / 64x32 / 64x32 / 64x64 — не изменились;
  2. альфа только 0 и 255;
  3. ровно 7 непрозрачных цветов, все из BASELINE_PALETTE (альфа у этих тел
     только 255 — прозрачных пикселей нет, уникальных RGBA ровно 7; замер
     Ревизора T-3167 на 3.7.2: 4 файла, alpha={255}, (0,0,0,0) не встречается);
  4. маска (альфа > 0) побитово идентична эталону из 01-coder/3.6.0-R;
  5. glowmask — ровно один цвет свечения: строго (255,92,57), как у принятых масок.

Использование:
    python3 tools/glow_check.py <каталог|zip> [эталонный zip]

Код возврата: 0 — ИТОГ: СХОДИТСЯ, 2 — ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ, 1 — ошибка запуска.
"""

import io
import os
import sys
import zipfile

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("ОШИБКА: нужен Pillow (python3 -m pip install Pillow)")
    sys.exit(1)

REL = "src/main/resources/assets/carnis/textures/entity/"
BODY = ["infected_creeper.png",
        "infected_skeleton.png",
        "infected_spider.png",
        "infected_zombie.png"]
GLOW = ["infected_creeper_glowmask.png",
        "infected_skeleton_glowmask.png",
        "infected_spider_glowmask.png",
        "infected_zombie_glowmask.png"]
SIZES = {"infected_creeper.png": (64, 32),
         "infected_skeleton.png": (64, 32),
         "infected_spider.png": (64, 32),
         "infected_zombie.png": (64, 64),
         "infected_creeper_glowmask.png": (64, 32),
         "infected_skeleton_glowmask.png": (64, 32),
         "infected_spider_glowmask.png": (64, 32),
         "infected_zombie_glowmask.png": (64, 64)}
GLOW_COLOR = (255, 92, 57, 255)

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
OPAQUE_BASE = {c for c in BASELINE_PALETTE if c[3] > 0}

DEFAULT_REF = "01-coder/3.6.0-R/project-3.6.0-R-clean.zip"

# З-17: эталон может лежать не на диске, а в git-объекте (см. baseline.py).
import baseline  # noqa: E402

problems = []


def note(msg):
    problems.append(msg)
    print("  [!] " + msg)


def load_from(src, name):
    """Прочитать PNG как RGBA из каталога или zip по целевому пути."""
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            want = REL + name
            cand = [n for n in z.namelist()
                    if n.replace("\\", "/").endswith(want)]
            if not cand:
                return None
            with z.open(cand[0]) as f:
                return Image.open(io.BytesIO(f.read())).convert("RGBA")
    path = os.path.join(src, REL, name)
    if not os.path.exists(path):  # допускаем плоский каталог из 8 PNG
        path = os.path.join(src, name)
    if not os.path.exists(path):
        return None
    return Image.open(path).convert("RGBA")


def mask_of(img):
    """Побитовая маска непрозрачных пикселей: set индексов."""
    raw = img.tobytes()
    return {i // 4 for i in range(0, len(raw), 4) if raw[i + 3] > 0}


def check_candidate(src, ref_src):
    print("A4-p7 — палитра существ (ТЗ 3.7.0 §2.3)")
    print("Кандидат:  %s" % src)
    print("Эталон:    %s" % ref_src)
    print()

    if not zipfile.is_zipfile(src) and not os.path.isdir(src):
        print("ОШИБКА: нет такого каталога или zip: %s" % src)
        return 1

    print("1) Размеры и альфа")
    for name in BODY + GLOW:
        img = load_from(src, name)
        if img is None:
            note("%s — файла нет в сдаче" % name)
            print("  %-36s ОТСУТСТВУЕТ" % name)
            continue
        w, h = img.size
        exp = SIZES[name]
        ok_size = (w, h) == exp
        alphas = sorted(set(img.tobytes()[3::4]))
        ok_alpha = alphas == [0, 255] or alphas == [255]
        print("  %-36s %dx%d %s  альфы %s %s"
              % (name, w, h, "ok" if ok_size else "НЕ %dx%d" % exp,
                 alphas, "ok" if ok_alpha else "<- промежуточная альфа"))
        if not ok_size:
            note("%s — размер %dx%d вместо %dx%d" % (name, w, h, exp[0], exp[1]))
        if not ok_alpha:
            note("%s — альфа не только 0/255: %s" % (name, alphas))

    print()
    print("2) Палитра тел — ровно 7 непрозрачных цветов из BASELINE_PALETTE")
    for name in BODY:
        img = load_from(src, name)
        if img is None:
            continue
        raw = img.tobytes()
        colours = {tuple(raw[i:i + 4]) for i in range(0, len(raw), 4)}
        opaque = {c for c in colours if c[3] > 0}
        extra = opaque - OPAQUE_BASE
        # ВАЖНО: «7 непрозрачных + прозрачный = 8 значений» — это описание
        # палитры, а не требование к каждому файлу. У тел заражённых мобов
        # прозрачных пикселей нет вовсе (альфа вся 255), поэтому в файле
        # физически может быть только 7 значений. Требуем ровно 7 непрозрачных
        # и отсутствие чего-либо вне BASELINE_PALETTE.
        outside = colours - BASELINE_PALETTE
        ok_pal = len(opaque) == 7 and not outside
        print("  %-36s цветов всего %d, непрозрачных %d, вне палитры %d %s"
              % (name, len(colours), len(opaque), len(outside),
                 "ok" if ok_pal else ""))
        if extra:
            note("%s — %d непрозрачных цветов вне BASELINE_PALETTE: %s"
                 % (name, len(extra), sorted(extra)[:4]))
        if outside - extra:
            note("%s — цвет с промежуточной альфой вне палитры" % name)
        if len(opaque) != 7:
            note("%s — непрозрачных цветов %d, ТЗ требует ровно 7"
                 % (name, len(opaque)))

    print()
    print("3) Glowmask — один цвет свечения, строго (255, 92, 57)")
    for name in GLOW:
        img = load_from(src, name)
        if img is None:
            continue
        raw = img.tobytes()
        opaque = {tuple(raw[i:i + 4]) for i in range(0, len(raw), 4) if raw[i + 3] > 0}
        print("  %-36s непрозрачных цветов %d %s"
              % (name, len(opaque), sorted(opaque)))
        if len(opaque) != 1:
            note("%s — цветов свечения %d, ТЗ требует один" % (name, len(opaque)))
        elif opaque != {GLOW_COLOR}:
            note("%s — цвет %s, требуется (255, 92, 57, 255)"
                 % (name, sorted(opaque)[0]))

    print()
    print("4) Маска побитово идентична эталону (силуэт не тронут)")
    for name in BODY + GLOW:
        img = load_from(src, name)
        ref = load_from(ref_src, name)
        if img is None or ref is None:
            note("%s — не с чем сравнить (нет кандидата или эталона)" % name)
            continue
        if img.size != ref.size:
            note("%s — размеры разные, маску не сверить" % name)
            continue
        a, b = mask_of(img), mask_of(ref)
        missing = len(b - a)
        added = len(a - b)
        print("  %-36s маска %d px  пропало %d  добавилось %d %s"
              % (name, len(b), missing, added,
                 "ok" if not missing and not added else "<- СИЛУЭТ ИЗМЕНЁН"))
        if missing or added:
            note("%s — маска не совпала: пропало %d px, добавилось %d px"
                 % (name, missing, added))

    print()
    if problems:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — %d" % len(problems))
        for i, p in enumerate(problems, 1):
            print("  %2d. %s" % (i, p))
        return 2
    print("ИТОГ: СХОДИТСЯ")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    # З-17: эталон ищем не только на диске, но и в git-объекте. Иначе
    # sparse-checkout проверяющего превращает «нет файла» в «✗ расхождение».
    if len(sys.argv) > 2:
        ref, ref_status, ref_src = sys.argv[2], "ok", "argv"
        if not zipfile.is_zipfile(ref) and not os.path.isdir(ref):
            print("ОШИБКА: эталон не найден: %s" % ref)
            print("Укажите вторым аргументом ZIP пакета 3.6.0-R (эталон масок).")
            return 1
    else:
        ref, ref_status, ref_src = baseline.resolve(DEFAULT_REF)
    if ref_status != baseline.OK:
        # Пропуск — не отказ. Код 2: «проверка не выполнена», а не «✗».
        print("  · эталон недоступен — проверка пропущена")
        print("ИТОГ: ПРОПУЩЕНО (эталон недоступен — ни на диске, ни в git)")
        return 2
    return check_candidate(src, ref)


if __name__ == "__main__":
    sys.exit(main())
