#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crest_delta.py — сверка crest-фактора (Peak − RMS) между архивом оригиналов и банком.

Зачем: правка громкости/тембра по ТЗ банка обязана сохранять crest
(**Δ ≤ 0,05 дБ**, см. `03-sound/CARNIS_Wave18B_SilenceRepair.md` и приёмку
T-3130). Чистое изменение усиления сдвигает пик и RMS одинаково и crest
**не меняет**; если Δ вылезло — значит изменилась динамика (лимитер,
перекодирование, VBR), а не только уровень. Ни гейт, ни мой прежний
чек-лист этого не мерили (З-21, находка Звука, проверено Ревизором).

Использование:
    python3 02-reviewer/tools/crest_delta.py <архив оригиналов> <банк|пакет> \\
            [--tol 0.05] [--top 20]

Код возврата: 0 — все в допуске, 2 — есть выходы за допуск, 1 — ошибка запуска.
"""

import argparse
import io
import math
import os
import pathlib
import sys
import zipfile

try:
    import av
    import numpy as np
except ImportError as e:  # pragma: no cover
    print("ОШИБКА: нужны PyAV и numpy (%s)" % e)
    sys.exit(1)


def crest_of_bytes(data):
    """crest = peak − RMS в дБ по декодированному сигналу (усиление не влияет)."""
    c = av.open(io.BytesIO(data))
    st = c.streams.audio[0]
    chunks = [fr.to_ndarray().astype("float64").ravel() for fr in c.decode(st)]
    c.close()
    if not chunks:
        return None
    x = np.concatenate(chunks)
    peak = float(np.abs(x).max())
    if peak <= 0:
        return None
    rms = float(math.sqrt((x ** 2).mean()))
    if rms <= 0:
        return None
    return 20 * math.log10(peak) - 20 * math.log10(rms)


def load_target(src):
    """Банк — каталог с .ogg; пакет — zip с sounds/**/*.ogg. Возвращает {имя: bytes-функция}."""
    p = pathlib.Path(src)
    if p.is_dir():
        return {f.name: (lambda f=f: f.read_bytes()) for f in p.rglob("*.ogg")}
    if p.suffix.lower() == ".zip":
        z = zipfile.ZipFile(p)
        return {n.split("/")[-1]: (lambda n=n: z.read(n))
                for n in z.namelist()
                if n.endswith(".ogg") and "/sounds/" in n}
    raise SystemExit("ОШИБКА: %s — не каталог и не zip" % src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", help="каталог оригиналов (.ogg), например 03-sound/archive_zapas_2026-11-26")
    ap.add_argument("target", help="банк (каталог) или пакет (zip)")
    ap.add_argument("--tol", type=float, default=0.05, help="допуск |Δ|, дБ (по умолчанию 0,05)")
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args()

    arch = pathlib.Path(a.archive)
    if not arch.is_dir():
        print("ОШИБКА: нет каталога архива %s" % a.archive)
        return 1
    originals = sorted(arch.glob("*.ogg"))
    if not originals:
        print("ОШИБКА: в архиве нет .ogg")
        return 1
    target = load_target(a.target)

    rows, missing = [], []
    for f in originals:
        get = target.get(f.name)
        if get is None:
            missing.append(f.name)
            continue
        old, new = crest_of_bytes(f.read_bytes()), crest_of_bytes(get())
        if old is None or new is None:
            missing.append(f.name + " (не декодирован)")
            continue
        rows.append((f.name, old, new, new - old))

    rows.sort(key=lambda r: -abs(r[3]))
    print("%-40s %10s %11s %7s" % ("файл", "crest было", "crest стало", "Δ дБ"))
    for name, o, n, d in rows[:a.top]:
        mark = "  " if abs(d) <= a.tol else " !"
        print("%-40s %10.2f %11.2f %7.2f%s" % (name, o, n, d, mark))

    over = [r for r in rows if abs(r[3]) > a.tol]
    diffs = sorted(abs(r[3]) for r in rows)
    median = diffs[len(diffs) // 2] if diffs else 0.0
    print("-" * 72)
    print("Файлов сверено: %d, выходов за %.2f дБ: %d, медиана |Δ| %.3f дБ, максимум %.2f дБ"
          % (len(rows), a.tol, len(over), median, max(diffs) if diffs else 0.0))
    if missing:
        print("Не сверено: %d — %s" % (len(missing), ", ".join(missing[:5])))
    if over:
        print("ИТОГ: ЕСТЬ ВЫХОДЫ — %d файлов изменили динамику, а не только уровень" % len(over))
        for name, _o, _n, d in over:
            print("   ! %-38s %+.2f дБ" % (name, d))
        return 2
    print("ИТОГ: СХОДИТСЯ — crest сохранён в пределах %.2f дБ" % a.tol)
    return 0


if __name__ == "__main__":
    sys.exit(main())
