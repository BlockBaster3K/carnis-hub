#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sounds_json_semantic.py — проверка смысла правки sounds.json (S17/T-3202).

Зачем: гейт приёмки разрешал файл `sounds.json` целиком (`--allow`). Значит
через дельту могло пройти что угодно: удалённое событие, смена набора файлов
у события, подмена на чужой звук. Ревизор и Кодер указали на это независимо
(«прежний gate способен пропустить удаление события/смену набора файлов»).

Правило S17 узкое: в `sounds.json` 3.7.3 к 3.7.2 добавлены **привязки**
(события ссылаются на файлы), громкость одного события поправлена намеренно.
Всё остальное — не разрешено.

Что проверяется (сравнение нового пакета с эталоном 3.7.2):
  1. Набор событий: не удалено ни одного, не добавлено ни одного.
  2. Для каждого события — набор файлов (`sounds[].name`) тот же.
  3. Из полей события меняться может только `sounds[].volume`.
  4. Провал, если что-то ещё отличается.

Код возврата: 0 — правка укладывается в S17; 2 — выходит за рамки; 1 — ошибка.
"""
import json
import os
import sys
import zipfile

REL = "src/main/resources/assets/carnis/sounds.json"
PREV = os.path.join("01-coder", "3.7.2", "project-3.7.2-clean.zip")


def load(z, name):
    """Достать и разобрать sounds.json из zip (None, если файла нет)."""
    try:
        raw = z.read(name)
    except KeyError:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None


def names_of(spec):
    """Набор файлов события: список `sounds[].name` по порядку."""
    out = []
    for s in (spec.get("sounds") or []) if isinstance(spec, dict) else []:
        if isinstance(s, dict):
            out.append(s.get("name"))
        else:
            out.append(s)
    return out


def volumes_of(spec):
    """Значения volume по индексам — единственное, что можно менять."""
    out = []
    for s in (spec.get("sounds") or []) if isinstance(spec, dict) else []:
        out.append(s.get("volume") if isinstance(s, dict) else None)
    return out


def strip_volumes(spec):
    """Копия события без volume — должна совпадать целиком."""
    clean = {}
    for key, val in spec.items():
        if key == "sounds" and isinstance(val, list):
            clean[key] = [
                {k: v for k, v in s.items() if k != "volume"}
                if isinstance(s, dict) else s
                for s in val
            ]
        else:
            clean[key] = val
    return clean


def compare(old, new):
    """Вернуть список нарушений S17."""
    bad = []
    if old is None or new is None:
        return ["sounds.json не разобран в одном из пакетов — сравнить нельзя"]

    old_ev = set(old)
    new_ev = set(new)
    for ev in sorted(old_ev - new_ev):
        bad.append("событие УДАЛЕНО: %s" % ev)
    for ev in sorted(new_ev - old_ev):
        bad.append("событие ДОБАВЛЕНО вне S17: %s" % ev)

    for ev in sorted(old_ev & new_ev):
        o, n = old[ev], new[ev]
        if not isinstance(o, dict) or not isinstance(n, dict):
            if o != n:
                bad.append("%s: событие не объект и изменилось" % ev)
            continue
        on, nn = names_of(o), names_of(n)
        if on != nn:
            bad.append("%s: набор файлов изменён (%s -> %s)"
                       % (ev, on, nn))
            continue
        # Всё, кроме volume, обязано совпасть.
        if strip_volumes(o) != strip_volumes(n):
            diffs = sorted(k for k in set(strip_volumes(o)) | set(strip_volumes(n))
                           if strip_volumes(o).get(k) != strip_volumes(n).get(k))
            bad.append("%s: изменены поля вне volume: %s" % (ev, ", ".join(diffs)))
        ov, nv = volumes_of(o), volumes_of(n)
        for i, (a, b) in enumerate(zip(ov, nv)):
            if a != b:
                print("  · %s[%d]: volume %s -> %s (разрешено S17)"
                      % (ev, i, a, b))
    return bad


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    pkg = sys.argv[1]
    prev = PREV
    if "--prev" in sys.argv:
        prev = sys.argv[sys.argv.index("--prev") + 1]
    if not os.path.isfile(pkg) or not os.path.isfile(prev):
        print("ОШИБКА: нет пакета или эталона (%s | %s)" % (pkg, prev))
        return 1

    with zipfile.ZipFile(prev) as zp:
        old = load(zp, REL)
    with zipfile.ZipFile(pkg) as zn:
        new = load(zn, REL)

    print("Смысловая проверка sounds.json (S17/T-3202)")
    print("  было событий: %s, стало: %s"
          % (len(old) if old else "—", len(new) if new else "—"))
    bad = compare(old, new)
    if bad:
        print()
        print("ВНЕ S17 (%d):" % len(bad))
        for b in bad:
            print("  ✗ %s" % b)
        print()
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — правка sounds.json выходит за S17")
        return 2
    print()
    print("ИТОГ: СХОДИТСЯ — события и наборы файлов те же, менялись только "
          "громкости")
    return 0


if __name__ == "__main__":
    sys.exit(main())
