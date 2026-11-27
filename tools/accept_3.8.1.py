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

    C. **Покрытие core9** (найдено 2026-11-27). Приёмка 3.8.0 вызывает чекер с
       `--only` по дельте реестра: 33 существа из 49. Ровно вне этой зоны
       оказались те девять, у кого EСТЬ код в игре, и у них же — все 9 коллизий
       имён анимаций. То есть приёмка проверяла то, чего в игре нет, и молчала
       о том, что в игре есть. Для 3.8.1 блок C обязателен: core9 проверяются
       явно и отдельно, даже если дельта их не включает.

Использование:
    python3 tools/accept_3.8.1.py [путь_к_zip] [путь_к_манифесту]

Коды: 0 — ПРИНЯТО, 1 — ЕСТЬ РАСХОЖДЕНИЯ, 2 — ошибка запуска.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

# Девять существ, у которых есть код в моде: ссылки на geo/entity/<name>.geo.json
# в java. Это ЕДИНСТВЕННЫЕ, кого игрок может увидеть; всё остальное в пакете
# лежит без кода. Приёмка 3.8.0 их не проверяет (они не в дельте реестра) —
# отсюда блок C. Список сверен с кодом прогоном, не по памяти.
CORE9 = ("infected_zombie", "infected_skeleton", "infected_spider",
         "infected_creeper", "flesh_amalgam", "hive_sentinel",
         "biomass_maggot", "cerebral_nexus", "parasitic_tendril")

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


