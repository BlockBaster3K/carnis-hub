#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приёмка пакета 3.7.0 по ТЗ 3.7.0.

Проверки:
    1. манифест sha256sum -c и число файлов;
    2. все JSON разбираются;
    3. версия 3.7.0 в четырёх местах;
    4. overlay accepted drops;
    5. A4-p7 — палитра существ (делегируется tools/glow_check.py);
    6. K8-S — 0 сиротских .ogg (делегируется tools/sound_orphans.py);
    7. Д1–Д7 и принятое не тронуто — сверка с 3.6.0-R.

Использование:
    python3 tools/accept_3.7.0.py [путь_к_zip] [путь_к_манифесту]

Коды: 0 — ПРИНЯТО, 1 — ЕСТЬ РАСХОЖДЕНИЯ, 2 — нет пакета / ошибка запуска.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ZIP = os.path.join(REPO, "01-coder", "3.7.0",
                           "project-3.7.0-clean.zip")
DEFAULT_MANIFEST = os.path.join(REPO, "01-coder", "3.7.0",
                                "project-3.7.0-clean.manifest.txt")
REF_360 = os.path.join(REPO, "01-coder", "3.6.0-R",
                       "project-3.6.0-R-clean.zip")

VERSION = "3.7.0"
GLOW_CHECK = os.path.join(REPO, "tools", "glow_check.py")
ORPHANS = os.path.join(REPO, "tools", "sound_orphans.py")

fail = []
warn = []

# Д1–Д7 и принятое: то, что НЕ должно измениться относительно 3.6.0-R.
KEEP_IDENTICAL = [
    "src/main/resources/assets/carnis/geo/entity/cerebral_nexus.geo.json",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_1.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_2.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_3.png",
    "src/main/resources/assets/carnis/textures/block/spore_sprout.png",
    "src/main/resources/assets/carnis/textures/block/neural_moss.png",
    "src/main/resources/assets/carnis/textures/block/pustule_cluster.png",
    "src/main/resources/assets/carnis/textures/mob_effect/incubating.png",
    "src/main/resources/assets/carnis/textures/mob_effect/thermal_shock.png",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_0.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_1.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_2.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_3.json",
]


def find_manifest(zip_path, given):
    if given and os.path.exists(given):
        return given
    d = os.path.dirname(zip_path)
    base = os.path.basename(zip_path)
    for cand in (base.replace(".zip", ".manifest.txt"),
                 base[:-4] + "-manifest.txt"):
        p = os.path.join(d, cand)
        if os.path.exists(p):
            return p
    hits = [f for f in sorted(os.listdir(d)) if f.endswith(".manifest.txt")]
    return os.path.join(d, hits[0]) if hits else None


def check_manifest(extract_dir, manifest):
    if not manifest or not os.path.exists(manifest):
        fail.append("манифест не найден — целостность не проверить")
        print("  ✗ манифест не найден")
        return
    r = subprocess.run(["sha256sum", "-c", manifest], cwd=extract_dir,
                       capture_output=True, text=True)
    ok = r.stdout.count(": OK")
    bad = r.stdout.count("FAILED")
    lines = sum(1 for line in open(manifest, encoding="utf-8") if line.strip())
    print("  ✓ совпало %d, расхождений %d, строк %d" % (ok, bad, lines)
          if not bad else "  ✗ совпало %d, РАСХОЖДЕНИЙ %d" % (ok, bad))
    if bad:
        fail.append("манифест: %d расхождений" % bad)
    if ok + bad != lines:
        fail.append("манифест: строк %d, проверено %d" % (lines, ok + bad))


def check_json(extract_dir):
    n = bad = 0
    for dp, _, fs in os.walk(extract_dir):
        for f in fs:
            if f.endswith(".json"):
                n += 1
                p = os.path.join(dp, f)
                try:
                    with open(p, encoding="utf-8") as fh:
                        json.load(fh)
                except Exception as e:
                    bad += 1
                    if bad <= 3:
                        print("  ✗ %s — %s" % (os.path.relpath(p, extract_dir), e))
    print("  ✓ JSON: %d файлов, невалидных %d" % (n, bad)
          if not bad else "  ✗ JSON: %d файлов, НЕВАЛИДНЫХ %d" % (n, bad))
    if bad:
        fail.append("невалидных JSON: %d" % bad)


