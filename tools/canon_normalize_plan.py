#!/usr/bin/env python3
"""План нормализации файла канона: что ещё сломается, если его изменить.

Зачем. Ревизор и Интегратор после S78 предлагают поднять `detail_flow_01` на
+7,74 дБ в самом `.ogg` — это решает задачу целиком, в отличие от множителя
в JSON. Но файл канона не живёт один: на него ссылаются манифест и таблица
baseline/M. Тихая правка `.ogg` без пересчёта этих записей делает эталоне
приёмки неверным — тем самым способом, которым я уже один раз промахнулся
(S60: `SHA256SUMS_all.txt` дал 42 ложных расхождения).

Тест НЕ правит аудио. Он отвечает «что нужно обновить, если файл изменят»:

  * запись в `MANIFEST_canon_144.txt` (sha256 + размер);
  * запись в `baseline_master.json` — ЕСТЬ ЛИ ОНА ВООБЩЕ;
  * есть ли PCM-мастер, по которому можно пересчитать crest-эталон;
  * есть ли файл в пакете 3.7.3 и совпадает ли он с каноном.

Коды возврата: 0 — план построен и все звенья названы;
              2 — есть звено, которое нельзя пересчитать (нет мастера/записи);
              3 — не удалось прочитать исходные файлы.
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True,
                    help="путь внутри канона, напр. sounds/hive/detail_flow_01.ogg")
    ap.add_argument("--zip", default=None, help="пакет 3.7.3 (zip) для сверки")
    a = ap.parse_args(argv)

    rel = a.file.lstrip("/")
    canon = os.path.join(REPO, "03-sound", rel)
    if not os.path.isfile(canon):
        print("ОШИБКА: нет файла канона %s" % canon)
        return 3

    print("Файл: %s" % rel)
    print("  размер %d Б, sha256 %s" % (os.path.getsize(canon), sha256(canon)[:16] + "…"))

    need = []      # что обновить
    cant = []      # что пересчитать нечем

    # 1. Манифест канона
    man = os.path.join(REPO, "03-sound", "MANIFEST_canon_144.txt")
    entry = None
    if os.path.isfile(man):
        with open(man, encoding="utf-8") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) == 2 and parts[1] == rel:
                    entry = parts[0]
                    break
    if entry:
        print("  манифест канона: запись есть (sha %s…)" % entry[:16])
        need.append("MANIFEST_canon_144.txt — пересчитать sha256 (строка «%s»)" % rel)
    else:
        print("  X манифест канона: записи НЕТ")
        cant.append("манифест канона не содержит файл — сверить нечем")

    # 2. baseline_master.json
    bm = os.path.join(REPO, "03-sound", "baseline_master.json")
    rec = None
    if os.path.isfile(bm):
        data = json.load(open(bm, encoding="utf-8"))
        for r in data.get("files", []):
            if r.get("file") == rel:
                rec = r
                break
    if rec:
        print("  baseline_master: запись есть (crest_master %.3f, tolerance %.3f)"
              % (rec.get("crest_master", 0), rec.get("tolerance", 0)))
        need.append("baseline_master.json — пересчитать crest_master/repro_delta/"
                    "file_sha256/file_size и УБЕДИТЬСЯ, что delta_crest осталась "
                    "в допуске %.3f" % rec.get("tolerance", 0))
    else:
        print("  baseline_master: записи НЕТ (файл не в норме crest)")
        cant.append("нет записи в baseline_master — crest-эталон для этого файла "
                    "не задан, проверять после правки нечем")

    # 3. PCM-мастер
    stem = os.path.splitext(os.path.basename(rel))[0]
    masters = [os.path.join(dp, f) for dp, _, fs in os.walk(os.path.join(REPO, "03-sound", "masters"))
               for f in fs if os.path.splitext(f)[0] == stem]
    if masters:
        print("  PCM-мастер: %s" % os.path.relpath(masters[0], REPO))
        need.append("проверить Δcrest против мастера после перекодирования "
                    "(норма З-29: max(порог; baseline+0,05))")
    else:
        print("  X PCM-мастер: НЕТ")
        cant.append("нет PCM-мастера — после правки нечем подтвердить, что "
                    "перекодирование не изменило динамику")

    # 4. Пакет
    if a.zip and os.path.isfile(a.zip):
        try:
            with zipfile.ZipFile(a.zip) as z:
                inner = [n for n in z.namelist()
                         if n.endswith(os.path.basename(rel))]
                if inner:
                    same = z.read(inner[0]) == open(canon, "rb").read()
                    print("  пакет 3.7.3: файл есть, %s" %
                          ("совпадает с каноном" if same else "ОТЛИЧАЕТСЯ от канона"))
                    if not same:
                        need.append("пакет 3.7.3 — файл отличается от канона, "
                                    "пересобрать пакет")
                else:
                    print("  X пакет 3.7.3: файла нет")
                    cant.append("в пакете нет файла — после правки канона пакет "
                                "разойдётся с банком")
        except (OSError, zipfile.BadZipFile) as exc:
            print("  X пакет не прочитан: %s" % exc)
            cant.append("пакет не прочитан")
    else:
        print("  пакет: не проверялся (--zip не задан)")

    print()
    print("ЧТО ОБНОВИТЬ В ОДНОМ КОММИТЕ С ПРАВКОЙ:")
    for n in need:
        print("  · %s" % n)
    if cant:
        print()
        print("ЧЕГО ПЕРЕСЧИТАТЬ НЕЧЕМ:")
        for c in cant:
            print("  x %s" % c)
        print()
        print("ИТОГ: правка файла канона НЕ БУДЕТ ПРОВЕРЯЕМОЙ до появления "
              "недостающего звена")
        return 2
    print()
    print("ИТОГ: все звенья названы — правка возможна с пересчётом и проверкой")
    return 0


if __name__ == "__main__":
    sys.exit(main())
