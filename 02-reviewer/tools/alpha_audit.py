#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""alpha_audit.py — аудит АЛЬФЫ текстур против эталона (находка З-12/З-13).

Зачем: чекеры светотени (`shade_density.py`, `creature_shade_audit.py`) смотрят
только непрозрачные пиксели — долю краски и число цветов. Полупрозрачные края
при этом не проверяются вообще, поэтому «схлопнутая» альфа (полупрозрачные
пиксели стали полностью непрозрачными) проходит все гейты молча.
Так в 3.7.2 ушли `pustule_cluster.png` (192 px) и `incubation_overlay.png` (683 px).

Что сравнивает: канал альфы каждого PNG текущего набора с одноимённым файлом
эталона. Сообщает, сколько полупрозрачных пикселей было и стало, и наборы
значений альфы. Байты RGB не важны — перекраска разрешена, деградация кромки нет.

Использование:
    python3 02-reviewer/tools/alpha_audit.py <каталог|zip> --baseline <zip|каталог>
                                            [--allow pustule_cluster.png,...] [-v]

Коды: 0 — альфа совпадает везде (или отличия только в разрешённом списке),
      2 — есть неразрешённые отличия, 1 — ошибка запуска.
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
    ap.add_argument("--allow", default="", help="имена файлов, где отличие допустимо")
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

    rows, unallowed = [], 0
    for k in sorted(cur):
        if k not in base:
            rows.append((k, "НОВЫЙ", "—", "—", "нет в эталоне"))
            continue
        a1, a2 = alpha(base[k]), alpha(cur[k])
        if np is not None and a1.shape != a2.shape:
            rows.append((k, "РАЗМЕР", "%s" % (a1.shape,), "%s" % (a2.shape,), "размер изменился"))
            unallowed += 1
            continue
        if np is not None and (a1 == a2).all():
            continue
        if np is None and a1 == a2:  # pragma: no cover
            continue
        s1, v1 = semi(a1)
        s2, v2 = semi(a2)
        ok = os.path.basename(k) in allow or k in allow
        rows.append((k, "альфа изменена", "%d px" % s1, "%d px" % s2,
                     ("разрешено" if ok else "НАРУШЕНИЕ") + (" | %s → %s" % (v1[:6], v2[:6]) if a.verbose else "")))
        if not ok:
            unallowed += 1

    print("Аудит альфы: цель — %s, эталон — %s" % (a.target, a.baseline))
    print("Проверено PNG: %d, отличий: %d, неразрешённых: %d" % (len(cur), len(rows), unallowed))
    if rows:
        print("\n%-44s %-16s %-10s %-10s %s" % ("файл", "что", "было", "стало", "вывод"))
        print("-" * 104)
        for k, what, s1, s2, note in rows:
            print("%-44s %-16s %-10s %-10s %s" % (k[:44], what, s1, s2, note))
    print("-" * 104)
    print("ИТОГ: %s" % ("АЛЬФА СХОДИТСЯ" if unallowed == 0 else "ЕСТЬ НЕРАЗРЕШЁННЫЕ ИЗМЕНЕНИЯ АЛЬФЫ — %d" % unallowed))
    return 0 if unallowed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
