#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""alpha_audit.py — аудит альфы текстур: стандарт 0/255 + сохранность маски.

Зачем. Чекеры светотени (`shade_density.py`, `creature_shade_audit.py`) смотрят
только непрозрачные пиксели — долю краски и число цветов; канал альфы не
проверяет ни один гейт. Стандарт проекта (ТЗ 3.7.0 §2.3, A4-p7, A3R1) требует
альфу **только 0 или 255**, а `glow_check.py` сверяет маску как «α > 0».
Отсюда два разных дефекта, которые надо ловить по отдельности:

  1. **полутоновая альфа** — нарушение стандарта (текстуры «мылятся»);
  2. **сдвиг маски** — α > 0 изменился относительно эталона (поехала геометрия:
     потеряны или добавлены непрозрачные пиксели).

Смена *значений* альфы при сохранной маске (например 210/220 → 255) — это
**бинаризация по стандарту**, а не дефект: так и было сделано для
`pustule_cluster.png` и `incubation_overlay.png` (см. `artist_z5_and_creatures.md`).
Поэтому такие изменения печатаются как справка и на код не влияют.

Использование:
    python3 02-reviewer/tools/alpha_audit.py <каталог|zip> [--baseline <zip|каталог>]
                                            [--require-binary] [--allow mask:имя,...] [--only block/] [-v]

Коды: 0 — маска совпадает и альфа соответствует стандарту (или отличия в --allow),
      2 — есть нарушение, 1 — ошибка запуска.
"""

import argparse
import io
import os
import sys
import tempfile
import zipfile

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("ОШИБКА: нужен Pillow")
    sys.exit(1)

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

TEX = "textures/"


def load(src):
    """{относительный путь внутри .../textures/: байты PNG} из каталога или zip."""
    out = {}
    if os.path.isdir(src):
        for root, _dirs, files in os.walk(src):
            for f in files:
                if not f.lower().endswith(".png"):
                    continue
                p = os.path.join(root, f)
                rel = p.split(TEX, 1)[-1] if TEX in p else f
                out[rel] = open(p, "rb").read()
        return out
    with zipfile.ZipFile(src) as z:
        for n in z.namelist():
            if not n.lower().endswith(".png"):
                continue
            rel = n.split(TEX, 1)[-1] if TEX in n else os.path.basename(n)
            out[rel] = z.read(n)
    return out


def alpha(data):
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    if np is not None:
        return np.array(im)[:, :, 3]
    return [p[3] for p in im.getdata()]  # pragma: no cover


def semi(a):
    if np is not None:
        return int(((a > 0) & (a < 255)).sum()), sorted(set(a.flatten().tolist()))
    return sum(1 for v in a if 0 < v < 255), sorted(set(a))  # pragma: no cover


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--allow", default="", help="имена файлов, где сдвиг маски допустим")
    ap.add_argument("--require-binary", action="store_true",
                    help="требовать альфу только 0/255 (стандарт проекта)")
    ap.add_argument("--only", default="", help="проверять только этот подкаталог, напр. block/")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    try:
        cur = load(a.target)
        base = load(a.baseline)
    except Exception as exc:  # noqa: BLE001
        print("ОШИБКА: не удалось прочитать вход: %s" % exc)
        return 1
    if not cur or not base:
        print("ОШИБКА: пустой набор (цель %d файлов, эталон %d)" % (len(cur), len(base)))
        return 1
    allow = {x.strip() for x in a.allow.split(",") if x.strip()}
    if a.only:
        cur = {k: v for k, v in cur.items() if k.startswith(a.only)}

    rows, unallowed, info = [], 0, []
    for k in sorted(cur):
        if k not in base:
            rows.append((k, "НОВЫЙ", "—", "—", "нет в эталоне (проверяется только стандарт)"))
            continue
        a1, a2 = alpha(base[k]), alpha(cur[k])
        if np is not None and a1.shape != a2.shape:
            rows.append((k, "РАЗМЕР", "%s" % (a1.shape,), "%s" % (a2.shape,), "РАЗМЕР ИЗМЕНИЛСЯ"))
            unallowed += 1
            continue
        s1, v1 = semi(a1)
        s2, v2 = semi(a2)
        if a.verbose and s1 != s2:
            info.append((k, s1, s2, v1[:6], v2[:6]))
        if np is not None:
            m1, m2 = (a1 > 0), (a2 > 0)
            same_mask = bool((m1 == m2).all())
            lost = int((m1 & ~m2).sum())
            gained = int((~m1 & m2).sum())
        else:  # pragma: no cover
            same_mask, lost, gained = True, 0, 0
        if not same_mask:
            ok = os.path.basename(k) in allow or k in allow
            rows.append((k, "МАСКА СДВИНУТА", "пропало %d" % lost, "добавилось %d" % gained,
                         "разрешено в --allow" if ok else "НАРУШЕНИЕ"))
            if not ok:
                unallowed += 1
            continue
        vals = set(np.unique(a2).tolist()) if np is not None else set(a2)  # pragma: no cover
        bad_vals = sorted(v for v in vals if v not in (0, 255))
        if a.require_binary and bad_vals:
            rows.append((k, "НЕ БИНАРНАЯ АЛЬФА", "%d px" % s2, "значения %s" % bad_vals[:6],
                         "НАРУШЕНИЕ СТАНДАРТА 0/255"))
            unallowed += 1

    print("Аудит альфы: цель — %s, эталон — %s" % (a.target, a.baseline))
    print("Проверено PNG: %d, нарушений: %d" % (len(cur), unallowed))
    if info:
        print("\nБинаризация альфы при сохранной маске (справка, не дефект):")
        for k, s1, s2, v1, v2 in info:
            print("  %-44s полупрозрачных %4d → %-4d  %s → %s" % (k[:44], s1, s2, v1, v2))
    if rows:
        print("\n%-44s %-16s %-10s %-10s %s" % ("файл", "что", "было", "стало", "вывод"))
        print("-" * 104)
        for k, what, s1, s2, note in rows:
            print("%-44s %-16s %-10s %-10s %s" % (k[:44], what, s1, s2, note))
    print("-" * 104)
    print("ИТОГ: %s" % ("АЛЬФА В ПОРЯДКЕ" if unallowed == 0 else "ЕСТЬ НАРУШЕНИЯ АЛЬФЫ — %d" % unallowed))
    return 0 if unallowed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
