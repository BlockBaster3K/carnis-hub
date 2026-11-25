#!/usr/bin/env python3
"""Приёмка пакета 3.5.3 по порядку приказа: ZIP → cmp звуков → манифест → PNG Д6.

Запуск (из корня репозитория):
    python3 tools/accept_3.5.3.py [путь_к_zip] [путь_к_манифесту]

Коды возврата:
    0 — все проверки пройдены, пакет готов к CI и merge;
    1 — есть блокирующие расхождения (R1 не закрыт), merge запрещён;
    2 — пакет не найден или не читается.
"""
import hashlib
import os
import shutil
import sys
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ZIP = os.path.join(REPO, "01-coder", "3.5.3", "project-3.5.3-clean.zip")
DEFAULT_MANIFEST = os.path.join(REPO, "01-coder", "3.5.3",
                                "project-3.5.3-clean.manifest.txt")

# Два файла, из-за которых вынесено «НЕ ПРИНЯТО» (R1 вердикта Ревизора).
SOUNDS = {
    "block/heart_pulse.ogg": "17f42e3076ee1d0bc8212ea4d817d43ac3e78ebbee8d6c7544e87b4832f7e905",
    "block/heartbeat_loop.ogg": "39de4db0d9938af9dba8b1f6b637988003410dd7daf85b17df8284c49a513079",
}
# Четыре PNG, принятые у Художника (DDD3630) и уже перенесённые Кодером верно.
FLESH = {
    "block/ossified_flesh_0.png": "0380c2c288f62c9cf8b55808fad36ccda3c41ba798d1289766e4c0a8373116ec",
    "block/ossified_flesh_1.png": "dcf3a77cdaa45901aefdef58a29fe98277bed12e86d235e522ab8bcdb0ffcb34",
    "block/ossified_flesh_2.png": "76afe5487bceb7edb701516755d3153fb93db0f4544932262d34159404718451",
    "block/ossified_flesh_3.png": "cb97a4649746f9fe03d6ba62b43c2e4ff485b6849b5d81855951936869628f23",
}
SOUND_PREFIX = "src/main/resources/assets/carnis/sounds/"
TEX_PREFIX = "src/main/resources/assets/carnis/textures/"

fail = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sound(extract_dir, rel, want):
    """cmp с банком: файл должен быть его побайтовой копией."""
    name = os.path.basename(rel)
    bank = os.path.join(REPO, "03-sound", "sounds", "block", name)
    packed = os.path.join(extract_dir, SOUND_PREFIX, rel)
    if not os.path.exists(packed):
        print(f"  ✗ {name}: НЕТ в пакете")
        fail.append(f"{name}: отсутствует в пакете")
        return
    got = sha256(packed)
    same_bank = os.path.exists(bank) and sha256(bank) == got
    mark = "✓" if got == want and same_bank else "✗"
    print(f"  {mark} {name}: {got[:16]}…  банк {'совпал' if same_bank else 'РАСХОЖДЕНИЕ'}"
          f"  размер {os.path.getsize(packed)} Б")
    if got != want:
        fail.append(f"{name}: хеш {got[:16]}… ≠ эталон {want[:16]}…")
    elif not same_bank:
        fail.append(f"{name}: не побайтовая копия банка")


def check_png(extract_dir, rel, want):
    name = os.path.basename(rel)
    packed = os.path.join(extract_dir, TEX_PREFIX, rel)
    if not os.path.exists(packed):
        print(f"  ✗ {name}: НЕТ в пакете")
        fail.append(f"{name}: отсутствует в пакете")
        return
    got = sha256(packed)
    mark = "✓" if got == want else "✗"
    print(f"  {mark} {name}: {got[:16]}…")
    if got != want:
        fail.append(f"{name}: хеш расходится")


def check_manifest(extract_dir, manifest):
    """sha256sum -c по манифесту пакета."""
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
                continue
            if sha256(p) == want:
                ok += 1
            else:
                bad += 1
                print(f"    расхождение: {rel}")
    print(f"  {'✓' if bad == 0 and miss == 0 else '✗'} манифест: "
          f"совпало {ok}, расхождений {bad}, отсутствует {miss}")
    if bad or miss:
        fail.append(f"манифест: расхождений {bad}, отсутствует {miss}")


def main():
    zip_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ZIP
    manifest = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MANIFEST

    if not os.path.exists(zip_path):
        print(f"Пакет не найден: {zip_path}", file=sys.stderr)
        return 2

    print(f"Пакет:    {os.path.relpath(zip_path, REPO)}")
    print(f"Размер:   {os.path.getsize(zip_path)} Б")
    print(f"SHA-256:  {sha256(zip_path)}")
    print()

    tmp = tempfile.mkdtemp(prefix="accept353_")
    try:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp)
            n = len(z.namelist())
        print(f"Распаковано {n} записей во временный каталог.")
        print()

        print("1) Звуки R1 — сравнение с банком 03-sound/sounds/")
        for rel, want in SOUNDS.items():
            check_sound(tmp, rel, want)
        print()

        print("2) Манифест пакета (sha256sum -c)")
        check_manifest(tmp, manifest)
        print()

        print("3) Текстуры Д6 — сверка с принятой сдачей Художника")
        for rel, want in FLESH.items():
            check_png(tmp, rel, want)
        print()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fail:
        print(f"ИТОГ: НЕ ПРИНЯТО — расхождений {len(fail)}")
        for x in fail:
            print(f"  • {x}")
        print("\nMerge в main и релиз v3.5.3 запрещены.")
        return 1
    print("ИТОГ: ПРИНЯТО — все проверки пройдены.")
    print("Дальше: CI на новом коммите → merge в main → релиз v3.5.3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