def check_version(extract_dir, zip_path):
    gp = os.path.join(extract_dir, "gradle.properties")
    mt = os.path.join(extract_dir, "src", "main", "resources", "META-INF",
                      "mods.toml")
    seen = {}
    if os.path.exists(gp):
        for line in open(gp, encoding="utf-8"):
            if line.startswith("mod_version="):
                seen["gradle.properties"] = line.split("=", 1)[1].strip()
                break
    if os.path.exists(mt):
        for line in open(mt, encoding="utf-8"):
            s = line.strip()
            if s.startswith("version=") and "version" not in seen:
                seen["mods.toml version"] = s.split("=", 1)[1].strip().strip('"')
            if s.startswith("displayVersion="):
                seen["displayVersion"] = s.split("=", 1)[1].strip().strip('"')
    folder = os.path.basename(os.path.dirname(zip_path))
    base = folder.split("-R")[0]
    for where, val in seen.items():
        ok = val == VERSION
        print("  %s %s: %s" % ("✓" if ok else "✗", where, val))
        if not ok:
            fail.append("версия %s: %s = %s" % (where, where, val))
    ok = base == VERSION
    print("  %s имя пакета: %s" % ("✓" if ok else "✗", folder))
    if not ok:
        fail.append("каталог пакета %s, ожидался %s" % (folder, VERSION))
    if len(seen) < 3:
        fail.append("версия: найдено только %d из 3 мест" % len(seen))


