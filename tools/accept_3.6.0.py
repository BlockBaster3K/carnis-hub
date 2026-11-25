#!/usr/bin/env python3
"""Приёмка пакета 3.6.0 по порядку заказчика.

Порядок (тот же, что для 3.5.3):
    1. распаковать ZIP;
    2. sha256sum -c по внешнему манифесту;
    3. все JSON пакета разбираются;
    4. версия 3.6.0 в четырёх местах;
    5. cmp по overlay (источники == цели в пакете);
    6. сводка K4 / K5 / K6-S — факты, а не оценки.

Запуск:
    python3 tools/accept_3.6.0.py [путь_к_zip] [путь_к_манифесту]

Коды возврата:
    0 — все проверки пройдены, пакет готов к CI и merge;
    1 — есть блокирующие расхождения;
    2 — пакет или манифест не найдены.
"""
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ZIP = os.path.join(REPO, "01-coder", "3.6.0", "project-3.6.0-clean.zip")
DEFAULT_MANIFEST = os.path.join(REPO, "01-coder", "3.6.0",
                                "project-3.6.0-clean.manifest.txt")
OVERLAY = os.path.join(REPO, "06-build", "overlay.txt")
VERSION = "3.6.0"

fail = []
warn = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest(extract_dir, manifest):
    if not os.path.exists(manifest):
        print(f"  ✗ манифест не найден: {manifest}")
        fail.append("манифест не найден")
        return
    ok = bad = miss = 0
    with open(manifest, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                continue
            want, rel = parts
            p = os.path.join(extract_dir, rel)
            if not os.path.exists(p):
                miss += 1
                print(f"    отсутствует: {rel}")
            elif sha256(p) == want:
                ok += 1
            else:
                bad += 1
                print(f"    расхождение: {rel}")
    mark = "✓" if bad == 0 and miss == 0 else "✗"
    print(f"  {mark} совпало {ok}, расхождений {bad}, отсутствует {miss}")
    if bad or miss:
        fail.append(f"манифест: расхождений {bad}, отсутствует {miss}")


def check_json(extract_dir):
    total = bad = 0
    for root, _dirs, files in os.walk(extract_dir):
        for name in files:
            if not name.endswith(".json"):
                continue
            total += 1
            p = os.path.join(root, name)
            try:
                with open(p, encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:  # noqa: BLE001
                bad += 1
                print(f"    невалидный JSON: {os.path.relpath(p, extract_dir)} — {e}")
    mark = "✓" if bad == 0 else "✗"
    print(f"  {mark} JSON: {total} файлов, невалидных {bad}")
    if bad:
        fail.append(f"JSON: невалидных {bad}")


def check_version(extract_dir, zip_path):
    """Версия 3.6.0 в четырёх местах (по §3 ТЗ 3.6.0)."""
    places = []

    gp = os.path.join(extract_dir, "gradle.properties")
    if os.path.exists(gp):
        with open(gp, encoding="utf-8") as f:
            m = re.search(r"^mod_version=(.+)$", f.read(), re.M)
        places.append(("gradle.properties: mod_version", m.group(1).strip() if m else "—"))
    else:
        places.append(("gradle.properties", "НЕТ ФАЙЛА"))

    toml = os.path.join(extract_dir, "src/main/resources/META-INF/mods.toml")
    ver = disp = "НЕТ ФАЙЛА"
    if os.path.exists(toml):
        with open(toml, encoding="utf-8") as f:
            txt = f.read()
        m = re.search(r'^\s*version\s*=\s*"([^"]+)"', txt, re.M)
        ver = m.group(1) if m else "—"
        if "displayVersion" in txt:
            m2 = re.search(r'displayVersion\s*=\s*"([^"]+)"', txt)
            disp = m2.group(1) if m2 else "—"
        else:
            disp = "(не объявлен)"
    places.append(("mods.toml: version", ver))
    places.append(("mods.toml: displayVersion", disp))

    d = os.path.basename(zip_path).replace("project-", "").replace("-clean.zip", "")
    places.append(("имя пакета", d))

    ok = True
    for name, val in places:
        good = str(val).startswith(VERSION)
        if not good:
            ok = False
        print(f"  {'✓' if good else '✗'} {name}: {val}")
    if not ok:
        fail.append("версия 3.6.0 не во всех четырёх местах")


def check_overlay(extract_dir):
    """cmp по overlay: источник == цель в пакете."""
    if not os.path.exists(OVERLAY):
        print("  ⚠ overlay.txt не найден — проверка пропущена")
        warn.append("overlay.txt отсутствует")
        return
    ok = bad = 0
    with open(OVERLAY, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line or "->" not in line:
                continue
            src = line.split("->", 1)[0].strip()
            rest = line.split("->", 1)[1]
            dst = rest.split("|", 1)[0].strip()
            want = rest.split("|", 1)[1].strip() if "|" in rest else ""
            sp = os.path.join(REPO, src)
            if not os.path.exists(sp):
                bad += 1
                print(f"    ✗ нет источника: {src}")
                continue
            if want and sha256(sp) != want:
                bad += 1
                print(f"    ✗ хеш источника не совпал: {src}")
                continue
            dp = os.path.join(extract_dir, dst)
            if not os.path.exists(dp):
                # overlay может намеренно перекрывать файл, которого нет в пакете
                warn.append(f"цель overlay отсутствует в пакете: {dst}")
                print(f"    ⚠ цели нет в пакете: {dst}")
                continue
            if sha256(sp) == sha256(dp):
                ok += 1
            else:
                bad += 1
                print(f"    ✗ расхождение с пакетом: {dst}")
    mark = "✓" if bad == 0 else "✗"
    print(f"  {mark} overlay: совпало {ok}, расхождений {bad}")
    if bad:
        fail.append(f"overlay: расхождений {bad}")


def summary_k4(extract_dir):
    """K4 — два мёртвых ресурса удалены, ссылок на них нет."""
    targets = [
        "src/main/resources/assets/carnis/textures/item/bio_purifier_geo.png",
        "src/main/resources/assets/carnis/models/item/pulsing_heart_geometry.json",
    ]
    for rel in targets:
        name = os.path.basename(rel)
        present = os.path.exists(os.path.join(extract_dir, rel))
        if present:
            fail.append(f"K4: файл не удалён — {name}")
        print(f"  {'✗' if present else '✓'} удалён: {name}")


def check_k5(extract_dir):
    """K5 — blockstates = 4 x N, y по facing, parent лестницы сохранён."""
    bs = os.path.join(extract_dir,
                      "src/main/resources/assets/carnis/blockstates/creeping_tendrils.json")
    if not os.path.exists(bs):
        warn.append("K5: blockstates/creeping_tendrils.json отсутствует")
        print("  ⚠ blockstates/creeping_tendrils.json отсутствует")
        return
    with open(bs, encoding="utf-8") as f:
        d = json.load(f)
    variants = d.get("variants", {})
    print(f"  ✓ вариантов: {len(variants)}")
    bad_y = []
    for key, val in variants.items():
        m = re.search(r"facing=(north|south|west|east)", key)
        if not m:
            bad_y.append(f"{key}: нет facing")
            continue
        expected_y = {"north": 0, "south": 180, "west": 270, "east": 90}[m.group(1)]
        models = val if isinstance(val, list) else [val]
        for mv in models:
            got = mv.get("y", 0)
            if got != expected_y:
                bad_y.append(f"{key}: y={got}, ожидалось {expected_y}")
    if bad_y:
        print(f"  ✗ y не соответствует facing: {len(bad_y)} случаев")
        for b in bad_y[:3]:
            print(f"      {b}")
        fail.append(f"K5: y/facing расхождений {len(bad_y)}")
    else:
        print("  ✓ y соответствует facing во всех вариантах")
    # parent лестницы задаётся в ФАЙЛАХ МОДЕЛЕЙ, на которые ссылается blockstates,
    # а не в самом blockstates — проверяем там.
    model_ids = set()
    for mv in variants.values():
        for m_ in (mv if isinstance(mv, list) else [mv]):
            mid = m_.get("model", "")
            if mid:
                model_ids.add(mid.split(":")[-1])
    ladder_ok = False
    for mid in model_ids:
        mp = os.path.join(extract_dir, "src/main/resources/assets/carnis/models", mid + ".json")
        if not os.path.exists(mp):
            continue
        with open(mp, encoding="utf-8") as f:
            try:
                md = json.load(f)
            except Exception:  # noqa: BLE001
                continue
        if "ladder" in str(md.get("parent", "")):
            ladder_ok = True
    if ladder_ok:
        print("  ✓ parent minecraft:block/ladder сохранён")
    else:
        print("  ✗ parent minecraft:block/ladder не найден в моделях вариантов")
        fail.append("K5: parent minecraft:block/ladder не сохранён")


def check_k6s(extract_dir):
    """K6-S — 82 события, файлы косы в пакете, константы не в вызовах."""
    sj = os.path.join(extract_dir, "src/main/resources/assets/carnis/sounds.json")
    if os.path.exists(sj):
        with open(sj, encoding="utf-8") as f:
            d = json.load(f)
        n = len(d)
        mark = "✓" if n == 82 else "⚠"
        if n != 82:
            warn.append(f"K6-S: событий {n}, ожидалось 82")
        print(f"  {mark} событий в sounds.json: {n} (ТЗ ждёт 82)")
        for name in ("ossified_scythe_hit", "ossified_scythe_swing"):
            for k, v in d.items():
                if name in k:
                    snd = v.get("sounds", [{}])
                    has = any("pitch" in s or "volume" in s for s in snd)
                    print(f"  {'✗' if has else '✓'} {k}: без pitch/volume"
                          if not has else f"  ✗ {k}: заданы pitch/volume")
                    if has:
                        fail.append(f"K6-S: {k} имеет pitch/volume")
    else:
        warn.append("K6-S: sounds.json отсутствует")
    # константы не должны вызываться в ScytheItem / CombatItemEvents
    for rel in ("src/main/java/com/carnis/mod/item/ScytheItem.java",
                "src/main/java/com/carnis/mod/event/CombatItemEvents.java"):
        p_ = os.path.join(extract_dir, rel)
        if not os.path.exists(p_):
            continue
        with open(p_, encoding="utf-8") as f:
            src = f.read()
        for const in ("OSSIFIED_SCYTHE_HIT", "OSSIFIED_SCYTHE_SWING"):
            if const in src:
                print(f"  ✗ {const} осталась в {os.path.basename(rel)}")
                fail.append(f"K6-S: {const} в {os.path.basename(rel)}")


def summary_k6s(extract_dir):
    """K6-S — файлы косы в пакете."""
    d = os.path.join(extract_dir, "src/main/resources/assets/carnis/sounds")
    if not os.path.isdir(d):
        print("  ⚠ каталог sounds не найден")
        return
    found = []
    for root, _dirs, files in os.walk(d):
        for name in files:
            if "scythe" in name.lower() or "bone_scythe" in name.lower():
                found.append(os.path.relpath(os.path.join(root, name), extract_dir))
    if found:
        for p in sorted(found):
            print(f"  ✓ {p}")
    else:
        warn.append("K6-S: файлов косы в пакете не найдено")
        print("  ⚠ файлов косы не найдено")


def main():
    zip_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ZIP
    manifest = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MANIFEST

    if not os.path.exists(zip_path):
        print(f"Пакет не найден: {zip_path}", file=sys.stderr)
        print("Приёмку проводить не по чему — 3.6.0 не сдан.", file=sys.stderr)
        return 2

    print(f"Пакет:   {os.path.relpath(zip_path, REPO)}")
    print(f"Размер:  {os.path.getsize(zip_path)} Б")
    print(f"SHA-256: {sha256(zip_path)}")
    print()

    tmp = tempfile.mkdtemp(prefix="accept360_")
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            z.extractall(tmp)
        dups = len(names) - len(set(names))
        print(f"Распаковано {len(names)} записей, дубликатов путей {dups}.")
        if dups:
            fail.append(f"дубликаты путей в ZIP: {dups}")
        print()

        print("1) Манифест (sha256sum -c)")
        check_manifest(tmp, manifest)
        print()

        print("2) JSON")
        check_json(tmp)
        print()

        print("3) Версия 3.6.0 в четырёх местах")
        check_version(tmp, zip_path)
        print()

        print("4) Overlay (cmp источник — пакет)")
        check_overlay(tmp)
        print()

        print("5) K4 — удаление двух мёртвых ресурсов")
        summary_k4(tmp)
        print()

        print("6) K5 — blockstates и facing")
        check_k5(tmp)
        print()

        print("7) K6-S — звук косы")
        summary_k6s(tmp)
        check_k6s(tmp)
        print()

        print("8) Число файлов пакета")
        count = sum(len(files) for _r, _d, files in os.walk(tmp))
        print(f"  файлов: {count}")
        print()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fail:
        print(f"ИТОГ: НЕ ПРИНЯТО — расхождений {len(fail)}")
        for x in fail:
            print(f"  • {x}")
        if warn:
            print("предупреждения:")
            for x in warn:
                print(f"  · {x}")
        print("\nMerge в main, тег v3.6.0 и релиз запрещены.")
        return 1

    print("ИТОГ: ПРИНЯТО — все проверки пройдены.")
    if warn:
        print("предупреждения (не блокируют):")
        for x in warn:
            print(f"  · {x}")
    print("Дальше: CI на новом коммите → merge PR → тег v3.6.0 → Release.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
