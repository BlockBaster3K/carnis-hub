#!/usr/bin/env python3
"""Сверка банка звуков: манифесты против диска + поиск мёртвых дублей.

Использование: python3 tools/sound_check.py [каталог_банка]
Каталог по умолчанию: /home/user/hub5/03-sound

Проверяет:
  * SHA256SUMS_all.txt  — каждая запись совпадает с диском;
  * MANIFEST_ogg.txt    — пути и размеры совпадают с диском;
  * SHA256SUMS_wave22.txt — записи совпадают с диском (пути от каталога банка);
  * каждый .ogg на диске присутствует хотя бы в одном манифесте;
  * файлы с одинаковым SHA (побайтовые дубли) — предупреждение.
"""
import hashlib
import os
import sys
from collections import defaultdict

BANK = sys.argv[1] if len(sys.argv) > 1 else "/home/user/hub5/03-sound"
SOUNDS = os.path.join(BANK, "sounds")

fail = 0


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_ogg():
    out = []
    for dp, _, names in os.walk(SOUNDS):
        for n in names:
            if n.endswith(".ogg"):
                full = os.path.join(dp, n)
                out.append((os.path.relpath(full, SOUNDS), full))
    return sorted(out)


files = disk_ogg()
print(f"банк: {BANK}")
print(f"файлов .ogg на диске: {len(files)}\n")

listed = defaultdict(set)

# --- 1. SHA256SUMS_all.txt ---
p = os.path.join(BANK, "SHA256SUMS_all.txt")
if os.path.exists(p):
    ok = bad = miss = 0
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        want, rel = line.split(None, 1)
        rel = rel.strip()
        listed[rel].add("all")
        full = os.path.join(SOUNDS, rel)
        if not os.path.exists(full):
            miss += 1
            print(f"  ОТСУТСТВУЕТ: {rel}")
        elif sha(full) != want:
            bad += 1
            print(f"  ХЕШ НЕ СОВПАЛ: {rel}")
        else:
            ok += 1
    print(f"SHA256SUMS_all.txt:  записей {ok+bad+miss}, совпало {ok}, "
          f"расхождений {bad}, отсутствует {miss}")
    fail += bad + miss
else:
    print("SHA256SUMS_all.txt: файла нет")

# --- 2. MANIFEST_ogg.txt ---
p = os.path.join(BANK, "MANIFEST_ogg.txt")
if os.path.exists(p):
    ok = bad = miss = 0
    for i, line in enumerate(open(p, encoding="utf-8")):
        line = line.strip()
        if not line or i == 0:
            continue
        rel, size = line.rsplit("|", 1)
        rel, size = rel.strip(), int(size.strip())
        listed[rel].add("manifest")
        full = os.path.join(SOUNDS, rel)
        if not os.path.exists(full):
            miss += 1
            print(f"  ОТСУТСТВУЕТ: {rel}")
        elif os.path.getsize(full) != size:
            bad += 1
            print(f"  РАЗМЕР НЕ СОВПАЛ: {rel} ({os.path.getsize(full)} != {size})")
        else:
            ok += 1
    print(f"MANIFEST_ogg.txt:    записей {ok+bad+miss}, совпало {ok}, "
          f"расхождений {bad}, отсутствует {miss}")
    fail += bad + miss
else:
    print("MANIFEST_ogg.txt: файла нет")

# --- 3. SHA256SUMS_wave22.txt ---
p = os.path.join(BANK, "SHA256SUMS_wave22.txt")
if os.path.exists(p):
    ok = bad = miss = 0
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        want, rel = line.split(None, 1)
        rel = rel.strip()
        if rel.startswith("sounds/"):
            rel = rel[len("sounds/"):]
        listed[rel].add("wave22")
        full = os.path.join(SOUNDS, rel)
        if not os.path.exists(full):
            miss += 1
            print(f"  ОТСУТСТВУЕТ: {rel}")
        elif sha(full) != want:
            bad += 1
            print(f"  ХЕШ НЕ СОВПАЛ: {rel}")
        else:
            ok += 1
    print(f"SHA256SUMS_wave22.txt: записей {ok+bad+miss}, совпало {ok}, "
          f"расхождений {bad}, отсутствует {miss}")
    fail += bad + miss

# --- 4. файлы на диске, не попавшие ни в один манифест ---
orphan = [rel for rel, _ in files if rel not in listed]
if orphan:
    print(f"\nНЕ УЧТЕНЫ в манифестах ({len(orphan)}):")
    for o in orphan:
        print(f"  {o}")
else:
    print("\nвсе файлы учтены хотя бы в одном манифесте")

# --- 5. побайтовые дубли ---
by_sha = defaultdict(list)
for rel, full in files:
    by_sha[sha(full)].append(rel)
dups = {k: v for k, v in by_sha.items() if len(v) > 1}
if dups:
    print(f"\nПОБАЙТОВЫЕ ДУБЛИ ({len(dups)}):")
    for k, v in dups.items():
        print(f"  {k[:16]}… → {', '.join(v)}")
else:
    print("побайтовых дублей нет")

print(f"\nИТОГ: {'ошибок ' + str(fail) if fail else 'все проверки пройдены'}")
sys.exit(1 if fail else 0)
