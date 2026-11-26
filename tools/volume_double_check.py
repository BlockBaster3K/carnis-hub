#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""volume_double_check.py — двойное применение громкости (R24, §4 вердикта).

Зачем. Ревизор в вердикте по 3.7.3 написал: «Громкость события задаётся в
одном месте — в коде. `sounds.json` держит `volume` 1.0 или не держит вовсе.
Ненулевой множитель в JSON при ненулевой громкости в коде = двойное
применение, дефект». И добавил: «проверка системная, а не выборочная — я видел
только этот [hive.detail_flow], но проверка должна быть по всему банку».

Это и есть системная проверка. Она сравнивает два множества:

  A. события, для которых КОД передаёт громкость != 1.0 в playSound;
  B. события, у которых `sounds.json` задаёт `volume` != 1.0.

Пересечение — двойное применение: множители перемножаются. Особый случай —
расхождение значений (код 0.2, JSON 0.45): это не «двойное», а
**несогласованная пара**, и её тоже надо назвать, потому что итог не равен
ни одному из задуманных.

Оговорка, которую обязан назвать вслух: если код играет событие без громкости
(вариант `playSound(x,y,z,ev,src)` без float), громкость берётся из JSON — это
НОРМА, а не дефект. Поэтому проверка ищет только пересечение.

