#!/usr/bin/env python3
"""Норма «моно» для банка звука (S100 волны 58).

Зачем: звук идёт в позиционный движок с окклюзией (Sound Physics Remastered,
мягкая интеграция — код GPL-3.0 не копируем и не делаем обязательным).
Позиционирование и окклюзию считает движок, поэтому **файл обязан быть
одноканальным**: стерео в 3D-звуке — двойное позиционирование, движок панорамирует
то, что уже панорамировано, и окклюзия перестаёт совпадать с геометрией.

Норма: каждый .ogg банка — 1 канал, 44.1 кГц. Любое отклонение — брак.

Коды возврата:
  0 — все файлы моно (и нужная частота)
  2 — есть отклонения (печатает список)
  3 — банк/декодер недоступны (fail-closed: не «чисто», а «не проверено»)
"""
import argparse
import collections
import json
import os
import sys

EXPECTED_SR = 44100


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", action="append", required=True,
                    help="каталог банка; можно несколько раз")
    ap.add_argument("--sr", type=int, default=EXPECTED_SR)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    try:
        import soundfile as sf
    except ImportError:
        print("ОШИБКА: нет soundfile — каналы не проверить. Это НЕ «чисто».")
        return 3

    total = 0
    bad = []
    stats = collections.Counter()
    for bank in a.bank:
        if not os.path.isdir(bank):
            print("ОШИБКА: банк %s отсутствует" % bank)
            return 3
        found = 0
        for dp, _, fs in os.walk(bank):
            for f in sorted(fs):
                if not f.endswith(".ogg"):
                    continue
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, bank)
                found += 1
                total += 1
                try:
                    info = sf.info(p)
                except Exception as exc:
                    bad.append((bank, rel, "НЕ ДЕКОДИРУЕТСЯ", str(exc)[:60]))
                    continue
                stats[(info.channels, info.samplerate)] += 1
                if info.channels != 1:
                    bad.append((bank, rel, "%d каналов" % info.channels,
                                "стерео/многоканальный — брак для 3D-звука"))
                elif info.samplerate != a.sr:
                    bad.append((bank, rel, "SR %d Гц" % info.samplerate,
                                "ожидалось %d Гц" % a.sr))
        print("%-34s файлов: %d" % (os.path.basename(os.path.normpath(bank)), found))

    print()
    print("распределение (каналы, Гц): %s"
          % ", ".join("%dx%d: %d" % (c, s, n) for (c, s), n in sorted(stats.items())))
    print()
    if a.json:
        print(json.dumps({"total": total, "bad": bad,
                          "stats": [{"channels": c, "sr": s, "n": n}
                                    for (c, s), n in sorted(stats.items())]},
                         ensure_ascii=False))
    if bad:
        print("ОТКЛОНЕНИЯ ОТ НОРМЫ «МОНО»: %d" % len(bad))
        for bank, rel, what, why in bad:
            print("  %s/%s — %s (%s)" % (os.path.basename(bank.rstrip("/")), rel, what, why))
        return 2
    print("ИТОГ: все %d файлов моно, %d Гц — норма соблюдена" % (total, a.sr))
    return 0


if __name__ == "__main__":
    sys.exit(main())
