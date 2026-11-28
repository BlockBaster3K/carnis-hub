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


# S131: варианты мобов 3.8.1 — СОЗНАТЕЛЬНОЕ добавление событий, а не «правка
# вне S17». Белый список по префиксу, а не «любое новое событие разрешено»:
# иначе тест перестаёт ловить настоящие случайные добавления. Расширять только
# вместе с задачей, где появление событий объявлено (сейчас — промпт Архитектора
# sound_prompt_submit_381.md, задача S131).
NEW_EVENTS_ALLOWED_PREFIXES = (
    "entity.infected_zombie_scythed.",
    "entity.infected_zombie_ripper.",
    "entity.infected_skeleton_sniper.",
    "entity.infected_skeleton_impaler.",
    "entity.infected_spider_arachnid.",
    "entity.infected_spider_crusher.",
    "entity.infected_creeper_mortar.",
    "entity.infected_creeper_charger.",
)


def allowed_new_event(ev):
    return ev.startswith(NEW_EVENTS_ALLOWED_PREFIXES)


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
        if allowed_new_event(ev):
            continue
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
        # Поля события (кроме sounds) обязаны совпасть.
        so = {k: v for k, v in o.items() if k != "sounds"}
        sn = {k: v for k, v in n.items() if k != "sounds"}
        if so != sn:
            diffs = sorted(k for k in set(so) | set(sn) if so.get(k) != sn.get(k))
            bad.append("%s: изменены поля события вне volume: %s"
                       % (ev, ", ".join(diffs)))
        # Внутри каждого элемента sounds[] разрешён ровно один ключ — volume.
        for i, (a, b) in enumerate(zip(o.get("sounds") or [],
                                       n.get("sounds") or [])):
            if not isinstance(a, dict) or not isinstance(b, dict):
                continue
            for key in sorted(set(a) | set(b)):
                if key == "volume":
                    continue
                if a.get(key) != b.get(key):
                    bad.append("%s[%d]: поле %s вне S17: %r -> %r"
                               % (ev, i, key, a.get(key), b.get(key)))
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
    # ⚠ Раньше итог печатал «события и наборы файлов те же» ВСЕГДА при пустом
    # списке нарушений, в том числе когда события добавлялись по белому списку:
    # строка «было 214, стало 241» и вывод «те же» стояли рядом. Теперь итог
    # называет, что именно произошло, чтобы зелёный прогон нельзя было принять
    # за «ничего не менялось».
    added = sorted(set(new) - set(old)) if (old is not None and new is not None) else []
    bad = compare(old, new)
    if not bad and added:
        print()
        print("ДОБАВЛЕНО ПО БЕЛОМУ СПИСКУ S131 (%d):" % len(added))
        for ev in added:
            print("  + %s" % ev)
    if bad:
        print()
        print("ВНЕ S17 (%d):" % len(bad))
        for b in bad:
            print("  ✗ %s" % b)
        print()
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — правка sounds.json выходит за S17")
        return 2
    print()
    if added:
        print("ИТОГ: СХОДИТСЯ — громкости в норме, %d событий добавлено по "
              "белому списку S131" % len(added))
    else:
        print("ИТОГ: СХОДИТСЯ — события и наборы файлов те же, менялись только "
              "громкости")
    return 0


if __name__ == "__main__":
    sys.exit(main())
