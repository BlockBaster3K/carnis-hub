#!/usr/bin/env python3
"""Проверка актуальности baseline_master.json (S50).

Зачем: baseline(M) — число, измеренное ОДИН раз (S48). Если файл банка изменится
(его перерисуют, перекодируют, подменят), число станет ложным, и гейт будет
судить по устаревшему допуску — молча, без ошибки. Это класс «источник истины
вне артефакта, fail-open», за который в проекте уже отзывали находки.

Этот скрипт сверяет SHA256 и размер каждого файла из JSON с тем, что лежит в
репозитории. Код возврата:
  0 — все записи актуальны
  2 — есть устаревшие записи (файл изменён/удалён/добавлен без записи) -> FAIL-CLOSED
  3 — сам JSON не читается или имеет не ту схему

Использование:
  python3 03-sound/check_baseline_master.py [--bank DIR] [--quiet]
"""
import argparse
import hashlib
import json
import os
import sys

SCHEMAS = ("carnis.baseline_master/1", "carnis.baseline_master/2")
REQUIRED = ("file", "signal_type", "threshold", "baseline_master", "tolerance")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", default=os.path.join("03-sound", "baseline_master.json"))
    ap.add_argument("--bank", default="03-sound", help="корень банка (по умолчанию 03-sound)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    try:
        doc = json.load(open(a.json, encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print("ОШИБКА: %s не читается (%s)" % (a.json, exc))
        return 3
    if doc.get("schema") not in SCHEMAS:
        print("ОШИБКА: схема %r, ожидалась одна из %r" % (doc.get("schema"), SCHEMAS))
        return 3
    rows = doc.get("files") or []
    if not rows:
        print("ОШИБКА: в %s нет записей" % a.json)
        return 3

    # самодостаточность записи (R23 §12: гейт не должен ходить в таблицу за типом)
    incomplete = []
    for r in rows:
        lost = [k for k in REQUIRED if k not in r]
        if lost:
            incomplete.append((r.get("file", "?"), ",".join(lost)))
            continue
        # tolerance должна совпадать с формулой З-30/З-31
        want = max(float(r["threshold"]), float(r["baseline_master"]) + 0.05)
        if abs(float(r["tolerance"]) - want) > 5e-4:
            incomplete.append((r["file"], "tolerance %.3f != max(%.2f, %.3f+0.05)"
                               % (r["tolerance"], r["threshold"], r["baseline_master"])))

    stale, missing, untracked = [], [], []
    recorded = set()
    for r in rows:
        rel = r["file"]
        recorded.add(rel)
        p = os.path.join(a.bank, rel)
        if not os.path.exists(p):
            missing.append(rel)
            continue
        if os.path.getsize(p) != r.get("file_size") or sha256_of(p) != r.get("file_sha256"):
            stale.append(rel)

    # файлы банка с мастером, но без записи в JSON — тоже устаревание
    for bank in ("sounds_380", "sounds"):
        root = os.path.join(a.bank, bank)
        mast = os.path.join(a.bank, "masters", bank)
        if not os.path.isdir(root) or not os.path.isdir(mast):
            continue
        for dp, _, fs in os.walk(root):
            for f in fs:
                if not f.endswith(".ogg"):
                    continue
                full = os.path.join(dp, f)
                rel = os.path.join(bank, os.path.relpath(full, root)).replace(os.sep, "/")
                if bank == "sounds":
                    has = os.path.exists(os.path.join(mast, "_z21", f[:-4] + ".flac"))
                else:
                    has = os.path.exists(os.path.join(mast, os.path.relpath(full, root))[:-4] + ".flac")
                if has and rel not in recorded:
                    untracked.append(rel)

    total = len(rows)
    if not a.quiet:
        print("baseline_master: %s, записей %d, перекод %s"
              % (a.json, total, doc.get("recode_preset", "?")))
    if incomplete:
        print("  x запись неполна или tolerance не по формуле: %d" % len(incomplete))
        for r, why in incomplete[:5]:
            print("      ? %s (%s)" % (r, why))
    if missing:
        print("  x нет файла: %d" % len(missing))
        for r in missing[:5]:
            print("      ? %s" % r)
    if stale:
        print("  x файл изменён, число baseline(M) устарело: %d" % len(stale))
        for r in stale[:5]:
            print("      ! %s" % r)
    if untracked:
        print("  x файл с мастером, но без записи: %d" % len(untracked))
        for r in untracked[:5]:
            print("      + %s" % r)
    if missing or stale or untracked or incomplete:
        print("ИТОГ: НЕАКТУАЛЬНО — пересчитать baseline(M) и обновить JSON (S48)")
        return 2
    if not a.quiet:
        print("ИТОГ: АКТУАЛЬНО — %d записей, все SHA256 сходятся, tolerance по формуле" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