def check_core9(pkg_path, extract_dir=None):
    """§4c: core9 проверяются отдельно и явно.

    Зачем. Приёмка 3.8.0 запускает `creature_pack_audit` с `--only` по дельте
    реестра (33 из 49 существ). Проверено на 3.8.0: все 9 коллизий имён
    анимаций — у существ ВНЕ этой зоны, и это ровно те девять, у кого есть код
    в игре (ссылки `geo/entity/<name>.geo.json` в java). Получалось, что
    приёмка строже всего там, где результат некому увидеть.

    Блок делает две вещи:
      1. гоняет чекер по core9 без `--only`, чтобы их изъяны были видны;
      2. сверяет список CORE9 с тем, что реально прописано в java — если
         Кодер добавил или убрал существо, список должен обновиться, иначе
         блок тихо проверяет не то.

    Fail-closed: не нашли java или чекер — провал, а не «пропуск».
    """
    import json as _json
    import re as _re
    import zipfile as _zip

    print()
    print("C) Покрытие core9 — существа, у которых есть код в игре (§4c)")
    problems = []

    # --- 1. Сверка списка с кодом -------------------------------------
    #
    # `_b` — ВАРИАНТ, а не существо. В 3.8.1 java ссылается и на
    # `geo/entity/infected_<mob>_b.geo.json`: четверо мобов получили вторую
    # боевую форму (`InfectedVariant` A/B), и `*GeoModel` переключает
    # модель/текстуру/анимации по `isVariantA()`. Если хвост `_b` не отбросить,
    # список «устаревает» на четырёх несуществующих существах, а чекер ниже
    # прогонялся бы по именам, которых нет в реестре. Варианты при этом не
    # теряются: они печатаются отдельной строкой, а сами `_b`-наборы
    # проверяются блоком E.
    java_refs = set()
    java_variant_refs = set()
    try:
        with _zip.ZipFile(pkg_path) as z:
            for n in z.namelist():
                if not n.endswith(".java"):
                    continue
                try:
                    src = z.read(n).decode("utf-8", "ignore")
                except Exception:
                    continue
                for m in _re.finditer(
                        r'"geo/entity/([a-z0-9_]+)\.geo\.json"', src):
                    raw = m.group(1)
                    if raw.endswith("_b"):
                        java_variant_refs.add(raw)
                        raw = raw[:-2]
                    java_refs.add(raw)
    except Exception as e:
        print("  x java в пакете не читается (%s) — сверка невозможна" % e)
        return ["core9: java не читается — проверка невозможна"]

    if not java_refs:
        print("  x в java нет ни одной ссылки geo/entity/*.geo.json")
        print("    либо код сменил схему путей, либо пакет собран без java.")
        print("    Молча пропустить нельзя: тогда core9 неопределим.")
        return ["core9: ссылок на geo/entity в java нет — core9 неопределим"]

    declared = set(CORE9)
    extra = sorted(java_refs - declared)
    missing = sorted(declared - java_refs)
    if java_variant_refs:
        print("  · варианты B — та же сущность, отдельный визуал: %s"
              % ", ".join(sorted(java_variant_refs)))
    if extra:
        print("  ✗ в java есть существа вне списка CORE9: %s" % ", ".join(extra))
        print("    список CORE9 в этом файле устарел — обновить перед приёмкой")
        problems.append("core9: в java есть %s — список устарел" % extra)
    if missing:
        print("  ✗ в java нет ссылки на: %s" % ", ".join(missing))
        print("    существо заявлено как «в игре», но кода у него нет")
        problems.append("core9: нет кода у %s" % missing)
    if not extra and not missing:
        print("  v список CORE9 сходится с java: %d существ" % len(declared))

    # --- 2. Прогон чекера по core9 ------------------------------------
    checker = os.path.join(REPO, "02-reviewer", "tools",
                           "creature_pack_audit.py")
    if not os.path.isfile(checker):
        print("  x чекера нет — изъяны core9 проверить нечем")
        return problems + ["core9: чекер отсутствует"]

    py = _python_with(["PIL", "numpy"])
    r = subprocess.run([py, checker, pkg_path,
                        "--only", ",".join(sorted(declared)),
                        "--require-anims"],
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    for line in out.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("\u2717") or "Существ:" in s or "ИТОГ" in s:
            print("  | " + s)
    # Счёт покрытия: чекер на пустом наборе печатает «Существ: 0» и «СХОДИТСЯ».
    m = _re.search(r"Существ:\s*(\d+)", out)
    covered = int(m.group(1)) if m else -1
    if covered != len(declared):
        print("  x проверено %d из %d — имена разошлись, аудит неполный"
              % (max(covered, 0), len(declared)))
        problems.append("core9: проверено %d из %d"
                        % (max(covered, 0), len(declared)))
        return problems
    if r.returncode != 0:
        print("  ✗ core9: код %d — у существ из игры есть изъяны" % r.returncode)
        problems.append("core9: чекер код %d" % r.returncode)
    else:
        print("  v core9: код 0 — у всех девяти изъянов нет")
    return problems


def check_java_refs(pkg_path):
    """§4d: код не ссылается на ресурсы, которых нет в пакете.

    Зачем. Проверено 2026-11-27 на пакете 3.8.1: гейт 3.8.0 разрешает любые
    изменения `src/main/java/` флагом `--allow` и НЕ СМОТРИТ внутрь. За сессию
    так прошли 2 изменённых файла (CarnisMod.java + новый
    CuriosSlotRegistration.java) без единой проверки содержимого — при том что
    в 3.8.1 должны появиться файлы 8 вариантов мобов.

    Это дыра именно того класса, что уже ловился в проекте: проверка есть, но
    смотрит не туда. Когда придёт код вариантов, он пройдёт так же молча, даже
    если сошлётся на несуществующую модель, анимацию или текстуру. GeckoLib в
    такой ситуации молча не рисует моб — ровно как было с `_glow.png` вместо
    `_glowmask.png`.

    Что проверяется: каждая литеральная ссылка вида
    `new ResourceLocation(..., "geo/entity/x.geo.json")` и подобные должна
    существовать в пакете как `src/main/resources/assets/carnis/<ссылка>`.

    Чего НЕ проверяется: смысл кода, его корректность, компиляция. Это не
    компилятор и не замена тестам — только «ссылка ведёт в существующий файл».

    Fail-closed: если в пакете нет ни одного .java — это провал, а не пропуск.
    Пустая проверка не имеет права выглядеть как успешная.
    """
    import re as _re
    import zipfile as _zip

    print()
    print("D) Код не ссылается на отсутствующие ресурсы (§4d)")

    PREFIX = "src/main/resources/assets/carnis/"
    # Литералы путей ресурсов внутри java. Только то, что реально кладут в
    # assets/carnis: geo, animations, textures, models, blockstates, sounds.
    PAT = _re.compile(
        r'"((?:geo|animations|textures|models|blockstates|sounds)/'
        r'[A-Za-z0-9_./-]+\.(?:json|png|ogg))"')

    try:
        z = _zip.ZipFile(pkg_path)
    except Exception as e:
        print("  x пакет не читается (%s) — проверка невозможна" % e)
        return ["java-ссылки: пакет не читается"]

    with z:
        names = set(z.namelist())
        java = [n for n in names if n.endswith(".java")]
        if not java:
            print("  x в пакете нет ни одного .java — проверять нечего,")
            print("    и это провал: пакет без кода не может быть 3.8.1.")
            return ["java-ссылки: в пакете нет .java"]

        refs = {}
        unreadable = []
        for n in java:
            try:
                src = z.read(n).decode("utf-8", "ignore")
            except Exception:
                unreadable.append(n)
                continue
            for m in PAT.finditer(src):
                refs.setdefault(m.group(1), []).append(n.split("/")[-1])

        if unreadable:
            print("  x не читается %d .java: %s"
                  % (len(unreadable), ", ".join(x.split("/")[-1]
                                                for x in unreadable[:3])))
            return ["java-ссылки: не читается %d файлов" % len(unreadable)]

        if not refs:
            print("  ? ни одной литеральной ссылки на ресурсы не найдено")
            print("    само по себе не провал: код может собирать пути")
            print("    динамически. Но и «чисто» это не делает.")
            return []

        missing = sorted(r for r in refs if (PREFIX + r) not in names)
        print("  .java файлов: %d | ссылок на ресурсы: %d | битых: %d"
              % (len(java), len(refs), len(missing)))
        if missing:
            for r in missing[:12]:
                print("    ✗ %-46s <- %s" % (r, refs[r][0]))
            if len(missing) > 12:
                print("    ... и ещё %d" % (len(missing) - 12))
            print("  ✗ код ссылается на ресурсы, которых нет в пакете")
            print("    в игре это молчаливый отказ: GeckoLib ничего не нарисует")
            return ["java-ссылки: %d битых ссылок" % len(missing)]

        print("  v все %d ссылок ведут в существующие файлы" % len(refs))
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


def check_variant_sets(pkg_path):
    """§4e (новый блок 3.8.1): визуальные наборы варианта B не «висят» зря.

    Зачем. Блок C теперь отбрасывает хвост `_b`, потому что это вариант, а не
    существо. Ослабить проверку и ничего не добавить взамен нельзя: тогда
    `_b`-модели могли бы лежать в пакете мёртвым грузом — ровно та дыра, из-за
    которой 3.8.1 уже проходила при старых `*GeoModel` (модели `_b` были, но
    код их не грузил).

    Что проверяется по КАЖДОМУ из четырёх мобов:
      1. код реально ссылается на `_b`-геометрию и `_b`-текстуру;
      2. файлы существуют;
      3. glowmask есть, ровно цвета (255,92,57), вне силуэта 0 px;
      4. аудитор по `_b`-набору проходит с `--require-anims` (UV, топ-доля,
         цвета, ключи idle/walk/attack/hurt/death).

    Fail-closed: нет набора или он не прошёл — провал, а не «пропуск».
    """
    import io as _io
    import json as _json
    import re as _re
    import zipfile as _zip

    print()
    print("E) Наборы варианта B (_b) — код грузит, ассеты полны (§4e)")
    problems = []
    MOBS = ("zombie", "skeleton", "spider", "creeper")
    PREFIX = "src/main/resources/assets/carnis/"
    GLOW = (255, 92, 57)

    try:
        z = _zip.ZipFile(pkg_path)
    except Exception as e:
        print("  x пакет не читается (%s)" % e)
        return ["варианты B: пакет не читается"]

    with z:
        names = set(z.namelist())
        srcs = {}
        for n in names:
            if n.endswith(".java"):
                try:
                    srcs[n.split("/")[-1]] = z.read(n).decode("utf-8", "ignore")
                except Exception:
                    pass
        blob = "\n".join(srcs.values())

        for mob in MOBS:
            geo = "geo/entity/infected_%s_b.geo.json" % mob
            tex = "textures/entity/infected_%s_b.png" % mob
            glow = "textures/entity/infected_%s_b_glowmask.png" % mob
            anim = "animations/entity/infected_%s_b.animation.json" % mob

            ref_geo = ('"%s"' % geo) in blob
            ref_tex = ('"%s"' % tex) in blob
            if not ref_geo or not ref_tex:
                print("  ✗ %s: код не ссылается на %s"
                      % (mob, "геометрию" if not ref_geo else "текстуру"))
                print("    модель _b лежит в пакете, но в игре не загрузится")
                problems.append("варианты B: %s не грузится кодом" % mob)
                continue

            absent = [p for p in (geo, tex, glow, anim) if PREFIX + p not in names]
            if absent:
                print("  ✗ %s: нет файлов %s" % (mob, ", ".join(absent)))
                problems.append("варианты B: у %s нет ассетов" % mob)
                continue

            # маска: размер, цвет, вне силуэта
            try:
                from PIL import Image
                import numpy as np
                ti = Image.open(_io.BytesIO(z.read(PREFIX + tex))).convert("RGBA")
                gi = Image.open(_io.BytesIO(z.read(PREFIX + glow))).convert("RGBA")
            except Exception as e:  # noqa: BLE001
                print("  x %s: png не читается (%s)" % (mob, e))
                problems.append("варианты B: %s png не читается" % mob)
                continue
            if gi.size != ti.size:
                print("  ✗ %s: маска %s != текстуры %s" % (mob, gi.size, ti.size))
                problems.append("варианты B: %s размер маски" % mob)
                continue
            ta, ga = np.array(ti), np.array(gi)
            mask = ga[:, :, 3] > 0
            cols = set(map(tuple, ga[mask][:, :3].tolist())) if mask.any() else set()
            if cols != {GLOW}:
                print("  ✗ %s: непрозрачные цвета маски %s, нужен только %s"
                      % (mob, sorted(cols)[:3], GLOW))
                problems.append("варианты B: %s цвет маски" % mob)
                continue
            outside = int(np.sum(mask & (ta[:, :, 3] == 0)))
            if outside:
                print("  ✗ %s: свечение вне силуэта %d px" % (mob, outside))
                problems.append("варианты B: %s glow вне силуэта" % mob)
                continue
            alphas = set(np.unique(ta[:, :, 3]).tolist())
            if not alphas <= {0, 255}:
                print("  ✗ %s: альфа текстуры не бинарная %s"
                      % (mob, sorted(alphas)[:4]))
                problems.append("варианты B: %s альфа" % mob)
                continue

            # имена анимаций: всё, что код может попросить у этого моба
            need = set(_re.findall(
                r'"animation\.infected_%s(?:_b)?\.([a-z_]+)"' % mob, blob))
            have = set()
            for suffix in ("", "_b"):
                p = PREFIX + "animations/entity/infected_%s%s.animation.json" % (
                    mob, suffix)
                if p in names:
                    try:
                        have |= set(_json.loads(z.read(p))["animations"])
                    except Exception:
                        pass
            have_short = {k.split(".")[-1] for k in have}
            miss = sorted(need - have_short)
            if miss:
                print("  ✗ %s: код просит анимации, которых нет: %s"
                      % (mob, ", ".join(miss)))
                print("    GeckoLib молча не проиграет их — поза замрёт")
                problems.append("варианты B: %s нет анимаций %s" % (mob, miss))
                continue
            print("  v %s_b: модель+текстура загружаются, маска %d px, "
                  "анимаций по коду %d/%d"
                  % (mob, int(mask.sum()), len(need), len(need)))

    if problems:
        return problems
    print("  ✓ все четыре набора варианта B полны и грузятся кодом")
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
    print("Приёмка пакета %s — правила 3.8.0 + §4a/§4b/§4c/§4d промпта Архитектора" % VERSION)
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
    # ⛔ Найдено 2026-11-27 прогоном на реальном пакете 3.8.1. `mod.main()`
    # читает путь из `sys.argv[1]`, а вызывающий скрипт запускался БЕЗ
    # аргументов — значит гейт проверял путь по умолчанию, то есть пакет
    # 3.8.0. Симптом: «✗ gradle.properties: 3.8.0», «✗ каталог пакета:
    # 3.8.0», «версия 3.8.1: 0 из 4» — то есть обёртка судила не тот файл.
    # Передаём путь явно, не полагаясь на argv.
    _argv_restore = list(sys.argv)
    sys.argv = [sys.argv[0], pkg]
    try:
        base_rc = mod.main()
    finally:
        sys.argv = _argv_restore
    print()
    print("=" * 78)
    print("Итог правил 3.8.0: код %d" % base_rc)

    # 2. Новые блоки 3.8.1 — нормативные.
    extra = []
    extra += check_require_anims(pkg)
    extra += check_volume_semantics(pkg)
    extra += check_core9(pkg)
    extra += check_java_refs(pkg)
    extra += check_variant_sets(pkg)

    print()
    print("=" * 78)
    if base_rc == 0 and not extra:
        print("ИТОГ: ПРИНЯТО — правила 3.8.0 и все новые блоки 3.8.1 пройдены.")
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
