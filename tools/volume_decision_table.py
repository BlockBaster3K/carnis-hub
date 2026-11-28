#!/usr/bin/env python3
"""Какой вариант громкости сэмпла ставит его В РЯД с остальными событиями.

Зачем. В S78 я назвал `volume 0.45` у `detail_flow_01` «намеренной частичной
компенсацией» — но это была оценка на глаз, а не измерение. Здесь считается
итоговый уровень каждого сэмпла ПОСЛЕ применения множителей и сравнивается
с группой однотипных событий. Тогда «в ряд» и «тише на N дБ» — числа.

Модель (та же, что в volume_effective_check):
    итоговый уровень сэмпла = измеренный RMS сэмпла + 20*log10(call_site * volume)

Код возврата: 0 — таблица построена; 3 — не удалось измерить (нет банка/библиотек).
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


def rms_db(path):
    data, _ = sf.read(path, dtype="float64")
    if data.ndim > 1:
        data = data.mean(axis=1)
    rms = float(np.sqrt(np.mean(data ** 2)))
    return 20.0 * np.log10(max(rms, 1e-12))


def find(bank, stem):
    for dp, _, fs in os.walk(bank):
        for f in fs:
            if f == stem + ".ogg":
                return os.path.join(dp, f)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="03-sound/sounds")
    ap.add_argument("--call-site", type=float, default=0.30,
                    help="громкость, которую передаёт код для detail-событий")
    ap.add_argument("--options", default="1.0,1.5,2.43",
                    help="МНОЖИТЕЛИ volume в sounds.json (не итоговые уровни!), через запятую")
    a = ap.parse_args(argv)

    if sf is None:
        print("ОШИБКА: нужны numpy и soundfile (pip install soundfile numpy)")
        return 3

    # Группа: остальные detail-события, у которых volume в JSON = 1.0
    others = ["detail_creak_01", "detail_membrane_01",
              "detail_bubbles_01", "detail_scuttle_01"]
    pair = ["detail_flow_01", "detail_flow_02"]
    raw = {}
    for stem in others + pair:
        p = find(a.bank, stem)
        if not p:
            print("ОШИБКА: не найден %s.ogg в %s" % (stem, a.bank))
            return 3
        raw[stem] = rms_db(p)

    def eff(stem, vol):
        return raw[stem] + 20.0 * np.log10(a.call_site * vol)

    group = [eff(s, 1.0) for s in others]
    g_mean = float(np.mean(group))
    g_lo, g_hi = min(group), max(group)

    print("Группа detail-событий при call-site %.2f и volume 1.0:" % a.call_site)
    for s, v in zip(others, group):
        print("   %-22s %7.1f dBFS" % (s, v))
    print("   разброс группы: %.1f … %.1f dBFS (полоса %.1f дБ)"
          % (g_lo, g_hi, g_hi - g_lo))
    print()

    options = [float(x) for x in a.options.split(",")]
    print("Пары hive.detail_flow — итоговый уровень при разных МНОЖИТЕЛЯХ")
    print("(volume в sounds.json перемножается с call-site %.2f):" % a.call_site)
    print("%-20s %10s %10s %12s %14s" %
          ("вариант", "flow_01", "flow_02", "разрыв пары", "flow_01 к группе"))
    for vol in options:
        e1 = eff("detail_flow_01", vol)
        e2 = eff("detail_flow_02", 1.0)      # flow_02 всегда 1.0
        print("%-20s %10.1f %10.1f %12.1f %+14.1f" %
              ("volume %.2f у _01" % vol, e1, e2, e2 - e1, e1 - g_mean))
    print()
    print("«Разрыв пары» — насколько _01 тише _02 внутри одного события.")
    print("«flow_01 к группе» — насколько _01 тише/громче среднего остальных")
    print("detail-событий; 0 означает «в ряд», отрицательное — тише.")

    best = min(options, key=lambda v: abs(eff("detail_flow_01", v) - g_mean))
    print()
    print("Ближе всего к остальным detail-событиям: volume %.2f "
          "(отклонение %+.1f дБ)" % (best, eff("detail_flow_01", best) - g_mean))
    print("Выбор между «разрывом пары» и «в ряд с группой» — акустическое решение,")
    print("а не арифметика: инструмент даёт числа, решение принимает Архитектор.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
