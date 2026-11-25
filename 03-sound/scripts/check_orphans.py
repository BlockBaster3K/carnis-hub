#!/usr/bin/env python3
"""check_orphans.py — проверка сиротских .ogg в пакете CARNIS (критерий K8-S).

Критерий приёмки K8-S (ТЗ 3.7.0 §3): «либо 0 файлов-сирот в JAR, либо оба
подключены и слышны». Этот скрипт проверяет ПЕРВУЮ половину — формально и
воспроизводимо, без игры.

Сирота = файл `assets/carnis/sounds/<путь>.ogg`, на который НЕ ссылается ни одна
запись `sounds` в `assets/carnis/sounds.json` (сравнение по пути после снятия
префикса `carnis:`). Дополнительно проверяется обратная ситуация — путь в
`sounds.json`, для которого нет файла.

Использование:
    python3 check_orphans.py <jar | каталог проекта>
    python3 check_orphans.py carnis-3.6.0.jar
    python3 check_orphans.py 01-coder/3.7.0
    python3 check_orphans.py 01-coder/3.7.0 --verbose

Коды возврата:
    0 — 0 сирот и 0 «ссылок в никуда» (критерий K8-S по сиротам выполнен)
    2 — есть сироты или висячие ссылки (критерий НЕ выполнен)
    1 — ошибка входа (нет `sounds.json`, нет пакета, битый архив)

Зависимостей нет — только стандартная библиотека.
Автор: роль Звук, волна 30. Источник данных аудита:
`00-board/reports/sound_orphan_audit.md`.
"""

import hashlib
import json
import os
import sys
import zipfile

SOUNDS_DIR = "assets/carnis/sounds"
SOUNDS_JSON = "assets/carnis/sounds.json"


def _iter_pack(root):
    """Возвращает (sounds_json_bytes, {путь без .ogg: (размер, sha256, имя_записи)})."""
    if os.path.isdir(root):
        # ищем sounds.json в самом каталоге или глубже (каталог пакета 01-coder/3.7.0,
        # src/main/resources, src/generated/resources — на выбор пользователя)
        sj_path = None
        for base, dirs, names in os.walk(root):
            if "sounds.json" in names and base.replace(os.sep, "/").endswith("assets/carnis"):
                sj_path = os.path.join(base, "sounds.json")
                break
        if sj_path is None:
            raise SystemExit(f"ОШИБКА: под {root} не найден assets/carnis/sounds.json")
        sounds_root = os.path.join(os.path.dirname(sj_path), "sounds")
        with open(sj_path, "rb") as fh:
            sj = fh.read()
        files = {}
        for dirpath, _dirs, names in os.walk(sounds_root):
            for n in names:
                if not n.endswith(".ogg"):
                    continue
                full = os.path.join(dirpath, n)
                rel = os.path.relpath(full, sounds_root).replace(os.sep, "/")
                with open(full, "rb") as fh:
                    data = fh.read()
                files[rel[:-4]] = (len(data), hashlib.sha256(data).hexdigest(), full)
        return sj, files

    with zipfile.ZipFile(root) as z:
        names = z.namelist()
        if SOUNDS_JSON not in names:
            raise SystemExit(f"ОШИБКА: в {root} нет {SOUNDS_JSON}")
        sj = z.read(SOUNDS_JSON)
        files = {}
        for n in names:
            if not (n.startswith(SOUNDS_DIR + "/") and n.endswith(".ogg")):
                continue
            rel = n[len(SOUNDS_DIR) + 1:-4]
            data = z.read(n)
            files[rel] = (len(data), hashlib.sha256(data).hexdigest(), n)
    return sj, files


def collect_refs(sounds_json):
    """{путь: [события]} из sounds.json."""
    refs = {}
    for event, body in sounds_json.items():
        for entry in body.get("sounds", []):
            name = entry["name"] if isinstance(entry, dict) else entry
            name = name.replace("carnis:", "")
            refs.setdefault(name, []).append(event)
    return refs


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1
    root = argv[1]
    verbose = "--verbose" in argv

    if not os.path.exists(root):
        print(f"ОШИБКА: нет пути {root}")
        return 1

    try:
        sj_raw, files = _iter_pack(root)
    except (zipfile.BadZipFile, OSError) as exc:
        print(f"ОШИБКА: {exc}")
        return 1

    try:
        sounds_json = json.loads(sj_raw)
    except json.JSONDecodeError as exc:
        print(f"ОШИБКА: sounds.json не разбирается — {exc}")
        return 1

    refs = collect_refs(sounds_json)
    orphans = sorted(p for p in files if p not in refs)
    missing = sorted(p for p in refs if p not in files)
    used = [p for p in files if p in refs]

    label = os.path.basename(os.path.normpath(root))
    print(f"Пакет: {label}")
    print(f"Событий в sounds.json: {len(sounds_json)}")
    print(f"Уникальных путей в событиях: {len(refs)}")
    print(f"Файлов .ogg: {len(files)}")
    print(f"Используется файлов: {len(used)}")
    dup = {}
    for path, (_sz, sha, _n) in files.items():
        dup.setdefault(sha, []).append(path)
    same = {s: v for s, v in dup.items() if len(v) > 1}
    print(f"Дублей по sha256: {len(same)}")
    for sha, group in same.items():
        print(f"  ⚠ одинаковы: {sha[:16]}… — {', '.join(sorted(group))}")
    print()

    if orphans:
        print(f"СИРОТЫ ({len(orphans)}) — ни одного события:")
        print(f"  {'файл':34s} {'размер':>9s}  sha256")
        for p in orphans:
            sz, sha, _ = files[p]
            print(f"  {p + '.ogg':34s} {sz:9d}  {sha}")
    else:
        print("СИРОТ НЕТ — критерий K8-S по «0 сирот» выполнен.")

    if missing:
        print()
        print(f"ССЫЛКИ В НИКУДА ({len(missing)}) — событие есть, файла нет:")
        for p in missing:
            print(f"  {p + '.ogg':34s} ← {', '.join(refs[p])}")

    if verbose:
        print()
        print("Все файлы:")
        for p in sorted(files):
            events = ", ".join(refs.get(p, [])) or "—"
            print(f"  {p + '.ogg':34s} {files[p][0]:9d}  {files[p][1][:16]}…  {events}")

    print()
    if orphans or missing:
        print("ИТОГ: код 2 — критерий K8-S НЕ выполнен.")
        return 2
    print("ИТОГ: код 0 — 0 сирот, 0 висячих ссылок.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
