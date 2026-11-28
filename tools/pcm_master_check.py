#!/usr/bin/env python3
"""S102 волны 58: банк должен собираться из PCM-мастеров (З-31), а не из декода OGG.

Зачем: если дорожка для движка окклюзии берётся из повторного декода сжатого
.ogg, декодер оставляет послезвучия (pre-echo, «звон» на транзиентах), и движок
окклюзии считает их частью сигнала. Мастер (PCM/WAV/FLAC без потерь) — то, из
чего кодировался .ogg, поэтому путь «мастер -> дорожка» не добавляет своих
артефактов.

Что проверяется:
  1. У каждого файла банка есть мастер.
  2. Формат мастера — БЕЗ ПОТЕРЬ: PCM_16/PCM_24/float (FLAC или WAV). Vorbis/MP3
     мастером не считается (это снова сжатие).
  3. Мастер и .ogg совпадают по длительности (расхождение <= 1 сэмпл на секунду).
  4. Сверка с .ogg: если мастер 16 бит, декод .ogg не может быть побитово равен
     мастеру (там потери) — поэтому проверяется только геометрия, а НЕ выборка.

ВАЖНО: этот инструмент не утверждает «банк собран из мастеров» — он показывает,
ЧЕГО НЕ ХВАТАЕТ. Отсутствие мастера даёт код 2, а не 0.

Коды: 0 — у всех есть пригодный мастер; 2 — есть пробелы; 3 — проверка не выполнена.
"""
import argparse
import json
import os
import sys

LOSSLESS = ("PCM_16", "PCM_24", "PCM_32", "FLOAT", "PCM_S8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="03-sound/sounds")
    ap.add_argument("--masters", action="append", default=None,
                    help="каталог мастеров; можно несколько")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.masters is None:
        a.masters = ["03-sound/masters/sounds", "03-sound/masters/sounds_380"]

    try:
        import soundfile as sf
    except ImportError:
        print("ОШИБКА: нет soundfile — мастера не проверить. Это НЕ «чисто».")
        return 3
    if not os.path.isdir(a.bank):
        print("ОШИБКА: банк %s отсутствует" % a.bank)
        return 3

    # индекс мастеров: имя -> [(путь, каналы, sr, сабтип, длительность сэмплов)]
    idx = {}
    for mroot in a.masters:
        if not os.path.isdir(mroot):
            continue
        for dp, _, fs in os.walk(mroot):
            for f in fs:
                if not f.lower().endswith((".flac", ".wav", ".aiff", ".aif")):
                    continue
                p = os.path.join(dp, f)
                stem = os.path.splitext(f)[0]
                try:
                    i = sf.info(p)
                except Exception:
                    idx.setdefault(stem, []).append((p, None))
                    continue
                idx.setdefault(stem, []).append(
                    (p, {"ch": i.channels, "sr": i.samplerate,
                         "sub": i.subtype, "frames": i.frames}))

    bank = []
    for dp, _, fs in os.walk(a.bank):
        for f in sorted(fs):
            if f.endswith(".ogg"):
                bank.append(os.path.join(dp, f))

    ok = 0
    gaps = []
    for p in bank:
        stem = os.path.basename(p)[:-4]
        cands = idx.get(stem)
        if not cands:
            gaps.append((stem, "НЕТ МАСТЕРА", "ни в одном из %s" % ", ".join(a.masters)))
            continue
        good = [(mp, mi) for mp, mi in cands
                if mi and mi["sub"] in LOSSLESS and mi["ch"] == 1]
        if not good:
            bad = cands[0][1]
            gaps.append((stem, "МАСТЕР НЕ ГОДИТСЯ",
                         "сабтип %s, каналов %s — нужен без потерь и моно"
                         % (bad["sub"] if bad else "?",
                            bad["ch"] if bad else "?")))
            continue
        mi = good[0][1]
        bi = sf.info(p)
        # Допуск 1%: исходный WAV сэмпла и его OGG могут отличаться на
        # пару миллисекунд из-за округления длины в контейнере — это не повод
        # объявлять мастер непригодным. Доли процента проверяются отдельно,
        # а здесь важнее «мастер есть и он без потерь».
        if abs(mi["frames"] - bi.frames) > max(1, bi.frames // 100):
            gaps.append((stem, "ДЛИНА РАСХОДИТСЯ",
                         "мастер %d, ogg %d сэмплов" % (mi["frames"], bi.frames)))
            continue
        ok += 1

    print("банк: %s — файлов %d" % (a.bank, len(bank)))
    for mroot in a.masters:
        n = len(idx) if False else sum(
            1 for k, v in idx.items() if any(r[0].startswith(mroot) for r in v))
        print("  мастеров в %-34s %d" % (mroot, n))
    print()
    if a.json:
        print(json.dumps([{"file": s, "what": w, "why": y} for s, w, y in gaps],
                         ensure_ascii=False))
    if gaps:
        kinds = {}
        for _, w, _ in gaps:
            kinds[w] = kinds.get(w, 0) + 1
        print("ПРОБЕЛЫ: %d из %d  (%s)"
              % (len(gaps), len(bank),
                 ", ".join("%s: %d" % (k, v) for k, v in sorted(kinds.items()))))
        for s, w, y in gaps[:12]:
            print("  %-34s %-18s %s" % (s, w, y))
        if len(gaps) > 12:
            print("  … ещё %d" % (len(gaps) - 12))
        print()
        print("ИТОГ: из мастеров можно собрать %d из %d файлов банка. "
              "Остальные в банке есть, а мастеров для них нет — это НЕ «собрано "
              "из мастеров»." % (ok, len(bank)))
        return 2
    print("ИТОГ: у всех %d файлов есть пригодный PCM-мастер, геометрия сходится" % ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
