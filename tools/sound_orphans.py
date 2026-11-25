#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sound_orphans.py — аудит сиротских .ogg (K8-S, ТЗ 3.7.0 §3).

Сирота = файл .ogg лежит в пакете, но ни одно событие sounds.json на него
не ссылается. Критерий приёмки 3.7.0 §3: «либо 0 файлов-сирот в JAR,
либо оба подключены и слышны».

Также ловит обратную ошибку: ссылка в sounds.json на несуществующий файл
(«ссылка в пустоту») — она ломает звук на клиенте.

Использование:
    python3 tools/sound_orphans.py <каталог|zip> [--quiet]

Код возврата: 0 — сирот 0 и ссылок в пустоту 0, 2 — есть замечания, 1 — ошибка.
"""

import io
import json
import os
import sys
import zipfile

ASSETS = "assets/carnis/"
SOUNDS_JSON = ASSETS + "sounds.json"
SOUNDS_DIR = ASSETS + "sounds/"


def norm(path):
    """assets/carnis/sounds/block/x.ogg -> carnis:block/x"""
    p = path.replace("\\", "/")
    i = p.find(SOUNDS_DIR)
    if i < 0:
        return None
    rel = p[i + len(SOUNDS_DIR):]
    if not rel.endswith(".ogg"):
        return None
    return "carnis:" + rel[:-4]


def collect(src):
    """Вернуть (множество ссылок, множество файлов, dict sounds.json)."""
    files = set()
    data = None

    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                k = norm(n)
                if k:
                    files.add(k)
            want = [n for n in z.namelist()
                    if n.replace("\\", "/").endswith(SOUNDS_JSON)]
            if want:
                with z.open(want[0]) as f:
                    data = json.load(io.BytesIO(f.read()))
    else:
        # Ищем sounds.json, затем считаем .ogg РЯДОМ с ним (в той же ветке
        # assets/carnis/). Иначе можно взять generated/sounds.json и считать
        # файлы в main/resources — два разных пути, ложные «ссылки в пустоту».
        sj = os.path.join(src, SOUNDS_JSON)
        if not os.path.exists(sj):
            for dp, _, fs in os.walk(src):
                if "sounds.json" in fs:
                    sj = os.path.join(dp, "sounds.json")
                    break
        if os.path.exists(sj):
            with open(sj, encoding="utf-8") as f:
                data = json.load(f)
            sdir = os.path.join(os.path.dirname(sj), "sounds")
            for dp, _, fs in os.walk(sdir):
                for f in fs:
                    if f.endswith(".ogg"):
                        full = os.path.join(dp, f)
                        rel = os.path.relpath(full, sdir).replace(os.sep, "/")
                        files.add("carnis:" + rel[:-4])

    if data is None:
        raise SystemExit("ОШИБКА: не найден %s в %s" % (SOUNDS_JSON, src))

    refs = set()
    for _ev, body in data.items():
        for s in body.get("sounds", []):
            name = s if isinstance(s, str) else s.get("name", "")
            if name:
                refs.add(name)
    return refs, files, data


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in sys.argv
    if not args:
        print(__doc__)
        return 1
    src = args[0]
    if not zipfile.is_zipfile(src) and not os.path.isdir(src):
        print("ОШИБКА: нет такого каталога или zip: %s" % src)
        return 1

    try:
        refs, files, data = collect(src)
    except SystemExit as e:
        print(e)
        return 1

    orphans = sorted(files - refs)
    dangling = sorted(refs - files)

    if not quiet:
        print("Аудит сирот .ogg (K8-S, ТЗ 3.7.0 §3)")
        print("Пакет:     %s" % src)
        print("Событий в sounds.json: %d, ссылок на файлы: %d, файлов .ogg: %d"
              % (len(data), len(refs), len(files)))
        print()

    if orphans:
        print("СИРОТЫ (%d) — файл есть, ссылок нет:" % len(orphans))
        for o in orphans:
            print("  - %s.ogg" % o)
    elif not quiet:
        print("Сирот нет: 0")

    if dangling:
        print()
        print("ССЫЛКИ В ПУСТОТУ (%d) — sounds.json зовёт несуществующий файл:"
              % len(dangling))
        for d in dangling:
            print("  - %s" % d)

    print()
    if orphans or dangling:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — сирот %d, ссылок в пустоту %d"
              % (len(orphans), len(dangling)))
        return 2
    print("ИТОГ: СХОДИТСЯ — сирот 0, ссылок в пустоту 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
