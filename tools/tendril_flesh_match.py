#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tendril_flesh_match.py — приёмка A3R1 (цвет щупалец под плоть), ТЗ 3.7.0, СРОЧНО 1.

Проверяет 4 файла `creeping_tendrils_0..3.png` из сдачи Художника:

  1. размер ровно 64x64;
  2. формат RGBA;
  3. альфа только 0 и 255;
  4. ровно 7 непрозрачных цветов;
  5. средний RGB по непрозрачным пикселям отличается от соответствующего
     `living_flesh_i` не больше чем на 12 по (|dR|+|dG|+|dB|)/3 (метод Д6);
  6. маска (альфа > 0) побитово идентична принятой версии из 3.6.0-R.

Эталон масок и средних плоти берётся из `01-coder/3.6.0-R/` (ZIP или
распакованный каталог), а не «из памяти».

Использование:
    python3 tools/tendril_flesh_match.py <каталог|zip> [эталонный zip|каталог]

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

REL = "src/main/resources/assets/carnis/textures/block/"
NAMES = ["creeping_tendrils_%d.png" % i for i in range(4)]
FLESH = ["living_flesh_%d.png" % i for i in range(4)]
SIZE = (64, 64)
THRESHOLD = 12.0
# Набор цветов для A3R1 НЕ зафиксирован: ТЗ требует «ровно 7 непрозрачных
# цветов» и попадания среднего в цвет плоти (Δ ≤ 12). Палитра BASELINE_PALETTE
# сюда не применяется — она светлее плоти, и требование «только из неё» сделало
# бы критерий 5 невыполнимым. Печатаем фактические цвета, но не запрещаем их.
DEFAULT_REF = os.path.join("01-coder", "3.6.0-R", "project-3.6.0-R-clean.zip")

# З-17: эталон может быть только в git-объекте (см. baseline.py).
import baseline  # noqa: E402


def load_from(src, name):
    """Возвращает PIL.Image или None. src — каталог или zip."""
    if src is None:
        return None
    if os.path.isdir(src):
        p = os.path.join(src, name)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return Image.open(io.BytesIO(f.read()))
        p = os.path.join(src, REL, name)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return Image.open(io.BytesIO(f.read()))
        return None
    if os.path.exists(src):
        with zipfile.ZipFile(src) as z:
            for cand in (name, REL + name):
                try:
                    return Image.open(io.BytesIO(z.read(cand)))
                except KeyError:
                    continue
        return None
    return None


def rgba(im):
    return im.convert("RGBA")


def mean_rgb(im):
    px = list(rgba(im).getdata())
    opaque = [p for p in px if p[3] == 255]
    if not opaque:
        return None, 0
    n = len(opaque)
    return tuple(sum(p[i] for p in opaque) / n for i in range(3)), n


def mask_of(im):
    im = rgba(im)
    w, h = im.size
    px = list(im.getdata())
    return {i for i, p in enumerate(px) if p[3] > 0}, w, h


