#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""deps_soft_check.py — I102/R102: зависимости мягкие, сборка без них возможна.

Зачем: в 3.8.0 заявлены пять библиотек Директора — Curios, Patchouli,
SmartBrainLib, Lodestone, Sound Physics. Если любая попадёт в `build.gradle`
как жёсткая (`modImplementation`/`implementation` с `fg.deobf`), сборка
начнёт требовать её в Classpath, и проект без неё **не соберётся**. Игрок
тогда получает краш, а не «работает без необязательного».

Проверяется по байтам пакета, без доверия отчёту:
  1. Пять библиотек не должны быть ЖЁСТКИМИ зависимостями `build.gradle`.
  2. GeckoLib — наоборот, обязан быть жёстким (это требование R23 п.5:
     `mandatory=true` только у него, и без него геометрия не рисуется).
  3. Если библиотека всё же объявлена, она обязана быть `compileOnly`
     или `runtimeOnly` (мягко) — тогда сборка без неё пройдёт.

Код возврата: 0 — мягко; 2 — есть жёсткая зависимость; 1 — ошибка входа.
"""
import os
import re
import sys
import zipfile

SOFT_LIBS = {
    "curios": "Curios",
    "patchouli": "Patchouli",
    "smartbrainlib": "SmartBrainLib",
    "lodestone": "Lodestone",
    "soundphysics": "Sound Physics",
}
HARD = ("modImplementation", "implementation", "modCompileOnly_never",
        "api")
SOFT = ("compileOnly", "runtimeOnly")


def read_gradle(src):
    """Вернуть текст build.gradle (zip или каталог)."""
    if os.path.isdir(src):
        for rel in ("build.gradle", "src/build.gradle"):
            p = os.path.join(src, rel)
            if os.path.isfile(p):
                return open(p, encoding="utf-8", errors="replace").read()
        return None
    with zipfile.ZipFile(src) as z:
        for name in z.namelist():
            if name == "build.gradle" or name.endswith("/build.gradle"):
                return z.read(name).decode("utf-8", "replace")
    return None


def dependency_lines(text):
    """Строки блока dependencies, где объявлена зависимость."""
    out = []
    inside = False
    for raw in text.splitlines():
        line = raw.split("//")[0].strip()
        if re.match(r"^dependencies\s*\{", line):
            inside = True
            continue
        if inside and line == "}":
            inside = False
            continue
        if inside and line:
            out.append(line)
    return out


def classify(line):
    """('hard'|'soft'|'other', ключ зависимости или None)."""
    low = line.lower()
    key = next((k for k in SOFT_LIBS if k in low), None)
    if key is None:
        return "other", None
    # head — только имя конфигурации Gradle: до пробела/кавычки/скобки.
    head = re.split(r"[\s\"'(]", low.strip(), 1)[0]
    # Сравнение регистронезависимое: SOFT/HARD записаны в camelCase, а head
    # приведён к нижнему — без .lower() мягкое объявление считалось жёстким
    # (поймано негативом: compileOnly давал код 2).
    if any(head.startswith(s.lower()) for s in SOFT):
        return "soft", key
    if any(head.startswith(h.lower()) for h in HARD
           if h != "modCompileOnly_never"):
        return "hard", key
    # ключ совпал, но объявление незнакомое — это НЕ «мягко». Fail-closed:
    # неизвестный способ объявления трактуем как жёсткий, иначе чекер молчит
    # на новой форме записи (проверено: `modImplementation ... curios-forge`
    # раньше проходил как «ок»).
    return "hard", key


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    if not os.path.exists(src):
        print("ОШИБКА: нет файла или каталога: %s" % src)
        return 1
    text = read_gradle(src)
    if text is None:
        print("ОШИБКА: в %s нет build.gradle — проверить нечего" % src)
        return 1

    lines = dependency_lines(text)
    print("Зависимости мягкие (I102/R102)")
    print("  строк в блоке dependencies: %d" % len(lines))

    hard = []
    soft = []
    for line in lines:
        kind, key = classify(line)
        if kind == "hard":
            hard.append((SOFT_LIBS[key], line))
        elif kind == "soft":
            soft.append((SOFT_LIBS[key], line))

    for name, line in soft:
        print("  ✓ %-14s мягкая: %s" % (name, line[:70]))
    for name, line in hard:
        print("  ✗ %-14s ЖЁСТКАЯ: %s" % (name, line[:70]))

    # GeckoLib обязан быть жёстким: без него не рисуется геометрия.
    gecko_hard = any("geckolib" in ln.lower()
                     and not ln.lower().startswith(SOFT)
                     for ln in lines)
    print("  %s GeckoLib жёсткий (обязан быть: R23 п.5)"
          % ("✓" if gecko_hard else "✗"))

    # Пять заявленных библиотек: либо их нет в блоке вовсе (значит сборку не
    # тянут — это и есть «мягкие по построению»), либо они объявлены мягко.
    declared_keys = set()
    for line in lines:
        kind, key = classify(line)
        if key is not None:
            declared_keys.add(key)
    undeclared = [SOFT_LIBS[k] for k in SOFT_LIBS if k not in declared_keys]
    if undeclared:
        print("  · нет в build.gradle вовсе (сборку не тянут): %s"
              % ", ".join(undeclared))

    if hard:
        print()
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — %d жёстких зависимостей: сборка без них "
              "не пройдёт" % len(hard))
        return 2
    if not gecko_hard:
        print()
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — GeckoLib не жёсткий, геометрия не "
              "соберётся (R23 п.5)")
        return 2
    print()
    print("ИТОГ: СХОДИТСЯ — пять библиотек Директора сборку не тянут "
          "(в build.gradle их нет либо они мягкие)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
