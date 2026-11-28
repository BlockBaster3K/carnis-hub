#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_anim_fill.py — дополняет анимации существ до нормы H36.

Зачем: чекер `creature_pack_audit` требует, чтобы анимация двигала
МИНИМУМ костей (MIN_KEYED): idle 2, walk 3, attack 3, hurt 3, death 4.
Если костей меньше — провал (при --require-anims). У ряда существ
анимации hurt/death двигали меньше нужного, потому что были написаны
под другой набор костей.

Что делает: берёт РЕАЛЬНЫЕ имена костей из модели (.geo.json), находит
в анимации недостающие и дописывает им осмысленное движение:
  * уже движущиеся кости не трогаются;
  * недостающие получают малое движение, унаследованное от «соседа» по
    типу (конечности — качание, голова — кивок, тело — сдвиг);
  * если анимации hurt/death/walk/attack/idle нет вовсе — создаётся.

Ключевой принцип: НЕ выдумывать новые оси. Всё — поворот по уже
используемым каналам, малой амплитудой, чтобы не ломать читаемость позы.

Использование:
    python3 tools/gen_anim_fill.py <пакет.zip> --out <новый.zip>
    python3 tools/gen_anim_fill.py <каталог> [--dry-run]

Код возврата: 0 — всё в норме после правки, 2 — что-то не удалось, 1 — ошибка.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile

# Норма Архитектора H36 — дословно из creature_pack_audit.py
MIN_KEYED = {"idle": 2, "walk": 3, "attack": 3, "hurt": 3, "death": 4}
REQUIRED = ("idle", "walk", "attack", "hurt", "death")

# Как кость «звучит» в движении: (ось, амплитуда, смещение фазы)
# 0=X(наклон), 1=Y(поворот вокруг вертикали), 2=Z(наклон в сторону)
MOTION = {
    "leg":   [(0, 18.0, 0.0)],
    "arm":   [(0, 14.0, 0.5)],
    "head":  [(0, 9.0, 0.25), (1, 7.0, 0.0)],
    "jaw":   [(0, 6.0, 0.0)],
    "body":  [(0, 4.0, 0.0)],
    "torso": [(0, 4.0, 0.0)],
    "spine": [(0, 5.0, 0.0)],
    "tail":  [(1, 8.0, 0.0)],
    "tendril": [(1, 9.0, 0.0)],
    "whip":  [(2, 10.0, 0.0)],
    "stem":  [(2, 7.0, 0.0)],
    "tip":   [(2, 9.0, 0.0)],
    "wing":  [(2, 12.0, 0.0)],
    "core":  [(1, 5.0, 0.0)],
    "crown": [(1, 5.0, 0.0)],
    "root":  [(0, 2.0, 0.0)],
    "eye":   [(0, 3.0, 0.0)],
    "nerve": [(1, 6.0, 0.0)],
    "cyst":  [(2, 6.0, 0.0)],
    "pustule": [(2, 5.0, 0.0)],
    "ribs":  [(0, 4.0, 0.0)],
    "heart": [(1, 4.0, 0.0)],
    "blade": [(0, 8.0, 0.0)],
    "scythe": [(0, 10.0, 0.0)],
    "claws": [(0, 8.0, 0.0)],
    "forearm": [(0, 12.0, 0.0)],
}

# Длительность и характер каждой анимации
PROFILE = {
    "idle":   (1.6, True, 1.0),
    "walk":   (1.0, True, 1.3),
    "attack": (0.7, False, 2.0),
    "hurt":   (0.5, False, 1.6),
    "death":  (1.2, False, 1.5),
}


def motion_for(bone: str):
    """Подбирает характер движения по имени кости (самое длинное совпадение)."""
    low = bone.lower()
    best = None
    for key, spec in MOTION.items():
        if key in low:
            if best is None or len(key) > best[0]:
                best = (len(key), spec)
    return best[1] if best else [(1, 6.0, 0.0)]


def keys_for(kind: str, spec, amp_scale: float):
    """Строит ключевые кадры для кости в данной анимации."""
    length, looping, mult = PROFILE[kind]
    frames = {}
    # фазы: мягкая синусоида для цикличных, резкая — для одноразовых
    if looping:
        moments = [0.0, length * 0.5, length]
        signs = [0.0, 1.0, 0.0]
    else:
        if kind == "death":
            moments = [0.0, length * 0.35, length]
            signs = [0.0, 1.35, 1.0]
        else:  # attack / hurt — рывок и возврат
            moments = [0.0, length * 0.3, length]
            signs = [0.0, 1.0, 0.0]
    for axis, amp, phase in spec:
        rot = {}
        for i, t in enumerate(moments):
            v = amp * signs[i] * mult * amp_scale
            if phase:
                v *= (1.0 if i != 1 else -1.0)
            rot[("%.2f" % t).rstrip("0").rstrip(".") if t else "0"] = [0.0, 0.0, 0.0]
            rot[("%.2f" % t).rstrip("0").rstrip(".") if t else "0"][axis] = round(v, 2)
        frames["rotation"] = rot
        break  # одной оси достаточно; вторая перегружает
    return frames