Код возврата: 0 — пересечений нет; 2 — есть; 1 — ошибка входа.
"""
import json
import os
import re
import sys
import zipfile

SOUNDS_JSON = "src/main/resources/assets/carnis/sounds.json"


def read_pkg(src):
    """Вернуть (sounds.json как dict, {имя файла: текст java})."""
    if os.path.isdir(src):
        sj = os.path.join(src, SOUNDS_JSON)
        if not os.path.isfile(sj):
            return None, {}
        data = json.load(open(sj, encoding="utf-8"))
        java = {}
        for dp, _, fs in os.walk(src):
            for f in fs:
                if f.endswith(".java"):
                    p = os.path.join(dp, f)
                    java[f] = open(p, encoding="utf-8",
                                   errors="replace").read()
        return data, java
    with zipfile.ZipFile(src) as z:
        data = json.loads(z.read(SOUNDS_JSON).decode("utf-8"))
        java = {n.split("/")[-1]: z.read(n).decode("utf-8", "replace")
                for n in z.namelist() if n.endswith(".java")}
    return data, java


def const_to_key(java):
    """ModSounds.КОНСТАНТА -> ключ события в sounds.json."""
    src = java.get("ModSounds.java", "")
    out = {}
    # ХИТРЫЙ МОМЕНТ: два вида объявления —
    #   ИМЯ = registerVariableRangeSound("ключ");
    #   ИМЯ = ModSounds.register("ключ") / register("ключ")
    for m in re.finditer(r'\b([A-Z][A-Z0-9_]*)\s*=\s*'
                         r'(?:MOD?SOUNDS\.)?(?:registerVariableRangeSound|'
                         r'register|registerSound)\s*\(\s*"([^"]+)"', src):
        out[m.group(1)] = m.group(2)
    # и обычная форма пары строк: ИМЯ =\n ... register("ключ")
    for m in re.finditer(r'\b([A-Z][A-Z0-9_]*)\s*=\s*[^;]{0,80}?\(\s*"([^"]+)"',
                         src):
        out.setdefault(m.group(1), m.group(2))
    return out


def helper_consts(java):
    """Имя функции-выборщика -> константы ModSounds, которые она возвращает.

    Зачем (поймано на 3.7.3): `HiveAmbientSoundHandler` играет `selectHiveDetail(level)`
    с громкостью 0,30F — и это ЧЕТЫРЕ разных события, выбираемых по зоне, плюс
    пятое (FLOW) с `volume 1.5` в JSON. Прямой поиск `ModSounds.X.get()` внутри
    `playLocalSound` такие случаи не видит и даёт ложно-зелёный результат.
    """
    out = {}
    for _fn, src in java.items():
        for m in re.finditer(r'SoundEvent\s+(\w+)\s*\([^)]*\)\s*\{', src):
            name = m.group(1)
            body = src[m.end():m.end() + 1200]
            consts = set(re.findall(r'ModSounds\.([A-Z][A-Z0-9_]*)\.get\(\)',
                                    body))
            if consts:
                out[name] = consts
    return out


def code_volumes(java):
    """Событие -> множество громкостей, переданных кодом (кроме 1.0)."""
    c2k = const_to_key(java)
    helpers = helper_consts(java)
    out = {}

    def add(key, fn, vol):
        if key:
            out.setdefault(key, set()).add((fn, vol))

    for fn, src in java.items():
        for m in re.finditer(r'play(?:Local)?Sound\(([^;]{0,300})\)', src):
            body = m.group(1)
            nums = re.findall(r'(\d+(?:\.\d+)?)F', body)
            if not nums:
                continue
            vol = float(nums[-2]) if len(nums) >= 2 else float(nums[0])
            if abs(vol - 1.0) < 1e-9:
                continue
            const = re.search(r'ModSounds\.([A-Z][A-Z0-9_]*)\.get\(\)', body)
            if const:
                add(c2k.get(const.group(1)), fn, vol)
                continue
            # Аргумент события — вызов локального выборщика. Искать надо именно
            # в позиции аргумента: до него в теле стоят getX()/getY(), и первая
            # же найденная «функция» оказывается не той (поймано отладкой).
            # Разбираю аргументы по запятым: третий-четвёртый — событие.
            # Аргумент может быть (а) прямым `ModSounds.X.get()`, (б) вызовом
            # локального выборщика `selectHiveDetail(level)`, (в) ЛОКАЛЬНОЙ
            # ПЕРЕМЕННОЙ, которой присвоен выборщик. Вариант (в) мой первый
            # вариант не видел вовсе — и дал ложно-зелёный по
            # hive.detail_flow (0.30 в коде × 1.5 в JSON = 0.45).
            args = [a.strip() for a in body.split(",")]
            for arg in args[:5]:
                for call in re.finditer(r'\b(\w+)\s*\(', arg):
                    if call.group(1) in helpers:
                        for name in helpers[call.group(1)]:
                            add(c2k.get(name), fn, vol)
                        break
                var = re.fullmatch(r'(\w+)', arg)
                if var:
                    assigned = re.search(r'\b' + re.escape(var.group(1)) +
                                         r'\s*=\s*(\w+)\s*\(', src)
                    if assigned and assigned.group(1) in helpers:
                        for name in helpers[assigned.group(1)]:
                            add(c2k.get(name), fn, vol)
    return out


def json_volumes(data):
    """Событие -> множество volume из sounds.json (кроме 1.0 и None)."""
    out = {}
    for ev, spec in (data or {}).items():
        if not isinstance(spec, dict):
            continue
        vols = set()
        for s in spec.get("sounds") or []:
            if isinstance(s, dict) and s.get("volume") is not None:
                v = float(s["volume"])
                if abs(v - 1.0) >= 1e-9:
                    vols.add(v)
        if vols:
            out[ev] = vols
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    if not os.path.exists(src):
        print("ОШИБКА: нет пакета или каталога: %s" % src)
        return 1
    try:
        data, java = read_pkg(src)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print("ОШИБКА: пакет не прочитан (%s)" % exc)
        return 1
    if data is None or not java:
        print("ОШИБКА: нет sounds.json или .java — проверить нечего")
        return 1

    code = code_volumes(java)
    js = json_volumes(data)
    print("Громкость: двойное применение (R24 §4)")
    print("  событий с громкостью в КОДЕ != 1.0: %d" % len(code))
    print("  событий с volume в JSON != 1.0:      %d" % len(js))

    both = sorted(set(code) & set(js))
    if not both:
        print()
        print("ИТОГ: СХОДИТСЯ — ни одно событие не задаёт громкость в двух "
              "местах одновременно")
        return 0

    print()
    print("ДВОЙНОЕ ПРИМЕНЕНИЕ (%d):" % len(both))
    for ev in both:
        cv = sorted({v for _f, v in code[ev]})
        jv = sorted(js[ev])
        same = len(cv) == 1 and len(jv) == 1 and abs(cv[0] - jv[0]) < 1e-9
        eff = ["%.3f" % (a * b) for a in cv for b in jv]
        print("  %s ✗ %s" % ("=" if same else "↯", ev))
        print("      код: %s | JSON: %s | итог: %s"
              % (cv, jv, ", ".join(eff)))
        for fn, v in sorted(code[ev]):
            print("      · %s передаёт %.3f" % (fn, v))
    print()
    print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — %d событий задают громкость в двух местах"
          % len(both))
    return 2


if __name__ == "__main__":
    sys.exit(main())
