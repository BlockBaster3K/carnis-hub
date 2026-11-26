#!/usr/bin/env python3
"""T-3128 системно: найти файлы, которые тише СВОИХ СОСЕДЕЙ, а не «тише числа».

Почему так. Задача T-3128 поднимала «тихие файлы» и пропустила два:
`detail_flow_01` (−29.57) и `hive_spawn_idle_01` (−29.09). Отбор шёл по
абсолютному порогу «тише −30.2 дБ», и оба в него не попали — а они тише
соседей по своему семейству на **7.7 и 7.1 дБ**, то есть слышимо проваливаются
при случайном выборе варианта.

Абсолютный порог тут неверен по существу: у каждой категории свой уровень
(медианы `entity` −17.9, `hive` −18.8, `amb` −20.8), поэтому «тихо» — это
свойство ОТНОСИТЕЛЬНО семейства, а не число dBFS.

Проверка:
  * семейство = каталог + имя без хвоста `_NN`;
  * для семейства из ≥2 файлов считается медиана RMS;
  * файл тише медианы больше чем на --gap (по умолчанию 6 дБ) — находка.

Коды: 0 — таких файлов нет; 2 — есть (печатает); 3 — банк не прочитан.
"""
import argparse
import collections
import os
import re
import sys

GAP_DEFAULT = 6.0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True)
    ap.add_argument("--gap", type=float, default=GAP_DEFAULT)
    ap.add_argument("--json", action="store_true", dest="json_out")
    a = ap.parse_args(argv)

    try:
        import numpy as np
        import soundfile as sf
    except ImportError as exc:
        print("ОШИБКА: нет %s — НЕ ПРОВЕРЕНО (это не «чисто»)." % exc.name)
        return 3
    if not os.path.isdir(a.bank):
        print("ОШИБКА: банка %s нет — НЕ ПРОВЕРЕНО." % a.bank)
        return 3

    lev = {}
    for dp, _, fs in os.walk(a.bank):
        for f in sorted(fs):
            if not f.lower().endswith(".ogg"):
                continue
            p = os.path.join(dp, f)
            x, _ = sf.read(p, dtype="float64", always_2d=False)
            if x.ndim > 1:
                x = x.max(axis=1)
            if x.size == 0:
                continue
            lev[os.path.relpath(p, a.bank)[:-4]] = (
                20 * __import__("math").log10(float(np.sqrt((x ** 2).mean()))))
    if not lev:
        print("ОШИБКА: в %s нет .ogg — НЕ ПРОВЕРЕНО." % a.bank)
        return 3

    fam = collections.defaultdict(list)
    for k, v in lev.items():
        base = os.path.basename(k)
        m = re.match(r"^(.*?)_(\d+)(?:_[a-z]+)?$", base)
        fam[(os.path.dirname(k), m.group(1) if m else base)].append((v, k))

    found, checked = [], 0
    for (d, pref), items in sorted(fam.items()):
        if len(items) < 2:
            continue
        checked += 1
        vals = sorted(v for v, _ in items)
        med = vals[len(vals) // 2]
        for v, k in items:
            if med - v > a.gap:
                found.append({"file": k, "rms": round(v, 2),
                              "family_median": round(med, 2),
                              "gap": round(med - v, 2), "size": len(items)})
    found.sort(key=lambda r: -r["gap"])

    print("банк: %s — файлов %d, семейств из 2+ файлов: %d, порог %.1f дБ"
          % (a.bank, len(lev), checked, a.gap))
    print()
    if found:
        print("ТИШЕ СОСЕДЕЙ (это и есть провал, который ищет T-3128): %d"
              % len(found))
        for r in found:
            print("  %-38s %7.2f  медиана семейства %6.2f  разрыв %5.2f дБ  "
                  "(в семействе %d)" % (r["file"], r["rms"],
                                        r["family_median"], r["gap"],
                                        r["size"]))
    else:
        print("файлов, тише соседей больше чем на %.1f дБ: 0" % a.gap)
    if a.json_out:
        import json
        print(json.dumps({"bank": a.bank, "files": len(lev),
                          "families": checked, "found": found},
                         ensure_ascii=False, indent=1))
    print()
    if found:
        print("ИТОГ: %d файлов проваливаются относительно соседей — код 2"
              % len(found))
        print("  лечение: выравнивание ключом volume в sounds.json (банк не")
        print("  перекодируется), а НЕ подъёмом файла: подъём меняет crest и")
        print("  требует мастеров, которых у канона нет (129 из 144).")
        return 2
    print("ИТОГ: относительно-тихих файлов нет — код 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
