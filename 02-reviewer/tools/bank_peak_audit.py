#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bank_peak_audit.py — пики и запас банка: норма и единообразие (З-Г2).

Зачем. Гейт `accept_3.7.2.py` (блок 13) считает клиппингом только `peak >= 0 dBFS`,
то есть файл с пиком −0.01 dBFS он считает нормальным. Норма проекта другая:
**эффекты ≤ −1.00 dBFS**, а T-3140 ввела ещё и **запас ≥ 0.20 дБ** (пик ≤ −1.20).
Ни того, ни другого блок не проверяет: он видит только «больше нуля».

Что делает: декодирует каждый `.ogg` (PyAV или ffmpeg через `tools/timbre_check.py`),
печатает пик в dBFS, запас до 0 dBFS и запас до нормы −1.00 dBFS, отдельно
перечисляет файлы с запасом меньше порога.

Использование:
    python3 02-reviewer/tools/bank_peak_audit.py <каталог|zip> [--margin 0.20] [--norm -1.00]
                                                [--top 20] [--quiet]

Коды: 0 — все файлы не громче нормы и запас не меньше порога,
      2 — есть файлы с запасом меньше порога (норма при этом может соблюдаться),
      1 — ошибка запуска / нет декодера.
"""

import argparse
import os
import shutil
import sys
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))

try:
    import numpy as np
    import timbre_check as T
except Exception as exc:  # noqa: BLE001
    print("ОШИБКА: нужен numpy и tools/timbre_check.py (%s)" % exc)
    sys.exit(1)


def iter_ogg(src):
    if os.path.isdir(src):
        for dp, _d, fs in os.walk(src):
            for f in sorted(fs):
                if f.lower().endswith(".ogg"):
                    p = os.path.join(dp, f)
                    yield os.path.relpath(p, src), open(p, "rb").read()
    else:
        with zipfile.ZipFile(src) as z:
            for n in sorted(z.namelist()):
                if n.lower().endswith(".ogg"):
                    yield n.split("sounds/", 1)[-1], z.read(n)


def peak_dbfs(x):
    return 20.0 * np.log10(max(1e-9, float(np.max(np.abs(x.astype(np.float64))))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", default=os.path.join(REPO, "03-sound", "sounds"))
    ap.add_argument("--margin", type=float, default=0.20, help="требуемый запас, дБ")
    ap.add_argument("--norm", type=float, default=-1.00, help="норма пика, dBFS")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(a.src):
        print("ОШИБКА: нет такого пути: %s" % a.src)
        return 1

    rows, undecoded = [], []
    for rel, data in iter_ogg(a.src):
        if rel.startswith("archive"):
            continue
        x = T.decode(data)
        if x is None or len(x) == 0:
            undecoded.append(rel)
            continue
        rows.append((rel, peak_dbfs(x), len(x) / T.SR))
    if not rows:
        print("ОШИБКА: ни один файл не декодирован (нет PyAV/ffmpeg?) — это НЕ «ок»")
        return 1

    rows.sort(key=lambda r: -r[1])
    # «запас ≥ X дБ» читается как «пик на X дБ тише нормы»: peak <= norm − margin
    tight = [r for r in rows if r[1] > a.norm - a.margin]
    hard = [r for r in rows if r[1] > a.norm]

    print("Пики банка: %s" % a.src)
    print("Файлов: %d, не декодировано: %d" % (len(rows), len(undecoded)))
    print("Норма пика: ≤ %.2f dBFS; требуемый запас: %.2f дБ (то есть пик ≤ %.2f dBFS)"
          % (a.norm, a.margin, a.norm - a.margin))
    print()
    print("%-52s %8s %9s %9s" % ("файл", "пик", "запас", "до нормы"))
    print("-" * 82)
    for rel, pk, _dur in rows[:a.top]:
        print("%-52s %8.2f %9.2f %9.2f" % (rel, pk, -pk, a.norm - pk))
    print("-" * 82)
    print("Худший пик: %.2f dBFS (%s)" % (rows[0][1], rows[0][0]))
    print("Файлов громче нормы (%.2f): %d" % (a.norm, len(hard)))
    print("Файлов с запасом меньше %.2f дБ: %d" % (a.margin, len(tight)))
    for rel, pk, _d in tight:
        print("   %-52s %.2f" % (rel, pk))
    for rel in undecoded[:5]:
        print("   НЕ ДЕКОДИРОВАН: %s" % rel)
    print("-" * 82)
    if hard:
        print("ИТОГ: НОРМА ПИКА НАРУШЕНА — %d" % len(hard))
        return 2
    if tight:
        print("ИТОГ: норма соблюдена, единообразие запаса — нет (%d файлов)" % len(tight))
        return 2
    print("ИТОГ: ВСЁ В НОРМЕ — пики ≤ %.2f, запас ≥ %.2f дБ" % (a.norm, a.margin))
    return 0


if __name__ == "__main__":
    sys.exit(main())
