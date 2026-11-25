#!/usr/bin/env python3
"""Проверка манифеста канона (S60/S65).

Зачем: `MANIFEST_canon_144.txt` — единственный пригодный эталон канона (S60).
Как только файл канона изменится без пересчёта манифеста, приёмка «банк == пакет»
будет сверять с устаревшим эталоном и даст ложные расхождения — молча.

Коды возврата:
  0 — манифест актуален: 144 файла, все SHA256 сходятся, лишних/недостающих нет
  2 — расхождение: файл изменён/удалён/добавлен без записи в манифесте
  3 — манифест не читается или покрывает не 144 файла

Использование:
  python3 tools/manifest_canon_test.py [--bank DIR] [--manifest FILE]
"""
import argparse
import hashlib
import os
import sys

CANON_COUNT = 144


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 2:
                continue
            digest, rel = parts
            rows[rel] = digest
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default=os.path.join("03-sound", "sounds"))
    ap.add_argument("--manifest",
                    default=os.path.join("03-sound", "MANIFEST_canon_144.txt"))
    a = ap.parse_args(argv)

    try:
        want = load_manifest(a.manifest)
    except OSError as exc:
        print("ОШИБКА: манифест %s не читается (%s)" % (a.manifest, exc))
        return 3
    if len(want) != CANON_COUNT:
        print("ОШИБКА: манифест покрывает %d файлов, ожидалось %d — "
              "это не манифест канона" % (len(want), CANON_COUNT))
        return 3

    # фактические файлы канона: путь в манифесте имеет префикс sounds/
    have = {}
    prefix = os.path.basename(os.path.normpath(a.bank))
    if not os.path.isdir(a.bank):
        print("ОШИБКА: каталог банка %s не найден" % a.bank)
        return 3
    for dp, _, fs in os.walk(a.bank):
        for f in fs:
            if not f.endswith(".ogg"):
                continue
            full = os.path.join(dp, f)
            rel = "%s/%s" % (prefix,
                             os.path.relpath(full, a.bank).replace(os.sep, "/"))
            have[rel] = full

    missing = sorted(set(want) - set(have))     # в манифесте есть, файла нет
    extra = sorted(set(have) - set(want))       # файл есть, в манифесте нет
    changed = []
    for rel, full in have.items():
        if rel in want and sha256_of(full) != want[rel]:
            changed.append(rel)

    print("манифест канона: %s (%d записей), банк: %s (%d файлов)"
          % (a.manifest, len(want), a.bank, len(have)))
    for title, items in (("файл удалён", missing),
                         ("файл изменён", changed),
                         ("файл добавлен без записи", extra)):
        if items:
            print("  x %s: %d" % (title, len(items)))
            for rel in items[:5]:
                print("      ? %s" % rel)
    if missing or extra or changed:
        print("ИТОГ: МАНИФЕСТ УСТАРЕЛ — пересчитать MANIFEST_canon_144.txt "
              "в том же коммите (S60)")
        return 2
    print("ИТОГ: АКТУАЛЬНО — %d файлов, все SHA256 сходятся" % len(want))
    return 0


if __name__ == "__main__":
    sys.exit(main())
