#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приёмка пакета 3.8.1 — правила 3.8.0 + блоки, которые вводятся впервые.

Зачем обёртка, а не копия. Гейт 3.8.0 — это ~2000 строк, где **уже** есть всё
содержательное: манифест (внешний и внутренний), дельта к предыдущей версии,
версия в четырёх местах, R23 вместе с пунктом 8 «лицензии == канон», блок 16
(существа: цвета, размер маски == тело, свечение вне силуэта, UV кубов),
crest, банк == пакет, канон 144. Скопировать это в `accept_3.8.1.py` значило
бы получить **две копии**, которые через месяц разойдутся — ровно так уже
случилось с таблицей лицензий в трёх файлах.

Поэтому здесь: подмена версии, расширение списка ожидаемого роста и **два
новых нормативных блока** из промпта Архитектора (§4a, §4b). Остальное
исполняет `accept_3.8.0.py` как есть — одно место правки правил.

Что добавляется (промпт `integrator_prompt_381.md` §4):

    A. `creature_pack_audit.py --require-anims` — **нормативным** для 3.8.1.
       У каждого существа в реестре обязаны быть анимации. В 3.7.3 этот флаг
       НЕЛЬЗЯ включать: там у большинства мобов анимаций нет (долг, вписанный
       в 3.8.1), и флаг обрушил бы приёмку уже выпущенной версии. Проверка
       вводится вперёд, а не задним числом.

    B. `volume_semantics_audit.py` — **сторож половинчатой правки**:
       эффективная громкость, метка и цели по сэмплам согласованы, «в спеке
       одно, в sounds.json другое» не допускается. Для 3.8.1 — нормативно.

Использование:
    python3 tools/accept_3.8.1.py [путь_к_zip] [путь_к_манифесту]

Коды: 0 — ПРИНЯТО, 1 — ЕСТЬ РАСХОЖДЕНИЯ, 2 — ошибка запуска.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

VERSION = "3.8.1"

# ⛔ 3.8.1 обязана вырасти относительно 3.8.0: две вариации на каждое из
# четырёх core-существ (зомби/скелет/паук/крипер). Список намеренно **шире**,
# чем у 3.8.0, и только на добавление: изменение и удаление существующих
# файлов по-прежнему запрещено дельтой.
GROWN_381 = (
    "src/main/resources/assets/carnis/geo/entity/",
    "src/main/resources/assets/carnis/textures/entity/",
    "src/main/resources/assets/carnis/animations/",
    "src/main/resources/assets/carnis/sounds/",
    "src/main/resources/assets/carnis/sounds.json",
    "MANIFEST.txt",
    "README.md",
    "LICENSE",
)


def _python_with(mods):
    """Интерпретатор, в котором есть нужные библиотеки (для чекера картинок)."""
    for exe in (sys.executable, "python3"):
        try:
            r = subprocess.run([exe, "-c", "import " + ", ".join(mods)],
                               capture_output=True)
            if r.returncode == 0:
                return exe
        except OSError:
            continue
    return sys.executable


