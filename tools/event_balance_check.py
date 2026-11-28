#!/usr/bin/env python3
"""Разброс громкости ВНУТРИ события — тремя метриками, чтобы не путать замысел с дефектом.

Зачем три метрики. Норма «сэмплы одного события не должны расходиться больше 3 дБ»
записана без указания, чем мерить. Если мерить сырым RMS, в провал попадают
события, где расхождение — не дефект, а следствие crest-фактора:

  combat.flesh_hit: RMS 4.63 дБ, пик 1.12 дБ, A-взвеш. 2.17 дБ.
  У всех трёх сэмплов пик выровнен (-1.47/-1.97/-2.60), а RMS разный потому,
  что _03 короче (0.51 с против 0.61) и плотнее по энергии.

Обратный случай тоже есть: hive.spawn_hurt_critical даёт RMS 1.01 дБ, а
A-взвеш. 5.38 дБ — то есть по RMS «ровно», а на слух расходится, потому что
разница в спектре, а не в уровне.

Поэтому:
  * пик — техническая норма (пики обязаны быть ровными: это запас до клиппинга);
  * A-взвеш. RMS — ВОСПРИНИМАЕМАЯ громкость, по ней и надо выравнивать;
  * сырой RMS — справка, НЕ критерий (иначе чинится не то).

Коды: 0 — все события в норме; 2 — есть выход за норму; 3 — не проверено
(нет пакета/банка/декодера — это НЕ «чисто»).
"""
import argparse
import json
import math
import os
import sys
import zipfile

TOL_DB = 3.0        # норма расхождения внутри события
CEIL_DB = -1.20     # потолок пика (T-3182 §1)


def a_weight(x, sr):
    import numpy as np
    from scipy.signal import bilinear, lfilter
    f1, f2, f3, f4 = 20.598997, 107.65265, 737.86223, 12194.217
    a1000 = 1.9997
    num = [(2 * np.pi * f4) ** 2 * a1000, 0, 0, 0, 0]
    den = np.polymul([1, 4 * np.pi * f4, (2 * np.pi * f4) ** 2],
                     [1, 4 * np.pi * f1, (2 * np.pi * f1) ** 2])
    den = np.polymul(np.polymul(den, [1, 2 * np.pi * f3]), [1, 2 * np.pi * f2])
    b, a = bilinear(num, den, fs=sr)
    return lfilter(b, a, x)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", required=True, help="ZIP-пакет с sounds.json")
    ap.add_argument("--bank", action="append", required=True)
    ap.add_argument("--json", action="store_true", dest="json_out")
    a = ap.parse_args(argv)

    try:
        import numpy as np
        import soundfile as sf
        import scipy  # noqa: F401
    except ImportError as exc:
        print("ОШИБКА: нет %s — разброс НЕ ПРОВЕРЕН (это не «чисто»)." % exc.name)
        return 3
    if not os.path.isfile(a.pkg):
        print("ОШИБКА: пакета %s нет — НЕ ПРОВЕРЕНО." % a.pkg)
        return 3
    for b in a.bank:
        if not os.path.isdir(b):
            print("ОШИБКА: банка %s нет — НЕ ПРОВЕРЕНО." % b)
            return 3

    z = zipfile.ZipFile(a.pkg)
    names = [n for n in z.namelist() if n.endswith("sounds.json")]
    if not names:
        print("ОШИБКА: в пакете нет sounds.json — НЕ ПРОВЕРЕНО.")
        return 3
    d = json.loads(z.read(names[0]))

    cache = {}

    def levels(name):
        key = name.split(":")[-1]
        if key in cache:
            return cache[key]
        for b in a.bank:
            p = os.path.join(b, key + ".ogg")
            if os.path.isfile(p):
                x, sr = sf.read(p, dtype="float64", always_2d=False)
                if x.ndim > 1:
                    x = x.max(axis=1)
                rms = 20 * math.log10(float(np.sqrt((x ** 2).mean())) + 1e-12)
                pk = 20 * math.log10(float(np.abs(x).max()) + 1e-12)
                arms = 20 * math.log10(float(np.sqrt((a_weight(x, sr) ** 2).mean()))
                                       + 1e-12)
                cache[key] = (rms, pk, arms, len(x) / float(sr))
                return cache[key]
        cache[key] = None
        return None

    rows, missing = [], []
    for ev, v in sorted(d.items()):
        lv = []
        for s in v.get("sounds", []):
            nm = s["name"] if isinstance(s, dict) else s
            vol = s.get("volume", 1.0) if isinstance(s, dict) else 1.0
            g = 20 * math.log10(vol) if vol and vol > 0 else 0.0
            r = levels(nm)
            if r is None:
                missing.append((ev, nm))
                continue
            lv.append((r[0] + g, r[1] + g, r[2] + g, r[3], nm.split("/")[-1]))
        if len(lv) < 2:
            continue
        rows.append({
            "event": ev, "n": len(lv),
            "rms": max(t[0] for t in lv) - min(t[0] for t in lv),
            "peak": max(t[1] for t in lv) - min(t[1] for t in lv),
            "aw": max(t[2] for t in lv) - min(t[2] for t in lv),
            "samples": [{"name": t[4], "rms": t[0], "peak": t[1], "aw": t[2],
                         "dur": t[3]} for t in sorted(lv)],
        })

    bad_aw = [r for r in rows if r["aw"] > TOL_DB]
    bad_pk = [r for r in rows if r["peak"] > TOL_DB]

    print("событий с >=2 сэмплами: %d" % len(rows))
    if missing:
        print("сэмплов без файла: %d (это провал, не пропуск)" % len(missing))
    print()
    print("по ВОСПРИНИМАЕМОЙ громкости (A-взвеш.) вне %.1f дБ: %d" % (TOL_DB, len(bad_aw)))
    for r in sorted(bad_aw, key=lambda t: -t["aw"]):
        print("  %-32s A %5.2f дБ (RMS %5.2f, пик %5.2f)"
              % (r["event"], r["aw"], r["rms"], r["peak"]))
        for s in r["samples"]:
            print("      %-34s A %7.2f  RMS %7.2f  пик %6.2f  %.2f с"
                  % (s["name"], s["aw"], s["rms"], s["peak"], s["dur"]))
    print()
    print("по ПИКУ вне %.1f дБ: %d" % (TOL_DB, len(bad_pk)))
    for r in sorted(bad_pk, key=lambda t: -t["peak"]):
        print("  %-32s пик %5.2f дБ" % (r["event"], r["peak"]))
    over = [(r["event"], s["name"], s["peak"]) for r in rows for s in r["samples"]
            if s["peak"] > CEIL_DB]
    print()
    print("сэмплов с пиком выше %.2f dBFS: %d" % (CEIL_DB, len(over)))
    for ev, nm, pk in over:
        print("  %-32s %-28s %+.2f" % (ev, nm, pk))

    if a.json_out:
        print(json.dumps({"events": len(rows), "bad_aw": bad_aw, "bad_peak": bad_pk,
                          "over_ceiling": over}, ensure_ascii=False, indent=1))
    problems = len(bad_aw) + len(bad_pk) + len(over) + len(missing)
    if problems:
        print("\nИТОГ: отклонений %d — код 2" % problems)
        return 2
    print("\nИТОГ: все %d событий ровны по обеим метрикам — код 0" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
