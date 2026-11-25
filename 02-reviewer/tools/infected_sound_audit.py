#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""infected_sound_audit.py — приёмка 132 звуков 33 существ (R11, волна 52).

Зачем отдельный чекер: гейт 3.8.0 блоком crest проверяет **только 15 файлов
из архива З-21** (дельта к оригиналам), а 132 новых файла S18 не проверяет
никто: у них нет «оригиналов», поэтому дельта неприменима, а абсолютная норма
(пик, клиппинг, тембр, единообразие внутри семейства) — не считается.

Что проверяется:
  1. комплект: 33 существа × 4 события (ambient/attack/hurt/death), лишних нет;
  2. имена файлов == именам реестра (`infected_<mob>_<event>_01.ogg`);
  3. пик ≤ нормы (по умолчанию −1.20 dBFS) — иначе провал; клиппинг (пик ≥ 0) — провал;
  4. тембр: спектральный центр в 200…8000 Гц, доля энергии < 80 Гц ≤ порога;
  5. единообразие: разброс RMS внутри семейства и разброс crest — в таблицу
     (для 3.8.0 это отчёт, для 3.8.1 — порог);
  6. фрагмент `sounds.json` (если задан): 132 события, каждое ссылается на
     существующий файл, ни одного файла без события.

Использование:
    python3 02-reviewer/tools/infected_sound_audit.py [--sounds-dir 03-sound/sounds] \\
            [--json 03-sound/3.8.0/sounds_json_infected_33.json] [--peak -1.20]

Код возврата: 0 — всё в норме, 2 — замечания, 1 — ошибка запуска.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))

import io

import numpy as np

try:
    from timbre_check import decode, metrics, seam_step_db  # PyAV-декодер проекта
except ImportError:
    decode = None


def analyze(path):
    """Метрики файла через PyAV-декодер проекта (тот же, что у гейта)."""
    with open(path, "rb") as f:
        x = decode(f.read())
    if x is None or not len(x):
        raise RuntimeError("не декодируется: %s" % path)
    dur, rms_db, frac_low, centroid = metrics(x)
    peak = float(np.max(np.abs(x)))
    peak_db = 20.0 * np.log10(peak) if peak > 0 else float("-inf")
    return {"dur": dur, "rms": rms_db, "peak_db": peak_db,
            "peak": peak, "crest": peak_db - rms_db,
            "centroid": centroid, "e80": frac_low / 100.0}

EVENTS = ("ambient", "attack", "hurt", "death")
PAT = re.compile(r"^infected_([a-z_]+)_(%s)_01$" % "|".join(EVENTS))
DB = lambda v: 20.0 * __import__("math").log10(v) if v > 0 else float("-inf")