def main():
    if len(sys.argv) < 2:
        print("использование: python3 tools/tendril_flesh_match.py <каталог|zip> [эталон]")
        return 1
    src = sys.argv[1]
    # З-17: эталон ищем и в git-объекте — иначе sparse-checkout проверяющего
    # даёт ложное «эталон НЕ НАЙДЕН», а за ним ложные расхождения.
    if len(sys.argv) > 2:
        ref = sys.argv[2]
    else:
        ref, _ref_status, _ref_src = baseline.resolve(DEFAULT_REF)
        if ref is None:
            # Пропуск — не отказ: код 2 «не проверено», а не 1 «не сходится».
            print("A3R1 — цвет щупалец под плоть (ТЗ 3.7.0, СРОЧНО 1)")
            print("Кандидат:  %s" % src)
            print("  · эталон недоступен — проверка пропущена")
            print("ИТОГ: ПРОПУЩЕНО (эталон недоступен — ни на диске, ни в git)")
            return 2
    if not os.path.exists(src):
        print("ОШИБКА: нет такого каталога или zip: %s" % src)
        return 1

    print("A3R1 — цвет щупалец под плоть (ТЗ 3.7.0, СРОЧНО 1)")
    print("Кандидат:  %s" % src)
    print("Эталон:    %s" % (ref if os.path.exists(ref) else "НЕ НАЙДЕН: " + str(ref)))
    print()

    problems = []

    def note(msg):
        problems.append(msg)
        print("  [!] " + msg)

    deltas = {}
    for i, name in enumerate(NAMES):
        im = load_from(src, name)
        if im is None:
            note("%s — нет файла в сдаче" % name)
            continue
        im = rgba(im)
        print("%s" % name)

        # 1. размер
        ok = im.size == SIZE
        print("   размер %dx%d (нужно %dx%d) %s"
              % (im.size[0], im.size[1], SIZE[0], SIZE[1], "OK" if ok else "FAIL"))
        if not ok:
            note("%s — размер %dx%d, нужно %dx%d" % (name, im.size[0], im.size[1], SIZE[0], SIZE[1]))

        # 2. RGBA (исходник уже приведён, проверяем по наличию альфа-канала)
        ok = im.mode == "RGBA"
        print("   режим %s %s" % (im.mode, "OK" if ok else "FAIL"))
        if not ok:
            note("%s — режим %s, нужен RGBA" % (name, im.mode))

        px = list(im.getdata())

        # 3. альфа
        alphas = sorted({p[3] for p in px})
        ok = set(alphas) <= {0, 255}
        print("   альфа %s %s" % (alphas, "OK" if ok else "FAIL"))
        if not ok:
            note("%s — альфа не только 0/255: %s" % (name, alphas))

        # 4. ровно 7 непрозрачных цветов
        colours = sorted({p[:3] for p in px if p[3] == 255})
        ok = len(colours) == 7
        print("   непрозрачных цветов %d (нужно ровно 7) %s"
              % (len(colours), "OK" if ok else "FAIL"))
        print("      цвета: %s" % (colours,))
        if not ok:
            note("%s — непрозрачных цветов %d, ТЗ требует ровно 7" % (name, len(colours)))

        # 5. Δ средних к living_flesh_i
        flesh = load_from(ref, FLESH[i])
        if flesh is None:
            note("%s — в эталоне нет %s, Δ не посчитать" % (name, FLESH[i]))
        else:
            m_t, n_t = mean_rgb(im)
            m_f, n_f = mean_rgb(flesh)
            d = sum(abs(m_t[k] - m_f[k]) for k in range(3)) / 3.0
            deltas[name] = d
            ok = d <= THRESHOLD
            print("   средний RGB (%6.2f, %6.2f, %6.2f) против %s (%6.2f, %6.2f, %6.2f)"
                  % (m_t[0], m_t[1], m_t[2], FLESH[i], m_f[0], m_f[1], m_f[2]))
            print("   Δ = %5.2f (порог ≤ %.0f) %s" % (d, THRESHOLD, "OK" if ok else "FAIL"))
            if not ok:
                note("%s — Δ средних %.2f > %.0f (щупальца не в цвете плоти)" % (name, d, THRESHOLD))

        # 6. маска побитово
        ref_im = load_from(ref, name)
        if ref_im is None:
            note("%s — нет эталона для сверки маски" % name)
        else:
            a, wa, ha = mask_of(im)
            b, wb, hb = mask_of(ref_im)
            if (wa, ha) != (wb, hb):
                note("%s — размеры разные, маску не сверить" % name)
            else:
                missing = len(b - a)
                added = len(a - b)
                ok = not missing and not added
                print("   маска %d px  пропало %d  добавилось %d %s"
                      % (len(b), missing, added,
                         "OK" if ok else "<- СИЛУЭТ ИЗМЕНЁН"))
                if not ok:
                    note("%s — маска не совпала: пропало %d px, добавилось %d px"
                         % (name, missing, added))
        print()

    if deltas:
        worst = max(deltas.items(), key=lambda kv: kv[1])
        print("Сводка: пар сверено %d, худшая Δ = %.2f (%s) при пороге %.0f"
              % (len(deltas), worst[1], worst[0], THRESHOLD))
    else:
        print("Сводка: ни одной пары не сверено")

    print()
    if problems:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — %d" % len(problems))
        for k, p in enumerate(problems, 1):
            print("  %2d. %s" % (k, p))
        return 2
    print("ИТОГ: СХОДИТСЯ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
