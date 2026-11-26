#!/usr/bin/env python3
"""Громкость сэмплов внутри события: где одна цель на событие неверна.

Зачем. Схема спеки «одна цель на событие» вынуждает выравнивать множители всех
сэмплов события. Это верно, когда сэмплы равноценны, и НЕВЕРНО, когда они разной
громкости по природе: тогда выравнивание множителей сохраняет (и даже
подчёркивает) разницу в уровне, и пара звучит как «то есть звук, то нет».

Так и вышло с `hive.detail_flow`: `flow_01` тише пары на ~7.8 дБ, S17 назначил
ему 0.45 против 0.30, а спека с одной целью потребовала 0.30 обоим — то есть
отменила решение S17, выглядя при этом «зелёной».

Тест показывает числа, на которых такое решение должно приниматься:
пик и RMS каждого сэмпла, разброс внутри события, и во сколько раз множитель
тихого сэмпла должен отличаться от громкого, чтобы уровни сравнялись.

Код возврата: 0 — разброс внутри всех событий ≤ порога;
              2 — есть событие с разбросом > порога (нужны цели по сэмплам);
              3 — не удалось измерить (нет банка/библиотеки).
"""
import argparse
import os
import sys

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    np = None
    sf = None

DEFAULT_THRESHOLD_DB = 3.0


def db(x):
    return 20.0 * np.log10(max(float(x), 1e-12))


def measure(path):
    data, sr = sf.read(path, dtype="float64")
    if data.ndim > 1:
        data = data.mean(axis=1)
    return db(np.max(np.abs(data))), db(np.sqrt(np.mean(data ** 2))), len(data) / sr


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True, help="каталог sounds/ с .ogg")
    ap.add_argument("--events", nargs="*", default=None,
                    help="события как префиксы имён файлов; по умолчанию — все detail_*")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD_DB)
    a = ap.parse_args(argv)

    if sf is None:
        print("ОШИБКА: нужны numpy и soundfile (pip install soundfile numpy)")
        return 3
    if not os.path.isdir(a.bank):
        print("ОШИБКА: нет каталога банка %s" % a.bank)
        return 3

    groups = {}
    for dp, _, fs in os.walk(a.bank):
        for f in fs:
            if not f.endswith(".ogg"):
                continue
            stem = f[:-4]
            if a.events and not any(stem.startswith(p) for p in a.events):
                continue
            groups.setdefault(stem, os.path.join(dp, f))

    if not groups:
        print("ОШИБКА: не найдено ни одного .ogg по заданным префиксам")
        return 3
    if not a.events and not any(k.startswith("detail_") for k in groups):
        # Без --events и без detail_* в банке раньше возвращалось «не найдено»,
        # то есть инструмент молча отказывался работать на чужом банке
        # (например sounds_380). Теперь меряет весь банк.
        print("банк без detail_*-сэмплов — меряю все %d файлов\n" % len(groups))

    bad = 0
    print("%-40s %9s %9s %8s" % ("сэмпл", "пик dBFS", "RMS dBFS", "длит, с"))
    rows = []
    for stem in sorted(groups):
        peak, rms, dur = measure(groups[stem])
        rows.append((stem, peak, rms, dur))
        print("%-40s %9.1f %9.1f %8.2f" % (stem, peak, rms, dur))

    # группируем по событию: detail_flow_01 / detail_flow_02 -> detail_flow
    events = {}
    for stem, peak, rms, dur in rows:
        base = stem.rsplit("_", 1)[0] if stem.rsplit("_", 1)[-1].isdigit() else stem
        events.setdefault(base, []).append((stem, peak, rms))

    print()
    for base in sorted(events):
        items = events[base]
        if len(items) < 2:
            continue
        lo = min(items, key=lambda t: t[2])      # самый тихий по RMS
        hi = max(items, key=lambda t: t[2])
        spread = hi[2] - lo[2]
        factor = 10 ** (spread / 20.0)
        status = "ok" if spread <= a.threshold else "РАЗБРОС"
        if spread > a.threshold:
            bad += 1
        print("%-22s разброс RMS %.1f дБ -> %s" % (base, spread, status))
        print("      тихий %s (%.1f), громкий %s (%.1f)"
              % (lo[0], lo[2], hi[0], hi[2]))
        if spread > a.threshold:
            print("      чтобы уровни сравнялись, множитель тихого должен быть "
                  "в %.2fx больше: одна цель на событие даст слышимый провал" % factor)

    print()
    if bad:
        print("ИТОГ: у %d событий разброс > %.1f дБ — нужны цели ПО СЭМПЛАМ "
              "(targets_by_sample), одна цель на событие неверна" % (bad, a.threshold))
        return 2
    print("ИТОГ: разброс внутри событий в пределах %.1f дБ — одна цель годится"
          % a.threshold)
    return 0


if __name__ == "__main__":
    sys.exit(main())