def registry_names():
    """Имена 33 существ — из реестра Художника, раздел 5 (источник истины)."""
    path = os.path.join(REPO, "04-artist", "creature_registry.md")
    if not os.path.isfile(path):
        return None
    txt = open(path, encoding="utf-8").read()
    m = re.search(r"^##\s*5\..*$", txt, re.M)
    if not m:
        return None
    tail = txt[m.end():]
    nxt = re.search(r"^##\s", tail, re.M)
    if nxt:
        tail = tail[:nxt.start()]
    # Имя — первая ячейка строки таблицы: `| \`infected_blaze\` | ...`. Свободный
    # поиск `infected_[a-z_]+` ловит ещё и `infected_vanilla_mobs` из колонки
    # «Архив» и `..._glowmask` из колонки масок — проверено, 35 вместо 33.
    return sorted(set(re.findall(r"^\|\s*`?(infected_[a-z_]+)`?\s*\|", tail, re.M)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sounds-dir", default=os.path.join(REPO, "03-sound", "sounds"))
    ap.add_argument("--json", dest="json_path",
                    default=os.path.join(REPO, "03-sound", "3.8.0",
                                         "sounds_json_infected_33.json"))
    ap.add_argument("--peak", type=float, default=-1.20)
    ap.add_argument("--max-low80", type=float, default=2.0,
                    help="допустимая доля энергии < 80 Гц, %%")
    ap.add_argument("--rms-spread", type=float, default=6.0,
                    help="допустимый разброс RMS внутри семейства, дБ")
    a = ap.parse_args()

    if decode is None:
        print("ОШИБКА: не импортируется tools/timbre_check.py")
        return 1

    names = registry_names()
    if names:
        # в таблице реестра рядом с именем встречается `<имя>_glowmask.png` —
        # это не существо
        names = [n for n in names if not n.endswith("_glowmask")]
    if not names:
        print("ОШИБКА: нет раздела 5 в 04-artist/creature_registry.md")
        return 1

    ent = os.path.join(a.sounds_dir, "entity")
    have = {}
    for f in sorted(os.listdir(ent)):
        if not f.endswith(".ogg") or not f.startswith("infected_"):
            continue
        stem = f[:-4]
        m = PAT.match(stem)
        if not m:
            print("  \u2717 имя вне схемы: entity/%s" % f)
            continue
        have[("infected_" + m.group(1), m.group(2))] = os.path.join(ent, f)

    fails, warns = [], []
    bad = lambda s: (fails.append(s), print("  \u2717 " + s))
    warn = lambda s: (warns.append(s), print("  ! " + s))

    print("Банк: %s" % ent)
    print("Существ в реестре: %d, ожидается файлов: %d, найдено: %d\n"
          % (len(names), len(names) * len(EVENTS), len(have)))
    for n in names:
        miss = [e for e in EVENTS if (n, e) not in have]
        if miss:
            bad("%s: нет %s" % (n, ", ".join(miss)))
    extra = sorted(set(k[0] for k in have) - set(names))
    for e in extra:
        bad("%s: есть файлы, но существа нет в реестре" % e)

    per_fam = defaultdict(list)
    worst_peak = None
    rows = []
    for key in sorted(have):
        m = analyze(have[key])
        pk = m["peak_db"]
        fam = key[1]
        per_fam[fam].append((m["rms"], m["crest"], pk))
        rows.append((key[0], fam, m["dur"], m["rms"], pk, m["crest"],
                     m["centroid"], m["e80"] * 100))
        if worst_peak is None or pk > worst_peak[0]:
            worst_peak = (pk, key)
        if pk >= 0:
            bad("%s/%s: КЛИППИНГ (пик %.2f dBFS)" % (key[0], fam, pk))
        elif pk > a.peak:
            bad("%s/%s: пик %.2f dBFS громче нормы %.2f" % (key[0], fam, pk, a.peak))
        if not (200 <= m["centroid"] <= 8000):
            bad("%s/%s: центр %d Гц вне 200…8000" % (key[0], fam, m["centroid"]))
        if m["e80"] * 100 > a.max_low80:
            bad("%s/%s: низы < 80 Гц %.2f %% > %.2f %%"
                % (key[0], fam, m["e80"] * 100, a.max_low80))

    print("\n%-26s %-8s %6s %7s %7s %6s %7s %6s" %
          ("существо", "событие", "длит.", "RMS", "пик", "crest", "центр", "<80Гц"))
    print("-" * 78)
    for r in rows:
        print("%-26s %-8s %5.2fс %7.2f %7.2f %6.1f %6dГц %5.2f%%"
              % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))

    print("\nСемейства (единообразие):")
    for fam in EVENTS:
        v = per_fam.get(fam) or []
        if not v:
            continue
        rms = [x[0] for x in v]
        crest = [x[1] for x in v]
        pk = [x[2] for x in v]
        print("  %-8s файлов %3d | RMS %.1f…%.1f (разброс %.1f дБ) | "
              "crest %.1f…%.1f | пик %.2f…%.2f"
              % (fam, len(v), min(rms), max(rms), max(rms) - min(rms),
                 min(crest), max(crest), min(pk), max(pk)))
        if max(rms) - min(rms) > a.rms_spread:
            warn("%s: разброс RMS %.1f дБ > %.1f" % (fam, max(rms) - min(rms), a.rms_spread))

    # фрагмент sounds.json
    if a.json_path and os.path.isfile(a.json_path):
        doc = json.load(open(a.json_path, encoding="utf-8"))
        events = doc if isinstance(doc, dict) else {}
        refs = set()
        for ev, body in events.items():
            for s in (body.get("sounds") or []):
                nm = s if isinstance(s, str) else s.get("name")
                if nm:
                    refs.add(nm.split(":")[-1])
        files = {"entity/" + os.path.basename(p)[:-4] for p in have.values()}
        print("\nsounds.json: событий %d, ссылок на файлы %d, файлов в банке %d"
              % (len(events), len(refs), len(files)))
        for r in sorted(refs - files):
            bad("sounds.json ссылается в пустоту: %s" % r)
        for f in sorted(files - refs):
            bad("файл без события: %s" % f)
    else:
        warn("фрагмент sounds.json не найден — сверка событий не выполнена")

    print("\n" + "-" * 78)
    print("Файлов: %d, провалов: %d, предупреждений: %d, худший пик %.2f dBFS (%s/%s)"
          % (len(rows), len(fails), len(warns), worst_peak[0], worst_peak[1][0], worst_peak[1][1])
          if worst_peak else "Файлов: 0")
    if fails:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ")
        return 2
    print("ИТОГ: СХОДИТСЯ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