def check_overlay(extract_dir):
    ov = os.path.join(REPO, "06-build", "overlay.txt")
    if not os.path.exists(ov):
        warn.append("overlay.txt нет — пропущено")
        print("  ! overlay.txt нет")
        return
    # Формат строки: "<источник> -> <назначение в пакете> | <sha256 назначения>"
    import re
    n = ok = 0
    for line in open(ov, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "->" not in line:
            continue
        left, _, right = line.partition("->")
        src = left.strip()
        dst, _, claim = right.partition("|")
        dst, claim = dst.strip(), claim.strip()
        n += 1
        a = os.path.join(REPO, src)
        b = os.path.join(extract_dir, dst)
        if not os.path.exists(a):
            print("  ✗ overlay: нет источника %s" % src)
        elif not os.path.exists(b):
            print("  ✗ overlay: в пакете нет %s" % dst)
        else:
            data = open(b, "rb").read()
            same = open(a, "rb").read() == data
            if same and claim:
                import hashlib
                same = hashlib.sha256(data).hexdigest() == claim
            if same:
                ok += 1
            else:
                print("  ✗ overlay расхождение: %s" % dst)
    print("  ✓ overlay: совпало %d из %d" % (ok, n) if ok == n
          else "  ✗ overlay: совпало %d из %d" % (ok, n))
    if ok != n:
        fail.append("overlay: %d из %d" % (ok, n))


def _python_with_pillow():
    """Интерпретатор, у которого есть Pillow: glow_check без него не работает."""
    cands = [sys.executable, "/tmp/vv/bin/python", "python3"]
    for c in cands:
        if not c or not (os.path.exists(c) or c == "python3"):
            continue
        r = subprocess.run([c, "-c", "import PIL"], capture_output=True)
        if r.returncode == 0:
            return c
    return None


def run_tool(name, script, *args):
    need_pil = "glow_check" in script
    py = _python_with_pillow() if need_pil else sys.executable
    if py is None:
        print("  ✗ %s: нет интерпретатора с Pillow (python3 -m pip install Pillow)" % name)
        fail.append("%s: нет Pillow" % name)
        return
    r = subprocess.run([py, script] + list(args), capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().split("\n") if l.startswith("ИТОГ")]
    print("  %s %s → код %d | %s" % ("✓" if r.returncode == 0 else "✗",
                                     name, r.returncode,
                                     tail[0] if tail else "(нет строки ИТОГ)"))
    if r.returncode != 0:
        for line in r.stdout.split("\n"):
            if "[!]" in line or "СИРОТЫ" in line or "  - " in line:
                print("      " + line.strip())
        fail.append("%s: код %d" % (name, r.returncode))


def check_keep_identical(extract_dir):
    if not os.path.exists(REF_360):
        warn.append("нет эталона 3.6.0-R — Д1–Д7 не сверены")
        print("  ! эталона 3.6.0-R нет, пропущено")
        return
    same = diff = missing = 0
    with zipfile.ZipFile(REF_360) as z:
        names = set(z.namelist())
        for rel in KEEP_IDENTICAL:
            cand = [n for n in names if n.endswith(rel)]
            cur = os.path.join(extract_dir, rel)
            if not cand or not os.path.exists(cur):
                missing += 1
                print("  ✗ нет файла: %s" % rel)
                continue
            if z.read(cand[0]) == open(cur, "rb").read():
                same += 1
            else:
                diff += 1
                print("  ✗ ИЗМЕНЁН (принятое трогать нельзя): %s" % rel)
    print("  %s сверено с 3.6.0-R: идентично %d, изменено %d, нет %d"
          % ("✓" if diff == 0 and missing == 0 else "✗", same, diff, missing))
    if diff:
        fail.append("изменено принятых файлов: %d" % diff)
    if missing:
        fail.append("не найдено принятых файлов: %d" % missing)


def main():
    zip_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ZIP
    man_arg = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MANIFEST

    print("Приёмка пакета %s (ТЗ 3.7.0)" % VERSION)
    if not os.path.exists(zip_path):
        print()
        print("ПАКЕТ НЕ НАЙДЕН: %s" % zip_path)
        print("Ждём сдачу: 04-artist/deliverables/Carnis_3.7.0_A4p7_palette.zip")
        print("            → сборка пакета Кодером → 01-coder/3.7.0/")
        return 2

    print("Пакет:   %s" % os.path.relpath(zip_path, REPO))
    print("Размер:  %d Б" % os.path.getsize(zip_path))
    h = subprocess.run(["sha256sum", zip_path], capture_output=True, text=True)
    print("SHA-256: %s" % h.stdout.split()[0])
    print()

    tmp = tempfile.mkdtemp(prefix="accept370_")
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            print("Распаковано %d записей, дубликатов путей %d."
                  % (len(names), len(names) - len(set(names))))
            z.extractall(tmp)

        print()
        print("1) Манифест (sha256sum -c)")
        m = find_manifest(zip_path, man_arg)
        if m:
            print("   %s" % os.path.relpath(m, REPO))
        check_manifest(tmp, m)

        print()
        print("2) JSON")
        check_json(tmp)

        print()
        print("3) Версия %s в четырёх местах" % VERSION)
        check_version(tmp, zip_path)

        print()
        print("4) Overlay (cmp источник — пакет)")
        check_overlay(tmp)

        print()
        print("5) A4-p7 — палитра существ (ТЗ §2.3)")
        if os.path.exists(GLOW_CHECK):
            run_tool("glow_check", GLOW_CHECK, zip_path, REF_360)
        else:
            fail.append("tools/glow_check.py отсутствует — A4-p7 не проверить")

        print()
        print("6) K8-S — сиротские .ogg (ТЗ §3)")
        if os.path.exists(ORPHANS):
            run_tool("sound_orphans", ORPHANS, zip_path)
        else:
            fail.append("tools/sound_orphans.py отсутствует — K8-S не проверить")

        print()
        print("7) Д1–Д7 и принятое не тронуто")
        check_keep_identical(tmp)

        print()
        if warn:
            print("Предупреждения: %d" % len(warn))
            for w in warn:
                print("  - %s" % w)
        if fail:
            print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — %d" % len(fail))
            for i, f in enumerate(fail, 1):
                print("  %2d. %s" % (i, f))
            return 1
        print("ИТОГ: ПРИНЯТО — все проверки пройдены.")
        print("Дальше: CI на новом коммите → merge PR → тег v%s → Release." % VERSION)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