def check_require_anims(pkg_path):
    """§4b: у каждого существа обязаны быть анимации — нормативно для 3.8.1.

    Fail-closed по смыслу: если чекер не может быть запущен, это НЕ «пропуск»,
    а провал. Иначе проверка существует только на бумаге — ровно та дыра, из-за
    которой анимации 33 существ однажды проверили «по отчёту», а не по файлам.
    """
    print()
    print("A) Анимации у каждого существа (--require-anims, промпт §4b)")
    checker = os.path.join(REPO, "02-reviewer", "tools", "creature_pack_audit.py")
    if not os.path.isfile(checker):
        print("  ✗ честно: 02-reviewer/tools/creature_pack_audit.py не найден —")
        print("    проверить анимации нечем. Это провал, а не «пропуск».")
        return ["анимации: чекер отсутствует — проверка невозможна"]
    py = _python_with(["PIL", "numpy"])
    cmd = [py, checker, pkg_path, "--require-anims"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    tail = [l for l in out.split("\n") if l.strip()][-8:]
    for l in tail:
        print("  | " + l)
    if r.returncode != 0:
        print("  ✗ код %d — у части существ нет анимаций (или чекер упал)" % r.returncode)
        return ["анимации: --require-anims код %d" % r.returncode]
    print("  ✓ код 0 — анимации есть у всех существ реестра")
    return []


def check_volume_semantics(pkg_path):
    """§4a: сторож половинчатой правки — нормативно для 3.8.1.

    Половинчатая правка: в спеке объявлена цель, в `sounds.json` стоит другая
    громкость, в call-site третья. Слух получает не то, что записано в
    документах, и ни одна отдельная проверка этого не видит.
    """
    print()
    print("B) Семантика громкостей — сторож половинчатой правки (промпт §4a)")
    audit = os.path.join(REPO, "02-reviewer", "tools", "volume_semantics_audit.py")
    if not os.path.isfile(audit):
        print("  ✗ честно: volume_semantics_audit.py не найден — проверить нечем.")
        return ["громкости: сторож отсутствует — проверка невозможна"]
    r = subprocess.run([sys.executable, audit, "--pkg", pkg_path],
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    tail = [l for l in out.split("\n") if l.strip()][-6:]
    for l in tail:
        print("  | " + l)
    if r.returncode != 0:
        print("  ✗ код %d — семантика громкостей не сходится" % r.returncode)
        return ["громкости: volume_semantics_audit код %d" % r.returncode]
    print("  ✓ код 0 — цели по сэмплам выполнены, половинчатых правок нет")
    return []


def main():
    args = sys.argv[1:]
    pkg = args[0] if args else os.path.join(
        REPO, "01-coder", VERSION, "project-%s-clean.zip" % VERSION)
    if not os.path.exists(pkg):
        print("НЕТ ПАКЕТА: %s" % pkg)
        print("Код 2 — ошибка запуска, а не приговор пакету.")
        return 2

    print("=" * 78)
    print("Приёмка пакета %s — правила 3.8.0 + §4a/§4b промпта Архитектора" % VERSION)
    print("=" * 78)

    # 1. Базовый гейт 3.8.0 с подменённой версией и расширенным ростом.
    base = os.path.join(REPO, "tools", "accept_3.8.0.py")
    if not os.path.isfile(base):
        print("НЕТ ГЕЙТА 3.8.0: %s" % base)
        print("Код 2 — ошибка запуска.")
        return 2
    sys.path.insert(0, os.path.join(REPO, "tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("accept_380_for_381", base)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.VERSION = VERSION
    # Список ожидаемого роста — объединение: 3.8.0 обязан был вырасти, и 3.8.1
    # растёт дальше. Только добавление; изменение/удаление держит дельта.
    grown = tuple(dict.fromkeys(tuple(mod.GROWN_380) + GROWN_381))
    mod.GROWN_380 = grown
    print()
    print("Правила: гейт 3.8.0, версия подменена на %s, ожидаемый рост — %d путей"
          % (VERSION, len(grown)))
    print()
    base_rc = mod.main()
    print()
    print("=" * 78)
    print("Итог правил 3.8.0: код %d" % base_rc)

    # 2. Новые блоки 3.8.1 — нормативные.
    extra = []
    extra += check_require_anims(pkg)
    extra += check_volume_semantics(pkg)

    print()
    print("=" * 78)
    if base_rc == 0 and not extra:
        print("ИТОГ: ПРИНЯТО — правила 3.8.0 и оба новых блока 3.8.1 пройдены.")
        return 0
    if base_rc != 0 and extra:
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — правила 3.8.0 (код %d) и %d новых блока"
              % (base_rc, len(extra)))
        for e in extra:
            print("  · %s" % e)
        return 1
    if base_rc != 0:
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — правила 3.8.0 дали код %d" % base_rc)
        return 1
    print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — правила 3.8.0 пройдены, но новые блоки нет: %d"
          % len(extra))
    for e in extra:
        print("  · %s" % e)
    return 1


if __name__ == "__main__":
    sys.exit(main())