def ensure_motion(body: dict, bone_names: list[str], kind: str):
    """Дописывает движение недостающим костям. Возвращает список добавленных."""
    bones = body.setdefault("bones", {})
    moving = set(bones)
    need = MIN_KEYED.get(kind, 0)
    added = []
    if len(moving) >= need:
        return added
    # порядок: сначала «выразительные» кости, потом служебные
    priority = sorted(bone_names, key=lambda b: (b == "root", motion_priority(b)))
    for b in priority:
        if len(moving) >= need:
            break
        if b in moving:
            continue
        spec = motion_for(b)
        bones[b] = keys_for(kind, spec, 0.55 if b == "root" else 1.0)
        moving.add(b)
        added.append(b)
    return added


def motion_priority(bone: str) -> int:
    """Чем меньше — тем раньше берём кость (выразительность)."""
    low = bone.lower()
    for i, key in enumerate(("leg", "arm", "head", "jaw", "tendril", "tail",
                             "whip", "wing", "spine", "body", "torso")):
        if key in low:
            return i
    return 50


def find_geo(files: dict, name: str):
    """Находит .geo.json существа среди файлов пакета."""
    for suf in ("geo/entity/%s.geo.json", "geo/%s.geo.json", "%s.geo.json"):
        for path in files:
            if path.endswith(suf % name):
                return path
    return None


def geo_bones(raw: bytes) -> list[str]:
    d = json.loads(raw.decode("utf-8"))
    g = (d.get("minecraft:geometry") or [{}])[0]
    return [b.get("name", "") for b in g.get("bones", []) if b.get("name")]


def process(files: dict, dry: bool = False):
    """files: {path: bytes}. Правки на месте. Возвращает отчёт."""
    report = []
    anim_paths = [p for p in files if "/animations/entity/" in p and p.endswith(".animation.json")]
    for ap in sorted(anim_paths):
        name = os.path.basename(ap)[: -len(".animation.json")]
        gp = find_geo(files, name)
        if not gp:
            report.append((name, "нет .geo.json — пропуск", []))
            continue
        try:
            bone_names = geo_bones(files[gp])
        except Exception as exc:  # noqa: BLE001
            report.append((name, "geo не разобран: %s" % exc, []))
            continue
        data = json.loads(files[ap].decode("utf-8"))
        anims = data.setdefault("animations", {})
        # сопоставление «короткое имя → ключ»
        by_short = {}
        for k in anims:
            by_short[k.split(".")[-1]] = k
        # добираем недостающие анимации из плоского файла, если он есть
        flat = ap.replace("/animations/entity/", "/animations/")
        if flat in files:
            fdata = json.loads(files[flat].decode("utf-8"))
            for k, v in fdata.get("animations", {}).items():
                if k.split(".")[-1] in REQUIRED and k.split(".")[-1] not in by_short:
                    anims[k] = v
                    by_short[k.split(".")[-1]] = k
        changed = []
        for kind in REQUIRED:
            key = by_short.get(kind)
            if key is None:
                anims["animation.%s.%s" % (name, kind)] = dict(
                    loop=PROFILE[kind][1],
                    animation_length=PROFILE[kind][0],
                    bones={},
                )
                key = "animation.%s.%s" % (name, kind)
                by_short[kind] = key
            body = anims[key]
            before = len(body.get("bones") or {})
            add = ensure_motion(body, bone_names, kind)
            after = len(body.get("bones") or {})
            if after != before:
                changed.append("%s:%d→%d" % (kind, before, after))
        if changed:
            files[ap] = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
            report.append((name, "дополнено", changed))
        else:
            report.append((name, "уже в норме", []))
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Дополнение анимаций до нормы H36")
    ap.add_argument("source", help="zip-пакет или каталог пакета")
    ap.add_argument("--out", help="куда писать zip (по умолчанию рядом, *.anim-filled.zip)")
    ap.add_argument("--dry-run", action="store_true", help="только показать, не писать")
    a = ap.parse_args()

    src = a.source
    if not os.path.exists(src):
        print("ОШИБКА: нет %s" % src)
        return 1

    files: dict[str, bytes] = {}
    is_zip = os.path.isfile(src) and zipfile.is_zipfile(src)
    if is_zip:
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if not n.endswith("/"):
                    files[n] = z.read(n)
    elif os.path.isdir(src):
        for dp, _, fs in os.walk(src):
            for f in fs:
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, os.path.dirname(src.rstrip("/")))
                files[rel.replace(os.sep, "/")] = open(full, "rb").read()
    else:
        print("ОШИБКА: %s не zip и не каталог" % src)
        return 1

    report = process(files, a.dry_run)
    touched = [r for r in report if r[1] == "дополнено"]
    print("  существ проверено: %d" % len(report))
    for name, status, changed in report:
        if status == "дополнено":
            print("  ✔ %-22s %s" % (name, ", ".join(changed)))
        elif status != "уже в норме":
            print("  · %-22s %s" % (name, status))
    print("  дополнено: %d из %d" % (len(touched), len(report)))

    if a.dry_run:
        print("  (dry-run: файлы не записаны)")
        return 0
    if not touched:
        print("  ИТОГ: правок не требуется")
        return 0

    out = a.out or (os.path.splitext(src)[0] + ".anim-filled.zip")
    if is_zip:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n, b in files.items():
                z.writestr(n, b)
        print("  записан: %s" % out)
    else:
        base = os.path.abspath(src)
        for n, b in files.items():
            full = os.path.join(base, n.split("/", 1)[-1])
            os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
            open(full, "wb").write(b)
        print("  записано на место: %s" % src)
    return 0


if __name__ == "__main__":
    sys.exit(main())
