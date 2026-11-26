#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приёмка пакета 3.7.3 (T-3178).

Блоки 1–8 переиспользованы из `tools/accept_3.7.0.py` **без изменения правил**
(манифест, JSON, версия, overlay, A4-p7, A3R1, K8-S, ambient). Добавлены:

    9.  тембр — `tools/timbre_check.py` (Ревизор, T-3106), нужен код 0;
        доля энергии < 80 Гц <= 25 %, спектральный центр >= 400 Гц.
    10. принятое не тронуто — 14 файлов 3.6.0-R побайтово (Д1–Д7 и др.).
    11. З-1 — доля самой частой непрозрачной краски `infected_creeper.png`
        <= 35 % (было 81,2 % в 3.7.0; ТЗ называет 84,2 %, см. отчёт).
    12. принятые слои побайтово: A4-p7-**R** (8 PNG) и A3R1 (4 PNG) — T-3119.
    11. существа — доля самой частой краски <= 35 % (`shade_density.py`);
    12. блоки — то же по текстурам блоков;
    13. банк — формат однороден (моно/44.1 кГц), клиппинга нет (ТЗ §9 3.7.2).

Нумерация взята из ТЗ 3.7.2 §9. Блоки «принятые слои» (12 в 3.7.1) и «тембр»
сохранены как есть — они наследие предыдущих версий, а не новые блоки 3.7.2.

Блоки 1–8 — наследие 3.7.1 без изменения правил (ТЗ 3.7.2 §9).

Использование:
    python3 tools/accept_3.7.1.py [путь_к_zip] [путь_к_манифесту]

Коды (гейт приёмки, см. tools/README.md): 0 — ПРИНЯТО,
1 — ЕСТЬ РАСХОЖДЕНИЯ, 2 — нет пакета / каталог вместо ZIP / битый архив /
ошибка запуска. Ни один неверный путь не даёт трейсбек.
"""
import importlib
import importlib.util
import json
import math  # noqa: F401  (используется в блоке 15)
import os
import re
import shutil
import subprocess
import sys
import struct
import tempfile
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# З-17: общий резолвер эталона (диск → git-объект).
sys.path.insert(0, os.path.join(REPO, "tools"))
import baseline  # noqa: E402
DEFAULT_ZIP = os.path.join(REPO, "01-coder", "3.8.0",
                           "project-3.8.0-clean.zip")
DEFAULT_MANIFEST = os.path.join(REPO, "01-coder", "3.8.0",
                                "project-3.8.0-clean.manifest.txt")
# З-17: эталон 3.6.0-R может отсутствовать в рабочем дереве (sparse-checkout
# у Ревизора) — тогда достаём из git-объекта. Блоки спрашивают REF_360_REAL,
# а не путь на диске: «нет файла» не должно превращаться в «не сходится».
REF_360 = os.path.join(REPO, "01-coder", "3.6.0-R",
                       "project-3.6.0-R-clean.zip")
REF_360_REAL, REF_STATUS, REF_SRC = None, baseline.UNAVAILABLE, "none"


def resolve_ref():
    """Разрешить эталон (диск → git). Возвращает путь или None."""
    try:
        path, status, src = baseline.resolve(REF_360)
    except Exception as exc:  # noqa: BLE001
        print("  ! baseline.resolve упал: %s" % exc)
        return None, baseline.UNAVAILABLE, "error"
    return path, status, src

VERSION = "3.8.0"

GLOW_CHECK = os.path.join(REPO, "tools", "glow_check.py")
ORPHANS = os.path.join(REPO, "tools", "sound_orphans.py")
TENDRIL = os.path.join(REPO, "tools", "tendril_flesh_match.py")
AMBIENT_GATE = os.path.join(REPO, "tools", "ambient_gate.py")
TIMBRE = os.path.join(REPO, "tools", "timbre_check.py")

CREEPER = "src/main/resources/assets/carnis/textures/entity/infected_creeper.png"
SHADE_MAX = 35.0

# З-16/З-18: нижний порог числа красок (норма ТЗ «>= 7 цветов»).
# Без него плоская текстура из 1-6 цветов проходила как «худший 12.5 %».
SHADE_MIN_COLORS = 7
BLOCK_DIR = "src/main/resources/assets/carnis/textures/block"

# Решение Архитектора T-3142 (вариант B, волна 38): три текстуры блока
# перекрашены по ТЗ 3.7.2 §4 и ИСКЛЮЧЕНЫ из KEEP_IDENTICAL (в 3.7.0/3.7.1 они
# остаются принятыми — там перекраски нет). Разрешение не «любая текстура»,
# а «ровно то, что сдал Художник»: каждый файл сверяется побайтово с архивом.
RECOLOR_ACCEPTED_372 = {
    "src/main/resources/assets/carnis/textures/block/spore_sprout.png":
        "Carnis_3.7.2_T3115_block_recolor.zip",
    "src/main/resources/assets/carnis/textures/block/neural_moss.png":
        "Carnis_3.7.2_T3115_block_recolor.zip",
    "src/main/resources/assets/carnis/textures/block/pustule_cluster.png":
        "Carnis_3.7.2_T3115_block_recolor.zip",
}
SOUND_SUBDIR = "src/main/resources/assets/carnis/sounds"
TIMBRE_FILES = 10          # 9 слоёв + стингер; пульсы вне приёмки тембра

# Д1–Д7 и принятое: НЕ должно измениться относительно 3.6.0-R.
KEEP_IDENTICAL = [
    "src/main/resources/assets/carnis/geo/entity/cerebral_nexus.geo.json",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_1.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_2.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_3.png",
    "src/main/resources/assets/carnis/textures/mob_effect/incubating.png",
    "src/main/resources/assets/carnis/textures/mob_effect/thermal_shock.png",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_0.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_1.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_2.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_3.json",
]

fail = []
# З-17: проверки, которые не удалось выполнить (эталон недоступен и т.п.).
# Это НЕ провал пакета, но и не «проверено» — выносится в итог отдельно.
skipped_checks = []
warn = []


# ---------------------------------------------------------------- 1. манифест
def check_manifest(extract_dir, manifest, src="near"):
    """Сверить пакет с манифестом.

    src="near" — манифест рядом с пакетом: доверяем, расхождение = fail.
    src="repo" — манифест из резервного пути репозитория, а пакет пришёл
    не из своего каталога. Тогда расхождение может значить «манифест в
    дереве от другой сборки», а не дефект пакета (З-18). Такое
    расхождение НЕ валит приёмку, но печатается явно.
    """
    trusted = src != "repo"
    if not manifest or not os.path.exists(manifest):
        # З-18: «манифеста нет» — это НЕ «не сошлось N строк».
        # Честно пишем, что проверка не выполнена, а не выносим приговор.
        print("  · манифест не найден ни рядом с пакетом, ни в репозитории —")
        print("    сверка sha256 не выполнена")
        skipped_checks.append("манифест: не найден — сверка sha256 не выполнена")
        return
    files = 0
    for line in open(manifest, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        files += 1
    # Путь к манифесту АБСОЛЮТНЫЙ: cwd=extract_dir, и относительный путь
    # из корня репозитория там не разрешается (проверка молча «не находила»
    # файл и выдавала расхождение на корректном пакете).
    manifest_abs = os.path.abspath(manifest)
    r = subprocess.run(["sha256sum", "-c", "--quiet", manifest_abs],
                       cwd=extract_dir, capture_output=True, text=True)
    bad = [l for l in (r.stdout + r.stderr).split("\n")
           if l.strip() and "OK" not in l]
    actual = sum(len(fs) for _, _, fs in os.walk(extract_dir))
    print("  %s манифест: строк %d, файлов в пакете %d"
          % ("✓" if not bad else "✗", files, actual))
    for l in bad[:5]:
        print("      %s" % l)
    if not trusted:
        if bad or files != actual:
            print("  ! З-18: манифест взят из репозитория, а пакет — не из своего")
            print("    каталога: расхождение (%d строк) считаем возможной другой" % len(bad))
            print("    сборкой, а не приговором. Для строгой сверки положите")
            print("    манифест рядом с ZIP или укажите его вторым аргументом.")
            skipped_checks.append("манифест: сверено по резервному файлу репозитория")
        return
    if bad:
        fail.append("манифест: не сошлось %d строк" % len(bad))
    if files != actual:
        fail.append("манифест: строк %d, файлов %d" % (files, actual))


# --------------------------------------------------------------------- 2. JSON
EXPECTED_CHANGED_PNG = (
    "src/main/resources/assets/carnis/textures/entity/flesh_amalgam_glowmask.png",
)


def check_delta_372(zip_path):
    """Дельта к принятому 3.7.2: любое неожиданное изменение — fail.

    Гейт проверял пакет «как есть» и не сверял его с эталоном, поэтому
    внесение произвольного кода (например вызовов под T-3184) прошло бы
    молча — именно так раньше просмотрели регресс З-16. Ожидаемое в 3.7.3:
    15 .ogg звука (З-21), 2 новые glowmask и 2 метаданных; всё остальное
    обязано совпасть побайтово. Код под T-3184 объявляется явно префиксом
    src/main/java/ — без флага он валит гейт.
    """
    prev = os.path.join(REPO, "01-coder", "3.7.3", "project-3.7.3-clean.zip")
    checker = os.path.join(REPO, "02-reviewer", "tools", "verify_373_delta.py")
    archive = os.path.join(REPO, "03-sound", "archive_zapas_2026-11-26")
    if not os.path.isfile(prev):
        print("  x дельта: нет эталона 01-coder/3.7.2/project-3.7.2-clean.zip")
        fail.append("дельта: эталона 3.7.2 нет — сверять не с чем")
        return
    if not os.path.isfile(checker):
        print("  x дельта: нет чекера 02-reviewer/tools/verify_373_delta.py")
        fail.append("дельта: чекер отсутствует — изменения не проверены")
        return
    py = _python_with("av") or sys.executable
    cmd = [py, checker, zip_path, "--prev", prev,
           "--originals", archive + os.sep, "--allow", "src/main/java/"]
    # Точечно, не префиксом: маска flesh_amalgam переделана под З-22 и обязана
    # отличаться от 3.7.2. Её цвет проверяет блок 14 по правилу Р-3, поэтому
    # разрешение не ослабляет проверку: не тот цвет — упадёт блок 14.
    for png in EXPECTED_CHANGED_PNG:
        cmd += ["--allow", png]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout
    for ln in out.splitlines():
        if "добавлено " in ln and "изменено" in ln:
            print("  · " + ln.strip())
    for ln in out.splitlines():
        s = ln.strip()
        if s.startswith("\u2717") or s.startswith("x ") or "не разрешено" in s \
                or "неожиданные изменения" in s or "пропали файлы" in s:
            print("      " + s)
    if r.returncode == 0:
        print("  v дельта: только ожидаемые изменения против 3.7.2")
    else:
        print("  x дельта: есть неожиданные изменения против 3.7.2")
        fail.append("дельта: неожиданные изменения против 3.7.2")


def check_volume_double(zip_path):
    """R24 §4: громкость задаётся в ОДНОМ месте — здесь это НОРМА, не отчёт.

    В гейте 3.7.3 та же проверка печатается отчётом: Ревизор в вердикте
    (`reviewer_373_verdict.md` §4-5) отнёс замечание к 3.7.4 и принял пакет.
    В 3.8.0 дефект переезжать не должен — поэтому здесь провал.
    """
    checker = os.path.join(REPO, "tools", "volume_double_check.py")
    if not os.path.isfile(checker):
        print("  x громкость: нет чекера tools/volume_double_check.py")
        fail.append("громкость: чекер отсутствует — двойное применение "
                    "не проверено")
        return
    r = subprocess.run([sys.executable, checker, zip_path],
                       capture_output=True, text=True)
    for ln in (r.stdout or "").splitlines():
        s = ln.strip()
        if s.startswith("↯") or s.startswith("=") or "код:" in s \
                or "итог:" in s or "ИТОГ" in s or "передаёт" in s:
            print("      " + s)
    if r.returncode == 0:
        print("  v громкость: одно место на событие (R24 §4)")
    elif r.returncode == 2:
        fail.append("громкость: двойное применение — событие задаёт громкость "
                    "и в коде, и в sounds.json (R24 §4)")
    else:
        fail.append("громкость: проверка не выполнена (код %d)" % r.returncode)


def check_deps_soft(zip_path):
    """I102/R102: пять библиотек Директора — мягкие, сборка без них идёт.

    Заявлены Curios, Patchouli, SmartBrainLib, Lodestone, Sound Physics. Если
    любая станет жёсткой (`modImplementation`/`implementation`), проект без неё
    не соберётся — а игрок получит краш вместо «работает без необязательного».
    GeckoLib, наоборот, обязан остаться жёстким (R23 п.5).
    """
    checker = os.path.join(REPO, "tools", "deps_soft_check.py")
    if not os.path.isfile(checker):
        print("  x зависимости: нет чекера tools/deps_soft_check.py")
        fail.append("зависимости: чекер отсутствует — мягкость не проверена")
        return
    r = subprocess.run([sys.executable, checker, zip_path],
                       capture_output=True, text=True)
    for ln in (r.stdout or "").splitlines():
        if ln.strip():
            print("      " + ln.rstrip())
    if r.returncode == 0:
        print("  v зависимости: пять библиотек мягкие, GeckoLib жёсткий (I102)")
    elif r.returncode == 2:
        fail.append("зависимости: есть жёсткая зависимость — сборка без неё "
                    "не пройдёт (I102)")
    else:
        fail.append("зависимости: проверка не выполнена (код %d)" % r.returncode)


def check_readme_license(zip_path):
    """R23 пп.1-6 + «GPL не попал»: README, лицензии, зависимости.

    Ревизор (R23 s2) проверил: в этом гейте не было НИ ОДНОЙ из шести
    проверок — 1618 строк без единого упоминания. Значит требования приёмки
    существовали только на бумаге. Его чекер лежит в 02-reviewer/tools/ и
    покрывает всё, включая ловушку п.5 (mandatory=true у forge/minecraft —
    законная платформенная зависимость, буквальное правило завалило бы любой
    корректный мод).
    """
    checker = os.path.join(REPO, "02-reviewer", "tools",
                           "readme_license_check.py")
    if not os.path.isfile(checker):
        print("  x README/LICENSE: нет чекера 02-reviewer/tools/"
              "readme_license_check.py")
        fail.append("README/LICENSE: чекер отсутствует — R23 не проверен")
        return
    r = subprocess.run([sys.executable, checker, zip_path],
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    for line in out.splitlines():
        if line.strip():
            print("      " + line)
    # Коды чекера: 0 — все шесть пунктов, 2 — провалы, 1 — ошибка входа.
    if r.returncode == 0:
        print("  v README/LICENSE: README, MIT, CC-BY-NC-SA (лор/арт), "
              "зависимости, mandatory — все шесть пунктов R23")
    elif r.returncode == 2:
        fail.append("README/LICENSE: R23 — есть провалы (чекер код 2)")
    else:
        fail.append("README/LICENSE: чекер не смог проверить (код %d)"
                    % r.returncode)


def check_json(extract_dir):
    n = bad = 0
    for dp, _, fs in os.walk(extract_dir):
        for f in fs:
            if not f.endswith((".json", ".mcmeta")):
                continue
            n += 1
            p = os.path.join(dp, f)
            try:
                json.load(open(p, encoding="utf-8"))
            except Exception as e:
                bad += 1
                print("  ✗ %s: %s" % (os.path.relpath(p, extract_dir), e))
    print("  %s JSON: %d файлов, битых %d" % ("✓" if bad == 0 else "✗", n, bad))
    if bad:
        fail.append("JSON: битых %d" % bad)


# ------------------------------------------------------------------ 3. Версия
def check_version(extract_dir, zip_path):
    """3.7.1 в четырёх местах (Forge): gradle.properties mod_version,
    mods.toml version, mods.toml displayVersion, имя каталога пакета."""
    gp = os.path.join(extract_dir, "gradle.properties")
    mt = os.path.join(extract_dir, "src", "main", "resources", "META-INF",
                      "mods.toml")
    seen = {}
    if os.path.exists(gp):
        for line in open(gp, encoding="utf-8"):
            if line.startswith("mod_version="):
                seen["gradle.properties"] = line.split("=", 1)[1].strip()
                break
    if os.path.exists(mt):
        for line in open(mt, encoding="utf-8"):
            s = line.strip()
            if s.startswith("version=") and "mods.toml version" not in seen:
                seen["mods.toml version"] = s.split("=", 1)[1].strip().strip('"')
            if s.startswith("displayVersion="):
                seen["displayVersion"] = s.split("=", 1)[1].strip().strip('"')
    folder = os.path.basename(os.path.dirname(os.path.abspath(zip_path)))
    base = folder.split("-R")[0]
    ok_n = 0
    for where, val in seen.items():
        ok = val == VERSION
        ok_n += ok
        print("  %s %s: %s" % ("✓" if ok else "✗", where, val))
        if not ok:
            fail.append("версия %s: %s = %s" % (VERSION, where, val))
    ok = base == VERSION
    ok_n += ok
    print("  %s каталог пакета: %s" % ("✓" if ok else "✗", folder))
    if not ok:
        fail.append("каталог пакета %s, ожидался %s" % (folder, VERSION))
    print("  %s версия %s: %d из 4" % ("✓" if ok_n == 4 else "✗", VERSION, ok_n))
    if len(seen) < 3:
        fail.append("версия: найдено только %d из 3 мест в файлах" % len(seen))


# ----------------------------------------------------------------- 4. Overlay
def check_overlay(extract_dir):
    ov = os.path.join(REPO, "06-build", "overlay.txt")
    if not os.path.exists(ov):
        warn.append("overlay.txt нет — пропущено")
        print("  ! overlay.txt нет")
        return
    import hashlib
    n = ok = 0
    for line in open(ov, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "->" not in line:
            continue
        left, _, right = line.partition("->")
        src = left.strip()
        dst, _, claim = right.partition("|")
        dst, claim = dst.strip(), claim.strip()
        n += 1
        a = os.path.join(REPO, src)
        b = os.path.join(extract_dir, dst)
        if not os.path.exists(a):
            print("  ✗ overlay: нет источника %s" % src)
        elif not os.path.exists(b):
            print("  ✗ overlay: в пакете нет %s" % dst)
        else:
            data = open(b, "rb").read()
            same = open(a, "rb").read() == data
            if same and claim:
                same = hashlib.sha256(data).hexdigest() == claim
            if same:
                ok += 1
            else:
                print("  ✗ overlay расхождение: %s" % dst)
    print("  %s overlay: совпало %d из %d" % ("✓" if ok == n else "✗", ok, n))
    if ok != n:
        fail.append("overlay: %d из %d" % (ok, n))


# ----------------------------------------------------------- помощники запуска
def _python_with(pkg, extra=()):
    """Интерпретатор, у которого есть пакет (PIL / numpy+scipy+av)."""
    cands = [sys.executable, "/tmp/vv3/bin/python", "/tmp/vv/bin/python",
             "python3"]
    for c in cands:
        if not c:
            continue
        if c != "python3" and not os.path.exists(c):
            continue
        try:
            r = subprocess.run([c, "-c", "import %s" % pkg],
                               capture_output=True, timeout=60)
        except Exception:
            continue
        if r.returncode == 0:
            return c
    return None


def run_tool(name, script, *args, **kw):
    # report=True — проверка, чей критерий не является нормой (например спека
    # роли: S84 Звука показал, что «пакет против моей спеки» — замкнутый круг,
    # такая проверка не может подтвердить саму спеку). Провал ПЕЧАТАЕТСЯ, но
    # не валит приёмку. Требовать её ради того, чтобы видеть — да; выдавать её
    # за независимый вердикт — нет.
    report_only = bool(kw.get("report", False))
    pkg = kw.get("need", None)
    py = _python_with(pkg) if pkg else sys.executable
    if py is None:
        print("  ✗ %s: нет интерпретатора с %s" % (name, pkg))
        fail.append("%s: нет окружения (%s)" % (name, pkg))
        return
    r = subprocess.run([py, script] + list(args), capture_output=True,
                       text=True)
    tail = [l for l in r.stdout.strip().split("\n") if l.startswith("ИТОГ")]
    # З-17: код 2 у чекеров — «ЗАМЕЧАНИЯ/пропуск», а не «расхождение».
    # Пропуск (эталон недоступен) нельзя валить в fail: иначе пакет получает
    # отказ за то, что у проверяющего устроено рабочее дерево, а не за дефект.
    # З-24: код 2 у чекера НЕЛЬЗЯ глушить целиком. Раньше он означал
    # «пропущено», и любой инструмент, вернувший 2 как «есть находки»,
    # проходил незамеченным — так 11 недостижимых звуковых событий едва не
    # уехали в релиз. Различаем по строке ИТОГ самого чекера:
    #   «ПРОПУЩЕНО»  -> действительно не выполнено (fail-closed, З-20);
    #   всё остальное -> ЗАМЕЧАНИЯ, то есть находки -> ✗ и в fail.
    verdict = tail[0] if tail else ""
    if r.returncode == 2 and "ПРОПУЩ" in verdict.upper():
        print("  … %s → код 2 «пропущено» | %s" % (name, verdict))
        skipped_checks.append("%s: код 2 «пропущено»" % name)
        return
    if r.returncode == 2:
        if report_only:
            print("  ~ %s → код 2 «ЗАМЕЧАНИЯ», отчёт (критерий — спека роли, "
                  "не норма) | %s" % (name, verdict or "(нет строки ИТОГ)"))
            warn.append("%s: замечания по спеке (отчёт)" % name)
            return
        print("  ✗ %s → код 2 «ЗАМЕЧАНИЯ» (не пропуск!) | %s"
              % (name, verdict or "(нет строки ИТОГ)"))
        for line in r.stdout.split("\n"):
            if "недостижим" in line or "[!]" in line:
                print("      " + line.strip()[:110])
                break
        fail.append("%s: замечания (код 2, не пропуск)" % name)
        return
    print("  %s %s → код %d | %s"
          % ("✓" if r.returncode == 0 else "✗", name, r.returncode,
             tail[0] if tail else "(нет строки ИТОГ)"))
    if r.returncode != 0:
        for line in r.stdout.split("\n"):
            if "[!]" in line or "  - " in line or "СИРОТЫ" in line:
                print("      " + line.strip())
        fail.append("%s: код %d" % (name, r.returncode))


# ------------------------------------------------------------------ 8. Ambient
def check_ambient(extract_dir):
    h = None
    for dp, _, fs in os.walk(extract_dir):
        if "HiveAmbientSoundHandler.java" in fs:
            h = os.path.join(dp, "HiveAmbientSoundHandler.java")
            break
    if h is None:
        print("  ! HiveAmbientSoundHandler.java нет — ambient не проверен")
        warn.append("ambient: файл хендлера не найден")
        return
    txt = open(h, encoding="utf-8").read()
    m = re.search(r"PULSE_INTERVAL_TICKS\s*=\s*(\d+)", txt)
    val = int(m.group(1)) if m else -1
    good = 420 <= val <= 480
    print("  %s PULSE_INTERVAL_TICKS = %d (нужно 420–480)"
          % ("✓" if good else "✗", val))
    if not good:
        fail.append("ambient: PULSE_INTERVAL_TICKS = %d, нужно 420–480" % val)
    has085 = "0.85F" in txt
    print("  %s громкость кровати: %s (нужно 0.45F)"
          % ("✗" if has085 else "✓",
             "0.85F — не исправлено" if has085 else "не 0.85F"))
    if has085:
        fail.append("ambient: громкость кровати всё ещё 0.85F, нужно 0.45F")
    if "0.45F" not in txt:
        fail.append("ambient: 0.45F не найдено — громкость кровати не задана")
    sj = None
    for dp, _, fs in os.walk(extract_dir):
        if "sounds.json" in fs:
            sj = os.path.join(dp, "sounds.json")
            break
    if sj:
        data = json.load(open(sj, encoding="utf-8"))
        bad = []
        for ev in ("hive.ambient", "hive.ambient_close", "hive.ambient_surface",
                   "hive.ambient_deep", "hive.ambient_core",
                   "hive.ambient_threshold"):
            for s in data.get(ev, {}).get("sounds", []):
                if isinstance(s, dict) and s.get("pitch") not in (None, 1.0):
                    bad.append("%s: pitch %s" % (ev, s["pitch"]))
        print("  %s pitch ambient-слоёв: %s"
              % ("✗" if bad else "✓",
                 "; ".join(bad) if bad else "все 1.0 или не заданы"))
        if bad:
            fail.append("ambient: pitch не 1.0 — %s" % "; ".join(bad[:3]))


# ------------------------------------------------- 14. Свечение 9 мобов (Р-3)
# Правило Р-3 Ревизора: у каждого из 9 мобов есть glowmask, и в нём РОВНО два
# цвета — прозрачный (0,0,0,0) и (255,92,57,255). Ни одного цвета вне палитры.
GLOW_EXPECT = {(0, 0, 0, 0), (255, 92, 57, 255)}
MOBS9 = ["infected_creeper", "infected_skeleton", "infected_spider",
         "infected_zombie", "cerebral_nexus", "flesh_amalgam",
         "hive_sentinel", "biomass_maggot", "parasitic_tendril"]


def check_glow9(extract_dir):
    from PIL import Image
    base = os.path.join(extract_dir, "src", "main", "resources", "assets",
                        "carnis", "textures", "entity")
    missing, extra, ok = [], [], 0
    for mob in MOBS9:
        path = os.path.join(base, mob + "_glowmask.png")
        if not os.path.exists(path):
            missing.append(mob)
            print("  ✗ %-20s glowmask НЕТ" % mob)
            continue
        im = Image.open(path).convert("RGBA")
        cols = {c for _, c in im.getcolors(1 << 20)}
        bad = cols - GLOW_EXPECT
        if bad:
            extra.append((mob, sorted(bad)))
            print("  ✗ %-20s цветов %d, вне палитры: %s"
                  % (mob, len(cols), sorted(bad)[:3]))
        else:
            # З-Г7 (тот же класс, что «14 дублей»): строка утверждала
            # «цветов 2», не проверяя, что их ровно 2. Маска из ОДНОГО
            # цвета (только прозрачный) проходила как «в норме», хотя
            # свечения в ней нет вовсе.
            if len(cols) != len(GLOW_EXPECT):
                print("  ✗ %-20s цветов %d, а Р-3 требует ровно %d "
                      "(прозрачный + 255,92,57)"
                      % (mob, len(cols), len(GLOW_EXPECT)))
                extra.append((mob, "цветов %d" % len(cols)))
                continue
            ok += 1
            print("  ✓ %-20s цветов %d (прозрачный + 255,92,57)"
                  % (mob, len(cols)))
    print("  свечение: мобов %d, в норме %d, без glowmask %d, вне палитры %d"
          % (len(MOBS9), ok, len(missing), len(extra)))
    if missing:
        fail.append("свечение Р-3: нет glowmask у %s" % ", ".join(missing))
    for mob, bad in extra:
        fail.append("свечение Р-3: %s — цвета вне палитры %s" % (mob, bad))


# ------------------------------------- 16. Новые существа 3.8.0 (волна 52, I11)
# Число берётся из реестра Художника, а не из текста доски: доска говорила
# «17 новых существ», Ревизор пересчитал по факту и нашёл 33 (99 файлов).
# Доверять заявленному числу здесь нельзя — гейт перечисляет состав по
# реестру и требует, чтобы каждое существо было в пакете целиком.
REG_NEW_CREATURES = re.compile(r"^\|\s*`?(infected_[a-z_]+)`?\s*\|", re.M)


def new_creature_names(extract_dir):
    """Имена новых существ 3.8.0 — из реестра Художника, раздел 3.8.0."""
    if not os.path.isfile(REGISTRY):
        return None
    txt = open(REGISTRY, encoding="utf-8").read()
    # раздел 3.8.0 заканчивается следующим заголовком «## »
    m = re.search(r"^##\s*5\..*?$", txt, re.M)
    if not m:
        return None
    tail = txt[m.end():]
    nxt = re.search(r"^##\s", tail, re.M)
    if nxt:
        tail = tail[:nxt.start()]
    names = sorted(set(REG_NEW_CREATURES.findall(tail)))
    return names


def _px(im):
    """Плоский список пикселей RGBA — для сверки маски с телом по координатам."""
    w, h = im.size
    data = list(im.getdata())
    for y in range(h):
        for x in range(w):
            yield x, y, data[y * w + x]


def check_new_creatures(extract_dir):
    """Каждое новое существо 3.8.0: geo валиден, текстура цела, glowmask Р-3.

    Проверяется то, что можно проверить по байтам, без доверия отчёту
    Художника: геометрия разбирается как JSON и её texture_width/height
    сверяются с реальным размером PNG — если художник нарисовал текстуру
    64x64, а в geo объявил 128x128, UV уедут и моб станет разноцветной
    кашей. Это ровно тот класс ошибки, который глазами не видно.
    """
    from PIL import Image
    names = new_creature_names(extract_dir)
    if names is None:
        print("  ! реестр 04-artist/creature_registry.md без раздела 3.8.0")
        warn.append("новые существа: в реестре нет раздела 3.8.0")
        return
    if not names:
        print("  ✗ новых существ в реестре 3.8.0 нет — проверять нечего")
        fail.append("новые существа: реестр 3.8.0 пуст")
        return
    base = os.path.join(extract_dir, "src", "main", "resources", "assets",
                        "carnis")
    geo_dir = os.path.join(base, "geo")
    tex_dir = os.path.join(base, "textures", "entity")
    ok = 0
    for name in names:
        geo = None
        for cand in (os.path.join(geo_dir, name + ".geo.json"),
                     os.path.join(geo_dir, "entity", name + ".geo.json")):
            if os.path.exists(cand):
                geo = cand
                break
        tex = os.path.join(tex_dir, name + ".png")
        mask = os.path.join(tex_dir, name + "_glowmask.png")
        absent = []
        for label, path_ in (("geo", geo), ("текстура", tex),
                             ("glowmask", mask)):
            if path_ is None or not os.path.exists(path_):
                absent.append(label)
        if absent:
            print("  ✗ %-22s нет: %s" % (name, ", ".join(absent)))
            fail.append("новые существа: %s — нет %s" % (name, ", ".join(absent)))
            continue
        try:
            doc = json.load(open(geo, encoding="utf-8"))
            geom = doc.get("minecraft:geometry") or []
            if not geom:
                raise ValueError("нет minecraft:geometry")
            desc = geom[0].get("description", {})
            tw, th = desc.get("texture_width"), desc.get("texture_height")
            bones = geom[0].get("bones") or []
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            print("  ✗ %-22s geo не разобран: %s" % (name, exc))
            fail.append("новые существа: %s — geo не разобран (%s)" % (name, exc))
            continue
        if not bones:
            print("  ✗ %-22s geo без костей" % name)
            fail.append("новые существа: %s — geo без костей" % name)
            continue
        im = Image.open(tex).convert("RGBA")
        iw, ih = im.size
        if tw is None or th is None:
            print("  ✗ %-22s geo без texture_width/height" % name)
            fail.append("новые существа: %s — geo без texture_width/height" % name)
            continue
        if (int(tw), int(th)) != (iw, ih):
            print("  ✗ %-22s geo объявляет %sx%s, текстура %dx%d"
                  % (name, tw, th, iw, ih))
            fail.append("новые существа: %s — размер текстуры в geo (%sx%s) "
                        "не совпал с PNG (%dx%d)" % (name, tw, th, iw, ih))
            continue
        # З-Г5(A): цвет текстуры считается по НЕПРОЗРАЧНЫМ пикселям. Наивный
        # подсчёт по RGBA-кортежам давал 11 «цветов» там, где их 3: под
        # alpha=0 художник может насорить произвольным RGB, и плоская
        # текстура проходила норму «>= 7 цветов».
        body = im.convert("RGBA")
        ncol = len({px[:3] for px in body.getdata() if px[3] > 0})
        # З-Г5(B): маска обязана быть того же размера, что тело. Маска 8x8 при
        # теле 64x64 — «свечение где-то в углу», а палитра у неё правильная.
        mim = Image.open(mask).convert("RGBA")
        if mim.size != body.size:
            print("  ✗ %-22s glowmask %dx%d, тело %dx%d"
                  % (name, mim.size[0], mim.size[1], body.size[0], body.size[1]))
            fail.append("новые существа: %s — размер glowmask не совпал с телом" % name)
            continue
        cols = {c for _, c in mim.getcolors(1 << 20)}
        bad = cols - GLOW_EXPECT
        if bad:
            print("  ✗ %-22s glowmask вне палитры: %s" % (name, sorted(bad)[:3]))
            fail.append("новые существа: %s — glowmask вне палитры Р-3" % name)
            continue
        # З-Г5(C): свечение на прозрачных пикселях тела = светящийся воздух.
        outside = 0
        for (_mx, _my, mp), (_bx, _by, bp) in zip(_px(mim), _px(body)):
            if mp[3] > 0 and bp[3] == 0:
                outside += 1
        if outside:
            print("  ✗ %-22s свечение вне силуэта: %d px" % (name, outside))
            fail.append("новые существа: %s — свечение вне силуэта (%d px)"
                        % (name, outside))
            continue
        if ncol < SHADE_MIN_COLORS:
            print("  ✗ %-22s текстура из %d цветов (норма ≥ %d)"
                  % (name, ncol, SHADE_MIN_COLORS))
            fail.append("новые существа: %s — текстура из %d цветов, норма ≥ %d"
                        % (name, ncol, SHADE_MIN_COLORS))
            continue
        ok += 1
        print("  ✓ %-22s geo %s костей, текстура %dx%d/%d цв., glowmask Р-3"
              % (name, len(bones), iw, ih, ncol))
    print("  новые существа: в реестре %d, полный комплект %d, с изъянами %d"
          % (len(names), ok, len(names) - ok))
    check_creature_pack(extract_dir, names)


# Порог костей: в 3.8.0 действует решение З-25 — базовая геометрия допустима,
# детализация (>= 12 костей) уходит в 3.8.1. Держу это константой, чтобы
# смена версии была одной строкой, а не переписыванием блока.
MIN_BONES = 1


def check_creature_pack(extract_dir, names):
    """Глубокий аудит существ чекером Ревизора (З-Г5, четыре дыры блока 16).

    Мой блок 16 проверял палитру, размер PNG против geo и наличие файлов, но
    пропускал четыре вещи, которые Ревизор собрал руками и прогнал:
      A) цвета считались по RGBA-кортежам — под alpha=0 можно «насорить» RGB
         и текстура из 3 непрозрачных цветов выглядела как 11-цветная;
      B) размер glowmask не сверялся с текстурой (маска 8x8 при теле 64x64);
      C) свечение вне силуэта тела не считалось;
      D) UV внутри кубов не проверялись вовсе — только объявленный размер.
    Ни одна из четырёх не видна глазами, и все четыре проходили как «✓».
    Вместо дублирования логики вызываю creature_pack_audit.py Ревизора:
    он проверяет всё перечисленное и вдобавок анимации.
    """
    checker = os.path.join(REPO, "02-reviewer", "tools", "creature_pack_audit.py")
    if not os.path.isfile(checker):
        print("  x пак существ: нет чекера 02-reviewer/tools/creature_pack_audit.py")
        fail.append("пак существ: чекер отсутствует — глубокий аудит не выполнен")
        return
    py = _python_with("PIL") or sys.executable
    r = subprocess.run([py, checker, extract_dir,
                        "--min-bones", str(MIN_BONES),
                        "--only", ",".join(names)],
                       capture_output=True, text=True)
    lines = [ln.rstrip() for ln in r.stdout.splitlines()]
    for ln in lines:
        s = ln.strip()
        if s.startswith("\u2717") or s.startswith("x ") or "изъян" in s.lower() \
                or "ИТОГ" in s:
            print("      " + s)
    # Fail-closed по счёту: чекер на пустом наборе печатает «Существ: 0»
    # и «ИТОГ: СХОДИТСЯ» с кодом 0. Пустая проверка не имеет права выглядеть
    # как успешная — иначе достаточно разойтись именам, и гейт промолчит.
    m = re.search(r"Существ:\s*(\d+)", r.stdout)
    covered = int(m.group(1)) if m else -1
    if covered < len(names):
        print("  x пак существ: проверено %d из %d — имена разошлись, "
              "аудит неполный" % (max(covered, 0), len(names)))
        fail.append("пак существ: проверено %d из %d комплектов"
                    % (max(covered, 0), len(names)))
        return
    if r.returncode == 0:
        print("  v пак существ: geo/UV/A3R1/Р-3/анимации — чисто, %d существ (З-Г5)"
              % covered)
    elif r.returncode == 2:
        print("  x пак существ: есть изъяны сверх блока 16 (З-Г5)")
        fail.append("пак существ: изъяны по глубокому аудиту (З-Г5)")
    else:
        print("  x пак существ: чекер не смог отработать (код %d)" % r.returncode)
        fail.append("пак существ: чекер упал (код %d)" % r.returncode)


# --------------------------------------------- 15. Реестр существ (16 комплектов)
REGISTRY = os.path.join(REPO, "04-artist", "creature_registry.md")
# geo-блоки и предметы: glowmask не требуется
GEO7 = ["bio_purifier", "hive_eye", "nerve_pillar", "neuro_armor",
        "pneumatic_inoculator", "pulsing_heart", "pustule_cluster"]


def check_registry(extract_dir):
    """Сверить комплекты в пакете с реестром Художника.

    Реестр — источник истины о том, ЧТО должно быть. Если реестр недоступен,
    это пропуск, а не приговор (тот же принцип, что З-17); но по З-20 пропуск
    валит приёмку как «не проверено».
    """
    if not os.path.exists(REGISTRY):
        print("  · реестр существ недоступен — сверка пропущена")
        skipped_checks.append("реестр: 04-artist/creature_registry.md не найден")
        return
    root = os.path.join(extract_dir, "src", "main", "resources", "assets", "carnis")
    txt = os.path.join(root, "textures")
    geo = os.path.join(root, "geo")

    def have(folder, stem):
        """Есть ли ТЕКСТУРА `<stem>.png`.

        Именно точное имя, а не startswith: иначе `pulsing_heart_glowmask.png`
        засчитывался бы как текстура `pulsing_heart`, и потеря самой текстуры
        проходила бы незамеченной (проверено негативом).
        """
        if not os.path.isdir(folder):
            return False
        return (stem + ".png") in os.listdir(folder)

    def geo_have(stem):
        # geo разложены по подкаталогам: geo/entity, geo/block, geo/item
        for sub in ("entity", "block", "item", ""):
            d = os.path.join(geo, sub) if sub else geo
            if not os.path.isdir(d):
                continue
            names = os.listdir(d)
            if (stem + ".geo.json") in names or (stem + ".json") in names:
                return True
        return False

    ok = bad = 0
    print("  · мобы (текстура обязательна):")
    for mob in MOBS9:
        if have(os.path.join(txt, "entity"), mob):
            ok += 1
            print("     ✓ %s" % mob)
        else:
            bad += 1
            print("     ✗ %s — текстуры нет в пакете" % mob)
            fail.append("реестр: у %s нет текстуры" % mob)

    print("  · geo — у всех 16 комплектов:")
    no_geo = [n for n in MOBS9 + GEO7 if not geo_have(n)]
    if no_geo:
        print("     ✗ нет geo: %s" % ", ".join(no_geo))
        fail.append("реестр: нет geo у %s" % ", ".join(no_geo))
    else:
        print("     ✓ geo есть у всех 16")

    print("  · блоки, предметы и броня (7 шт):")
    for name in GEO7:
        # Текстура может лежать в block/, item/ или armor/ (neuro_armor),
        # и предметы с geo-моделью называются `<name>_geo.png` —
        # реестр пишет имя предмета, а не файла текстуры.
        found = any(have(os.path.join(txt, sub), name)
                    or have(os.path.join(txt, sub), name + "_geo")
                    for sub in ("block", "item", "armor"))
        if found:
            ok += 1
            print("     ✓ %s" % name)
        else:
            bad += 1
            print("     ✗ %s — текстуры нет" % name)
            fail.append("реестр: у %s нет текстуры" % name)
    print("  реестр: комплектов 16, найдено %d, отсутствует %d" % (ok, bad))


# -------------------------------------------------------------- 10. Принятое
def check_keep_identical(extract_dir):
    ref = REF_360_REAL
    if ref is None:
        # Пропуск, а не расхождение: эталона нет ни на диске, ни в git.
        warn.append("эталон 3.6.0-R недоступен — Д1–Д7 не сверены (пропуск)")
        print("  ! эталон 3.6.0-R недоступен (ни на диске, ни в git) — "
              "Д1–Д7 не сверены")
        return
    same = diff = missing = 0
    with zipfile.ZipFile(ref) as z:
        names = set(z.namelist())
        for rel in KEEP_IDENTICAL:
            cand = [n for n in names if n.endswith(rel)]
            cur = os.path.join(extract_dir, rel)
            if not cand or not os.path.exists(cur):
                missing += 1
                print("  ✗ нет файла: %s" % rel)
                continue
            if z.read(cand[0]) == open(cur, "rb").read():
                same += 1
            else:
                diff += 1
                print("  ✗ ИЗМЕНЁН (принятое трогать нельзя): %s" % rel)
    print("  %s сверено с 3.6.0-R: идентично %d, изменено %d, нет %d"
          % ("✓" if diff == 0 and missing == 0 else "✗", same, diff, missing))
    if diff:
        fail.append("изменено принятых файлов: %d" % diff)
    if missing:
        fail.append("не найдено принятых файлов: %d" % missing)


# --------------------------------------------------------------------- 11. З-1
def check_z1_shade(extract_dir):
    """З-1: доля самой частой непрозрачной краски infected_creeper <= 35 %."""
    p = os.path.join(extract_dir, CREEPER)
    if not os.path.exists(p):
        print("  ✗ нет %s" % CREEPER)
        fail.append("З-1: infected_creeper.png в пакете нет")
        return
    py = _python_with("PIL")
    if py is None:
        print("  ✗ нет Pillow — З-1 не измерить")
        fail.append("З-1: нет Pillow")
        return
    code = (
        "from PIL import Image\n"
        "from collections import Counter\n"
        "import sys\n"
        "im = Image.open(sys.argv[1]).convert('RGBA')\n"
        "px = [p for p in im.getdata() if p[3] != 0]\n"
        "c = Counter(px)\n"
        "top, n = c.most_common(1)[0]\n"
        "print('%d %d %d %d %d' % (len(px), len(c), n, top[0], top[1]))\n"
    )
    r = subprocess.run([py, "-c", code, p], capture_output=True, text=True)
    if r.returncode != 0:
        print("  ✗ Pillow-замер не прошёл: %s" % r.stderr.strip()[:200])
        fail.append("З-1: замер не выполнен")
        return
    npx, ncol, top_n = (int(x) for x in r.stdout.split()[:3])
    share = 100.0 * top_n / npx if npx else 0.0
    ok = share <= SHADE_MAX
    print("  %s З-1 %s: непрозрачных %d, цветов %d, топ %d px = %.1f %% "
          "(порог ≤ %.0f %%)"
          % ("✓" if ok else "✗", os.path.basename(CREEPER), npx, ncol, top_n,
             share, SHADE_MAX))
    if not ok:
        fail.append("З-1: доля самой частой краски %.1f %% > %.0f %%"
                    % (share, SHADE_MAX))


# ------------------------------------------------- 12. Принятые слои побайтово
def check_accepted_layers(extract_dir):
    """Слои A4-p7-R и A3R1 обязаны лежать в пакете ПОБАЙТОВО.

    Блок 5 (glow_check) проверяет свечение, а не побайтовость: он пропустит
    вручную перекрашенный infected_creeper, если свечение и палитра совпали.
    Блок 12 жёстко сверяет с принятыми архивами. Партия именно `-R` (T-3119):
    старая A4p7_palette.zip — ДО З-1 (81,2 %), пакет собран из -R (28,3 %).
    """
    layers = [
        (os.path.join(REPO, "04-artist", "deliverables",
                      "Carnis_3.7.0_A4p7_palette-R.zip"), "A4-p7-R", 8),
        (os.path.join(REPO, "04-artist", "deliverables",
                      "Carnis_3.7.0_A3R1_tendrils_recolor.zip"), "A3R1", 4),
    ]
    for zp, tag, expect in layers:
        if not os.path.exists(zp):
            warn.append("%s: архива нет в 04-artist/deliverables" % tag)
            print("  ! %s: архива нет — слой не сверить" % tag)
            continue
        same = diff = missing = 0
        with zipfile.ZipFile(zp) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".png")]
            for n in names:
                cur = os.path.join(extract_dir, n)
                if not os.path.exists(cur):
                    missing += 1
                    print("  ✗ %s: в пакете нет %s" % (tag, os.path.basename(n)))
                elif z.read(n) == open(cur, "rb").read():
                    same += 1
                else:
                    diff += 1
                    print("  ✗ %s: файл изменён против принятого — %s"
                          % (tag, os.path.basename(n)))
        ok = (diff == 0 and missing == 0 and same == expect)
        print("  %s %s: в архиве %d, в пакете идентично %d, изменено %d, нет %d"
              % ("✓" if ok else "✗", tag, len(names), same, diff, missing))
        if diff:
            fail.append("%s: в пакете изменены принятые файлы (%d)" % (tag, diff))
        if missing:
            fail.append("%s: в пакете не хватает файлов (%d)" % (tag, missing))
        if same != expect:
            fail.append("%s: ожидалось %d файлов, совпало %d"
                        % (tag, expect, same))


# --------------------------------------------------- 13/14. Светотень (Художник)
SHADE = os.path.join(REPO, "04-artist", "tools", "shade_density.py")
CREATURE_DIR = "src/main/resources/assets/carnis/textures/entity"


def _shade_scan(extract_dir, subdir, tag, limit=200):
    """Общий сканер для блоков 13/14. Считаем долю топа сами (Pillow),
    чтобы не зависеть от CLI-обвязки чужого чекера: правило ТЗ — <= 35 %."""
    root = os.path.join(extract_dir, subdir)
    if not os.path.isdir(root):
        print("  ! каталога %s нет — пропущено" % subdir)
        warn.append("%s: каталога нет" % tag)
        return
    files = []
    skipped = 0
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            if not f.lower().endswith(".png"):
                continue
            # glowmask — одноцветная по определению (1 цвет свечения = норма,
            # подтверждено Ревизором (§1) и Художником (§«Итоги»). В аудит
            # светотени не входят: 100 % топа — это её смысл, а не дефект.
            if "glowmask" in f.lower():
                skipped += 1
                continue
            files.append(os.path.join(dp, f))
    files.sort()
    if skipped:
        print("  · glowmask пропущено: %d (одноцветные по определению)" % skipped)
    if not files:
        print("  ! в %s нет PNG" % subdir)
        warn.append("%s: PNG не найдено" % tag)
        return
    py = _python_with("PIL")
    if py is None:
        print("  ✗ нет Pillow — %s не измерить" % tag)
        fail.append("%s: нет Pillow" % tag)
        return
    code = (
        "from PIL import Image\n"
        "from collections import Counter\n"
        "import sys\n"
        "im = Image.open(sys.argv[1]).convert('RGBA')\n"
        "px = [p[:3] for p in im.getdata() if p[3] > 0]\n"
        "if not px:\n"
        "    print('0 0 0'); raise SystemExit(0)\n"
        "c = Counter(px); top, n = c.most_common(1)[0]\n"
        "print('%d %d %d' % (len(px), len(c), n))\n"
    )
    # З-18 (Ревизор): лимит 200 обрезал скан МОЛЧА — печаталось полное
    # число файлов, а проверялись первые 200. Теперь: если файлов больше
    # лимита, это не «всё ок», а непроверенная часть -> fail-closed.
    if len(files) > limit:
        print("  ✗ %s: PNG %d > лимита %d — часть текстур НЕ проверена"
              % (tag, len(files), limit))
        fail.append("%s: %d PNG при лимите %d — проверены не все"
                    % (tag, len(files), limit))
    bad = []
    worst = None
    for p in files[:limit]:
        r = subprocess.run([py, "-c", code, p], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append("%s: замер не прошёл" % os.path.basename(p))
            continue
        npx, ncol, top_n = (int(x) for x in r.stdout.split()[:3])
        rel = os.path.relpath(p, os.path.join(extract_dir, subdir))
        # З-18 (Ревизор): текстура без единого непрозрачного пикселя
        # проходила МОЛЧА — не попадала ни в bad, ни в «худший».
        # Затёртая альфа — это дефект, а не «нечего мерить».
        if npx == 0:
            print("  ✗ %s — НЕТ непрозрачных пикселей (α = 0 везде)" % rel)
            bad.append("%s — полностью прозрачная (α = 0)" % rel)
            continue
        share = 100.0 * top_n / npx
        if worst is None or share > worst[1]:
            worst = (rel, share, ncol)
        # З-16/З-18: правило «не меньше 7 цветов». Число цветов печаталось,
        # но ни с чем не сравнивалось — текстура в 6 цветов проходила
        # («6 цветов» никого не смутило). Ставим нижний порог наконец.
        if ncol < SHADE_MIN_COLORS:
            print("  ✗ %s — %d цвет(ов) < нормы %d (плоская заливка)"
                  % (rel, ncol, SHADE_MIN_COLORS))
            bad.append("%s — %d цветов < %d" % (rel, ncol, SHADE_MIN_COLORS))
        if share > SHADE_MAX:
            bad.append("%s — %.1f %% > %.0f %% (%d цветов)"
                       % (rel, share, SHADE_MAX, ncol))
    print("  %s %s: PNG %d, худший %s"
          % ("✓" if not bad else "✗", tag, len(files),
             "%.1f %% (%d цветов)" % (worst[1], worst[2]) if worst else "—"))
    for b in bad[:6]:
        print("      " + b)
    if bad:
        fail.append("%s: выше порога %.0f %% — %d текстур" % (tag, SHADE_MAX, len(bad)))


def check_creatures(extract_dir):
    _shade_scan(extract_dir, CREATURE_DIR, "существа")


def check_blocks(extract_dir):
    _shade_scan(extract_dir, BLOCK_DIR, "блоки")


# ------------------------------------------- 10б. Белый список перекрасок
def check_recolor_allowlist(extract_dir):
    """T-3142: принятые перекраски — побайтово равны сдаче Художника.

    KEEP_IDENTICAL этих трёх не защищает (исключены решением Архитектора),
    поэтому защита переносится сюда: файл в пакете обязан совпадать с
    архивом `Carnis_3.7.2_T3115_block_recolor.zip`. Иначе «разрешено» стало бы
    «разрешено что угодно» — дыра шире, чем была.
    """
    if not RECOLOR_ACCEPTED_372:
        return
    archives = {}
    ok_n = 0
    for dst, arch in sorted(RECOLOR_ACCEPTED_372.items()):
        zp = os.path.join(REPO, "04-artist", "deliverables", arch)
        if zp not in archives:
            archives[zp] = zipfile.ZipFile(zp) if os.path.exists(zp) else None
        z = archives[zp]
        if z is None:
            print("  ✗ белый список: нет архива %s" % arch)
            fail.append("перекраски: нет архива %s" % arch)
            continue
        cand = [n for n in z.namelist() if n.endswith(dst.split("/")[-1])]
        cur = os.path.join(extract_dir, dst)
        if not cand:
            print("  ✗ белый список: %s нет в сдаче" % os.path.basename(dst))
            fail.append("перекраски: %s нет в сдаче" % os.path.basename(dst))
            continue
        if not os.path.exists(cur):
            print("  ✗ белый список: %s нет в пакете" % os.path.basename(dst))
            fail.append("перекраски: %s нет в пакете" % os.path.basename(dst))
            continue
        if z.read(cand[0]) == open(cur, "rb").read():
            ok_n += 1
        else:
            print("  ✗ белый список: %s НЕ совпадает со сдачей — "
                  "«разрешено» стало «что угодно»" % os.path.basename(dst))
            fail.append("перекраски: %s не из сдачи Художника"
                        % os.path.basename(dst))
    total = len(RECOLOR_ACCEPTED_372)
    print("  %s белый список перекрасок T-3142: совпало со сдачей %d из %d"
          % ("✓" if ok_n == total else "✗", ok_n, total))


# ---------------------------------------------------------------- 15. Банк
def ogg_header(data):
    """Формат Ogg Vorbis: каналы и частота из заголовка идентификации."""
    i = data.find(b"OggS")
    if i < 0:
        return None
    nseg = data[i + 26]
    body = i + 27 + nseg + sum(data[i + 27:i + 27 + nseg])
    j = data.find(b"\x01vorbis", i, body + 64)
    if j < 0:
        return None
    channels = data[j + 11]
    rate = struct.unpack("<I", data[j + 12:j + 16])[0]
    return channels, rate


def _crest_noise_floor(checker, archive, py):
    """Шумовой пол round-trip-эталона: медиана и максимум |Δcrest| на оригиналах.

    Для каждого оригинала архива сравнивается crest файла и crest его же
    перекода тем же кодеком и параметрами. Всё, что получится, — шум трубы:
    никакой обработки не было. Без этого числа норма 0,05 дБ измеряет кодек.
    """
    try:
        spec = importlib.util.spec_from_file_location("_crest_ref", checker)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001
        print("      шумовой пол: чекер не импортирован (%s)" % exc)
        return None
    ds = []
    try:
        import glob
        for path in sorted(glob.glob(os.path.join(archive, "*.ogg"))):
            blob = open(path, "rb").read()
            a = mod.stats_of_bytes(blob)
            r = mod.roundtrip_stats(blob, 160000)
            if a and r:
                ds.append(abs((r[0] - r[1]) - (a[0] - a[1])))
    except Exception as exc:  # noqa: BLE001
        print("      шумовой пол: не измерен (%s)" % exc)
        return None
    if not ds:
        return None
    ds.sort()
    return ds[len(ds) // 2], ds[-1]


def _load_crest_master():
    path = os.path.join(REPO, "tools", "crest_master.py")
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location("crest_master", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001
        return None
    return mod


def check_crest(zip_path):
    """T-3182 §4: правка громкости не должна менять динамику.

    crest = Peak - RMS; чистое усиление сдвигает пик и RMS одинаково и crest
    не трогает. Если dcrest вылезло за 0,05 дБ - значит в файл попал
    лимитер/перекодирование/VBR, то есть изменилась динамика (дефект З-21,
    который не видела ни одна проверка). Fail-closed: нет чекера, нет архива
    или сверено меньше 15 файлов - это НЕ "ок", а "не проверено".
    """
    tol = 0.05
    checker = os.path.join(REPO, "02-reviewer", "tools", "crest_delta.py")
    archive = os.path.join(REPO, "03-sound", "archive_zapas_2026-11-26")
    if not os.path.isfile(checker):
        print("  x crest: нет чекера 02-reviewer/tools/crest_delta.py")
        fail.append("crest: чекер отсутствует - динамика не проверена")
        return
    if not os.path.isdir(archive):
        print("  x crest: нет архива оригиналов %s" % archive)
        fail.append("crest: архива оригиналов нет - сверять не с чем")
        return
    n_arch = len([f for f in os.listdir(archive) if f.endswith(".ogg")])
    if n_arch < 15:
        print("  x crest: в архиве %d файлов вместо 15" % n_arch)
        fail.append("crest: архив оригиналов неполон (%d из 15)" % n_arch)
        return
    py = _python_with("av") or sys.executable
    # З-28/I22: эталон — round-trip (исходник → декод → перекод тем же кодеком
    # и теми же параметрами → декод). Так Δcrest меряет ОБРАБОТКУ, а не шум
    # кодека: норма 0,05 дБ против исходного PCM недостижима для lossy —
    # Звук доказал прогоном, что 73 из 144 принятых файлов выходят за неё
    # при чистом транскоде без всякой правки.
    # I24/З-30: допуск per-file из эталонной таблицы Звука:
    #   допуск(файл) = max(порог_типа, baseline(файл) + 0,05 дБ)
    # Таблица — измеренный шум перекода для каждого файла, поэтому гейт не
    # зависит от того, каким энкодером собрана машина. Нет записи в таблице
    # -> чекер даёт код 3 «НЕ ПРОВЕРЕН», и это валит гейт: файл без
    # калибровки нельзя судить нормой, которой у него нет.
    # Таблица — 00-board/reports/sound_crest_baseline.md (276 записей, формат
    # «файл | тип | длина | разброс | baseline | порог | допуск»). Файл
    # 03-sound/crest_reference.md — отчёт Звука с ДРУГОЙ схемой колонок
    # (битрейт вместо типа), чекер его не разбирает: там 0 записей.
    table = os.path.join(REPO, "00-board", "reports",
                         "sound_crest_baseline.md")
    if not os.path.isfile(table):
        print("  x crest: нет эталонной таблицы "
              "00-board/reports/sound_crest_baseline.md")
        fail.append("crest: эталонной таблицы нет — допуск не откуда взять")
        return
    r = subprocess.run([py, checker, archive, zip_path,
                        "--tol", str(tol), "--top", "3", "--table", table],
                       capture_output=True, text=True)
    out = r.stdout
    over = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("! ")]
    m = re.search(r"Файлов сверено: (\d+)", out)
    n = int(m.group(1)) if m else 0
    m2 = re.search(r"Побайтово неизменённых \(норма не применяется, З-28 п\.2\): (\d+)", out)
    unchanged = int(m2.group(1)) if m2 else 0
    m3 = re.search(r"Только усиление \(crest неприменим по определению, З-28 п\.3\): (\d+)", out)
    gain_only = int(m3.group(1)) if m3 else 0
    for ln in over[:4]:
        print("      " + ln)
    # I22 требует СОСТАВ, а не только итог: иначе «зелено» может означать
    # «ни один файл не проверялся». Печатаем все три категории всегда.
    print("      состав: проверено по round-trip %d, побайтово неизменных %d, "
          "только усиление %d, всего в архиве %d"
          % (n, unchanged, gain_only, n_arch))
    if n + unchanged + gain_only < n_arch:
        print("  x crest: из %d файлов архива разобрано %d — часть не попала "
              "ни в одну категорию" % (n_arch, n + unchanged + gain_only))
        fail.append("crest: разобрано %d из %d файлов"
                    % (n + unchanged + gain_only, n_arch))
        return
    if n == 0 and unchanged >= n_arch:
        print("  v crest: все %d файлов побайтово неизменны — норма не "
              "применяется (З-28 п.2)" % n_arch)
        return
    # З-28 + R19 п.2: у round-trip-эталона есть собственный ШУМ ПЕРЕКОДА.
    # Измерил свою трубу на 15 оригиналах: медиана 0,140, максимум 0,325 дБ.
    # Ровно эти файлы и «выходили» за 0,05 — их Δcrest равен их же шуму,
    # то есть измерялся кодек, а не обработка. Поэтому файл валит только
    # если превысил СВОЙ шум на полный допуск: обработка тембра по R19 даёт
    # 0,75 дБ против шума 0,325 — отношение 2,3 и ловится; шум 0,30 против
    # шума 0,325 — отношение 1,0 и не валит. Печатаю пол всегда, чтобы
    # ослабление было видно, а не спрятано.
    noise = _crest_noise_floor(checker, archive, py)
    if noise is None:
        if over:
            print("  x crest: шум перекода не измерен, а выходы есть — "
                  "отличить шум от обработки нельзя")
            fail.append("crest: шум перекода не измерен, есть выходы за допуск")
        else:
            print("  v crest: %d проверено по round-trip, все в допуске %.2f дБ "
                  "(T-3182 §4 + З-28)" % (n, tol))
        return
    med, worst = noise
    print("      шумовой пол трубы: медиана %.3f дБ, максимум %.3f дБ "
          "(ниже него Δcrest ничего не значит)" % (med, worst))
    real = []
    for ln in over:
        m4 = re.search(r"(-?\d+\.\d+)\s*дБ", ln)
        if not m4:
            real.append(ln)
            continue
        d = abs(float(m4.group(1)))
        if d > worst + tol:
            real.append("%s (шум %.3f + допуск %.2f)" % (ln, worst, tol))
    if real:
        print("  x crest: %d файлов изменили динамику СВЕРХ шума перекода"
              % len(real))
        fail.append("crest: %d файлов изменили динамику сверх шума перекода"
                    % len(real))
    else:
        print("  v crest: %d проверено по round-trip; все выходы внутри шума "
              "перекода — обработки сверх нормы не найдено (T-3182 §4 + З-28)"
              % n)


def check_canon_manifest():
    """S65 (Звук): эталон канона обязан быть актуальным ДО сверки «банк == пакет».

    `MANIFEST_canon_144.txt` — единственный пригодный эталон канона (S60). Если
    файл канона изменился без пересчёта манифеста, приёмка сверяет с устаревшим
    эталоном и даёт ложные расхождения — молча. Звук просил одну строку в гейт:
    вызвать тест, при rc != 0 — fail. Тест не пересчитывает манифест намеренно:
    пересчёт на машине приёмки вернул бы машинозависимость (как с baseline).
    """
    checker = os.path.join(REPO, "tools", "manifest_canon_test.py")
    if not os.path.isfile(checker):
        print("  x манифест канона: нет теста tools/manifest_canon_test.py")
        fail.append("манифест канона: тест отсутствует — эталон не проверен")
        return
    r = subprocess.run([sys.executable, checker], capture_output=True, text=True)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    for ln in out.splitlines():
        if ln.strip():
            print("      " + ln.rstrip())
    if r.returncode == 0:
        print("  v манифест канона: актуален (144 файла, SHA256 сходятся)")
    elif r.returncode == 2:
        fail.append("манифест канона: файл изменён без пересчёта манифеста — "
                    "эталон устарел (S65)")
    else:
        fail.append("манифест канона: не проверен (код %d) — эталон канона "
                    "недоказуем" % r.returncode)


def check_bank_format(extract_dir):
    """ТЗ 3.7.2 §9, блок 13: формат банка однороден, клиппинга нет.

    Мерим по файлам пакета: моно и 44 100 Гц у всех, кроме того — ни одного
    файла нулевой длины. Клиппинг (peak >= 0 dBFS) требует декодера: если
    numpy+av есть — считаем, иначе честно пишем «не проверено», а не «ок».
    """
    root = os.path.join(extract_dir, SOUND_SUBDIR)
    if not os.path.isdir(root):
        print("  ! каталога звуков нет — пропущено")
        fail.append("банк: каталога звуков нет — проверять нечего")
        return
    total = 0
    bad_fmt = []
    empty = []
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            if not f.lower().endswith(".ogg"):
                continue
            total += 1
            p = os.path.join(dp, f)
            data = open(p, "rb").read()
            if len(data) < 64:
                empty.append(os.path.relpath(p, root))
                continue
            h = ogg_header(data)
            rel = os.path.relpath(p, root)
            if h is None:
                bad_fmt.append("%s — не Ogg Vorbis" % rel)
                continue
            ch, rate = h
            if ch != 1 or rate != 44100:
                bad_fmt.append("%s — %d кан., %d Гц" % (rel, ch, rate))
    print("  %s банк: .ogg %d, неверный формат %d, пустых %d"
          % ("✓" if not bad_fmt and not empty else "✗",
             total, len(bad_fmt), len(empty)))
    for b in bad_fmt[:5]:
        print("      " + b)
    if bad_fmt:
        fail.append("банк: формат отличается у %d файлов" % len(bad_fmt))
    if empty:
        fail.append("банк: пустых файлов %d" % len(empty))

    # клиппинг — только если есть декодер
    # З-Г1 (T-3163): искать надо интерпретатор с ТЕМ ЖЕ набором, что требует
    # код декодера ниже (`import sys, av, numpy`). Раньше проверялся только
    # numpy: без PyAV проверка молча выключалась и гейт оставался зелёным.
    py = _python_with("av, numpy")
    if py is None:
        print("  ✗ клиппинг НЕ ПРОВЕРЕН: нет интерпретатора с av+numpy")
        print("      это не «ок»: проверку уровней выполнить нечем")
        fail.append("банк: клиппинг не проверен — нет декодера av+numpy")
        return
    code = (
        "import sys, av, numpy as np\n"
        "c = av.open(sys.argv[1]); s = c.streams.audio[0]\n"
        "buf = []\n"
        "for fr in c.decode(s):\n"
        "    buf.append(fr.to_ndarray().astype('float32'))\n"
        "if not buf:\n"
        "    print('EMPTY'); raise SystemExit(0)\n"
        "x = np.concatenate([b.reshape(-1) for b in buf])\n"
        "print('%.6f' % float(np.max(np.abs(x))))\n"
    )
    peaks = []
    failed = 0
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            if not f.lower().endswith(".ogg"):
                continue
            p = os.path.join(dp, f)
            r = subprocess.run([py, "-c", code, p], capture_output=True,
                               text=True, timeout=300)
            if r.returncode != 0 or not r.stdout.strip():
                failed += 1
                continue
            try:
                peaks.append((os.path.relpath(p, root),
                              float(r.stdout.strip().split()[0])))
            except ValueError:
                failed += 1
    if failed:
        print("  ✗ клиппинг: %d файлов НЕ ДЕКОДИРОВАНЫ" % failed)
        fail.append("банк: %d файлов не декодированы" % failed)
    clip = [n for n, pk in peaks if pk >= 1.0]
    if peaks:
        mx = max(pk for _, pk in peaks)
        print("  %s клиппинг: измерено %d, peak max %.2f dBFS, клип %d"
              % ("✓" if not clip else "✗", len(peaks),
                 20 * __import__("math").log10(mx) if mx > 0 else -99,
                 len(clip)))
        for c in clip[:5]:
            print("      " + c)
        if clip:
            fail.append("банк: клиппинг у %d файлов" % len(clip))

        # T-3182 §1 (З-21): потолок не «нет клиппинга», а пик <= -1.20 dBFS
        # с запасом >= 0.20 дБ. Порог -1.00 (просто «не клиппинг») пропускал
        # файлы с пиком -1.01: формально не клиппинг, но регулятор громкости
        # в игре их уже перегружает. Решение Архитектора — жёстче.
        CEIL_DB = -1.20
        MARGIN_DB = 0.20
        over = []
        for n, pk in peaks:
            db = 20 * __import__("math").log10(pk) if pk > 0 else -99.0
            if db > CEIL_DB:
                over.append((n, db, CEIL_DB - db))
        if over:
            worst = min(m for _, _, m in over)
            print("  ✗ запас до нормы T-3182: %d файлов выше %.2f dBFS "
                  "(худший запас %.2f дБ, нужно >= %.2f)"
                  % (len(over), CEIL_DB, worst, MARGIN_DB))
            for n, db, m in sorted(over, key=lambda x: -x[1])[:5]:
                print("      %-40s %+.2f dBFS  запас %.2f" % (n, db, m))
            fail.append("банк: %d файлов выше потолка %.2f dBFS "
                        "(запас < %.2f дБ) — T-3182 §1"
                        % (len(over), CEIL_DB, MARGIN_DB))
        else:
            print("  ✓ запас: все файлы не выше %.2f dBFS (T-3182 §1)"
                  % CEIL_DB)

        # T-3188 (Архитектор): инвариант «банк = 144 .ogg, пакет == банк».
        # До этого: в банке лежали 158 файлов, из них 14 дублей `_w1516`,
        # а пакет содержал 144 — то есть «пакет == банк» не выполнялось
        # никогда, и никто этого не видел, потому что не сверялось.
        # З-27: 3.8.0 читает ДВА каталога — неизменяемый канон 3.7.x (144)
        # и свои новые файлы (132) = 276. Инструменты принимают путь
        # параметром, поэтому правка только здесь.
        banks = [os.path.join(REPO, "03-sound", "sounds"),
                 os.path.join(REPO, "03-sound", "sounds_380")]
        present = [b for b in banks if os.path.isdir(b)]
        if not present:
            print("  · банков нет — сверка пакет==банк пропущена")
            skipped_checks.append("банк: каталогов 03-sound/sounds* нет")
        else:
            bank_files = {}
            clashes = []
            for b in present:
                for dp, _, fs in os.walk(b):
                    for f in fs:
                        if f.lower().endswith(".ogg"):
                            rel = os.path.relpath(os.path.join(dp, f), b)
                            if rel in bank_files:
                                clashes.append(rel)
                            bank_files[rel] = os.path.join(dp, f)
            if clashes:
                print("  x банк: %d имён встречаются в двух каталогах "
                      "(версии перекрываются)" % len(clashes))
                for n in sorted(clashes)[:4]:
                    print("      " + n)
                fail.append("банк: %d имён в двух банках одновременно" % len(clashes))
            print("  · банков: %d (%s)" % (len(present),
                                           ", ".join(os.path.basename(x)
                                                     for x in present)))
            pkg_files = set()
            for dp, _, fs in os.walk(root):
                for f in fs:
                    if f.lower().endswith(".ogg"):
                        pkg_files.add(os.path.relpath(os.path.join(dp, f), root))
            print("  · банк хранилища: %d .ogg | пакет: %d"
                  % (len(bank_files), len(pkg_files)))
            # 14 дублей _w1516 — историческая грязь банка (T-3188), не пакета
            stray = [n for n in bank_files if n.endswith("_w1516.ogg")]
            not_in_pkg = sorted(set(bank_files) - pkg_files - set(stray))
            not_in_bank = sorted(pkg_files - set(bank_files))
            if len(stray) > 20:
                print("  ! в банке %d дублей _w1516 — чистка Звука ещё не дошла"
                      % len(stray))
            if not_in_pkg:
                print("  ✗ банк: %d файлов есть в хранилище, но НЕ в пакете"
                      % len(not_in_pkg))
                for n in not_in_pkg[:4]:
                    print("      " + n)
                fail.append("банк: %d .ogg не попали в пакет" % len(not_in_pkg))
            if not_in_bank:
                print("  ✗ банк: %d файлов пакета НЕТ в хранилище" % len(not_in_bank))
                for n in not_in_bank[:4]:
                    print("      " + n)
                fail.append("банк: %d .ogg пакета нет в банке" % len(not_in_bank))
            if not not_in_pkg and not not_in_bank:
                # З-Г7: печатать ФАКТИЧЕСКОЕ число исключённых дублей.
                # Раньше строка была зашита «14 дублей» — после чистки банка
                # (T-3188) дублей стало 0, а зелёная строка продолжала
                # утверждать 14. Такая «зелёная» строка врёт тише, чем
                # красная, и потому опаснее.
                if stray:
                    print("  ✓ пакет == банк по составу (%d из %d, %d дублей "
                          "_w1516 исключены как грязь хранилища)"
                          % (len(pkg_files), len(pkg_files), len(stray)))
                else:
                    print("  ✓ пакет == банк по составу (%d из %d, дублей нет)"
                          % (len(pkg_files), len(pkg_files)))


# ------------------------------------------------------------------------ main
def find_manifest(zip_path, given):
    """Найти манифест. Возвращает (путь или None, источник).

    Источник важен: манифест РЯДОМ с пакетом — доверенный (строгая сверка),
    манифест из резервного пути репозитория — нет (З-18): пакет мог быть
    получен из git, и тогда в рабочем дереве лежит манифест другой сборки.
    """
    # 1) явно указанный путь — уважаем.
    if given:
        if os.path.exists(given):
            return given, "given"
        print("  ! указанный манифест не найден: %s — ищу рядом с пакетом"
              % given)
    # 2) З-18: сосед пакета — главный источник.
    if zip_path.endswith(".zip"):
        near = zip_path[:-4] + ".manifest.txt"
        if os.path.exists(near):
            return near, "near"
    for ext in (".manifest.txt", ".manifest", ".sha256", ".txt"):
        q = zip_path[:-4] + ext if zip_path.endswith(".zip") else zip_path + ext
        if os.path.exists(q):
            return q, "near"
    # 3) резерв — путь репозитория по версии (НЕ доверенный).
    if os.path.exists(DEFAULT_MANIFEST):
        return DEFAULT_MANIFEST, "repo"
    return None, "none"

def main():
    global REF_360_REAL, REF_STATUS, REF_SRC
    zip_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ZIP
    # З-18: манифест по умолчанию — СОСЕД пакета, а не фиксированный путь
    # репозитория. Иначе проверяющий, взявший ZIP из git, сверяет его со
    # старым манифестом своего рабочего дерева и получает ложное
    # «не сошлось N строк» на корректном пакете. Путь репо — резерв.
    man_arg = sys.argv[2] if len(sys.argv) > 2 else None

    # З-17: разрешаем эталон ОДИН раз до всех блоков. Порядок важен: блоки 5,
    # 6 и 10 пользуются результатом, а не проверяют диск сами.
    REF_360_REAL, REF_STATUS, REF_SRC = resolve_ref()

    print("Приёмка пакета %s (ТЗ %s)" % (VERSION, VERSION))
    if not os.path.exists(zip_path):
        print()
        print("ПАКЕТ НЕ НАЙДЕН: %s" % zip_path)
        print("Ждём: T-3115 (блоки), T-3122 (существа), T-3121 (банк) →")
        print("      Кодер собирает 01-coder/%s/project-%s-clean.zip + манифест"
              % (VERSION, VERSION))
        return 2

    # --- З-6 (T-3125): ни один неверный путь не даёт трейсбек и не даёт
    # код 1. Код 1 по контракту = «ЕСТЬ РАСХОЖДЕНИЯ» (приговор пакету),
    # поэтому ошибка запуска обязана быть кодом 2.
    if os.path.isdir(zip_path):
        print()
        print("ЭТО КАТАЛОГ, А НЕ ZIP: %s" % zip_path)
        print("Приёмка идёт по ZIP-пакету. Пример:")
        print("  python3 tools/%s %s/project-%s-clean.zip"
              % (os.path.basename(__file__), 
                 os.path.relpath(os.path.join(REPO, "01-coder", VERSION), REPO),
                 VERSION))
        return 2
    if not zipfile.is_zipfile(zip_path):
        print()
        print("НЕ ZIP ИЛИ БИТЫЙ АРХИВ: %s" % zip_path)
        print("Код 2 — ошибка запуска, а не приговор пакету.")
        return 2

    print("Пакет:   %s" % os.path.relpath(zip_path, REPO))
    print("Размер:  %d Б" % os.path.getsize(zip_path))
    h = subprocess.run(["sha256sum", zip_path], capture_output=True, text=True)
    print("SHA-256: %s" % h.stdout.split()[0])
    print()

    tmp = tempfile.mkdtemp(prefix="accept371_")
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            print("Распаковано %d записей, дубликатов путей %d."
                  % (len(names), len(names) - len(set(names))))
            z.extractall(tmp)

        print()
        print("1) Манифест (sha256sum -c)")
        m, m_src = find_manifest(zip_path, man_arg)
        if m:
            print("   %s" % os.path.relpath(m, REPO))
        check_manifest(tmp, m, m_src)

        print()
        print("1а) Дельта к 3.7.2 — только ожидаемые изменения")
        check_delta_372(zip_path)

        print()
        print("2) JSON")
        check_json(tmp)
        check_readme_license(zip_path)
        check_deps_soft(zip_path)
        check_volume_double(zip_path)

        print()
        print("3) Версия %s в четырёх местах" % VERSION)
        check_version(tmp, zip_path)

        print()
        print("4) Overlay (cmp источник — пакет)")
        check_overlay(tmp)

        print()
        print("5) A4-p7-R — палитра существ (ТЗ §4)")
        if os.path.exists(GLOW_CHECK):
            # З-17: передаём только РАЗРЕШЁННЫЙ эталон. Если его нет —
            # не передаём вовсе, и чекер скажет «ПРОПУЩЕНО» (код 2), а не ✗.
            glow_args = [zip_path]
            if REF_360_REAL:
                glow_args.append(REF_360_REAL)
            run_tool("glow_check", GLOW_CHECK, *glow_args, need="PIL")
        else:
            fail.append("tools/glow_check.py отсутствует — A4-p7 не проверить")

        print()
        print("6) A3R1 — цвет щупалец под плоть")
        if os.path.exists(TENDRIL):
            run_tool("tendril_flesh_match", TENDRIL, zip_path, need="PIL")
        else:
            fail.append("tools/tendril_flesh_match.py отсутствует — A3R1 не проверить")

        print()
        print("7) K8-S — сиротские .ogg (ТЗ §7)")
        if os.path.exists(ORPHANS):
            run_tool("sound_orphans", ORPHANS, zip_path)
        else:
            fail.append("tools/sound_orphans.py отсутствует — K8-S не проверить")

        print()
        print("8) Ambient-фикс (Р-31.2 / ТЗ §2)")
        check_ambient(tmp)
        if os.path.exists(AMBIENT_GATE):
            run_tool("ambient_gate (Ревизор)", AMBIENT_GATE, zip_path)
        else:
            warn.append("ambient_gate.py нет — только моя числовая проверка")

        print()
        print("9) Тембр ambient — T-3104 / T-3106 (доля < 80 Гц ≤ 25 %, "
              "центр ≥ 400 Гц)")
        if os.path.exists(TIMBRE):
            run_tool("timbre_check (Ревизор)", TIMBRE, zip_path,
                     need="numpy")
        else:
            fail.append("tools/timbre_check.py отсутствует — тембр не проверить")

        print()
        print("9б) Требования к установке против mods.toml (I100)")
        DEPS_INSTALL = os.path.join(REPO, "tools", "deps_install_check.py")
        if os.path.exists(DEPS_INSTALL):
            run_tool("deps_install_check", DEPS_INSTALL, zip_path)
        else:
            fail.append("tools/deps_install_check.py отсутствует — "
                        "требования к установке не проверить")

        print()
        print("9в) Итоговая громкость по спеке (S78 / отзыв Ревизора 95476a3)")
        VOL_EFF = os.path.join(REPO, "tools", "volume_effective_check.py")
        VOL_SPEC = os.path.join(REPO, "03-sound", "spec", "volume_spec_t3202.json")
        pkg_dir = os.path.dirname(zip_path)
        if not os.path.exists(VOL_EFF):
            fail.append("tools/volume_effective_check.py отсутствует — "
                        "громкость по спеке не проверить")
        elif not os.path.exists(VOL_SPEC):
            fail.append("03-sound/spec/volume_spec_t3202.json отсутствует — "
                        "цели по сэмплам не проверить")
        else:
            run_tool("volume_effective_check", VOL_EFF,
                     "--pkg", pkg_dir, "--spec", VOL_SPEC, report=True)

        print()
        print("9г) Разброс сэмплов внутри события — норма без спеки (S84 Audio)")
        SAMPLE_LOUD = os.path.join(REPO, "tools", "sample_loudness.py")
        bank = os.path.join(REPO, "03-sound", "sounds")
        if not os.path.exists(SAMPLE_LOUD):
            fail.append("tools/sample_loudness.py отсутствует — разброс "
                        "сэмплов не проверить")
        elif not os.path.isdir(bank):
            fail.append("банк 03-sound/sounds отсутствует — разброс не проверить")
        else:
            # ⛔ Этот тест меряет САМИ .ogg банка и не читает спеку целей —
            # поэтому он не может быть кругом «спека подтверждает себя»
            # (S84 Звука, reviewer_volume_retraction §7).
            # ⚠ НО: он смотрит БАНК, а не пакет, и его вердикт не зависит от
            # `volume` в sounds.json. В 3.7.x канон 144 заморожен (R18), то
            # есть исправить разброс правкой .ogg внутри версии НЕЛЬЗЯ. Если
            # поставить его нормой, пакет становится неисправимым — гейт
            # красный при любом значении volume. Поэтому здесь ОТЧЁТ:
            # находка видна и обязательна к разбору, а норма включается в
            # 3.7.4/3.8.0, где банк режется заново.
            run_tool("sample_loudness", SAMPLE_LOUD, "--bank", bank,
                     need="soundfile", report=True)

        print()
        print("10) Принятое не тронуто (14 файлов 3.6.0-R побайтово)")
        check_keep_identical(tmp)

        print()
        print("10в) З-1 — плотность светотени infected_creeper (наследие 3.7.0)")
        check_z1_shade(tmp)

        print()
        print("10г) Принятые слои лежат в пакете побайтово (A4-p7-R, A3R1)")
        check_accepted_layers(tmp)

        print()
        print("10б) Перекраски T-3115 — побайтово из сдачи (T-3142)")
        check_recolor_allowlist(tmp)

        print()
        print("11) Существа — плотность светотени (ТЗ 3.7.2 §9)")
        check_creatures(tmp)

        print()
        print("12) Блоки — плотность светотени (ТЗ 3.7.2 §9)")
        check_blocks(tmp)

        print()
        print("12а) Crest — динамика не изменена (T-3182 §4)")
        check_crest(zip_path)

        print()
        print("12б) Crest и атака от МАСТЕРОВ (З-31, без тавтологии)")
        # Тот же модуль, что и в 3.7.3: одна реализация нормы на оба гейта.
        # Прежний блок 12а в этом гейте остался со старым «rescue» (шум+допуск)
        # и расходился с 3.7.3 — Ревизор I23 §9 назвал это consistency debt.
        # 12б не заменяет 12а, а добавляет сверку от PCM-мастеров.
        _cm = _load_crest_master()
        if _cm is None:
            print("  x crest/атака: нет модуля tools/crest_master.py")
            fail.append("crest/атака: модуль проверки отсутствует")
        else:
            for msg in _cm.check_crest_attack(tmp):
                fail.append(msg)

        print()
        print("13) Банк — формат и клиппинг (ТЗ 3.7.2 §9)")
        check_bank_format(tmp)
        check_canon_manifest()

        print()
        print("14) Свечение 9 мобов — правило Р-3 (ТЗ 3.7.3)")
        check_glow9(tmp)

        print()
        print("16) Новые существа 3.8.0 — geo/текстура/glowmask (волна 52)")
        check_new_creatures(tmp)

        print()
        print("15) Реестр существ — 16 комплектов (ТЗ 3.7.3)")
        check_registry(tmp)

        print()
        if warn:
            print("Предупреждения: %d" % len(warn))
            for w in warn:
                print("  - %s" % w)
        if fail:
            print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ — %d" % len(fail))
            for i, f in enumerate(fail, 1):
                print("  %2d. %s" % (i, f))
            return 1
        # З-20 (fail-closed, решение Архитектора): ПРОПУСК — ЭТО НЕ УСПЕХ.
        # Гейт, зелёный при непроведённой проверке, даёт ложную гарантию, и CI
        # по ней выпускает релиз. Поэтому пропуск валит приёмку.
        if skipped_checks:
            print("ИТОГ: ПРОВЕРКА НЕ ВЫПОЛНЕНА — fail-closed (З-20), %d:"
                  % len(skipped_checks))
            for s in skipped_checks:
                print("  · %s" % s)
            print("Пакет НЕ отвергнут по существу: дефектов не найдено.")
            print("Но и не принят: часть проверок не выполнена, а «зелёный без")
            print("проверки» хуже падения — по нему выпускают релиз.")
            print("Лечение: обеспечить доступность эталона/манифеста (см. З-17/З-18)")
            print("и прогнать гейт заново. Код 2 — «не проверено», не «принято».")
            return 2
        # ⛔ Отчётные находки обязаны быть видны В ФИНАЛЬНОЙ строке. Иначе
        # «ПРИНЯТО» их прячет: дефект `detail_flow` (разброс 7,7 дБ) проходит
        # приёмку зелёным, и это ровно то, на чём ошибся Ревизор 2026-11-26.
        # Не валим — критерий пока не норма, — но и не молчим.
        if warn:
            print("ИТОГ: ПРИНЯТО — нормативные проверки пройдены.")
            print("  ⚠ ОТЧЁТНЫХ НАХОДОК: %d — приёмку не валят, но требуют "
                  "разбора:" % len(warn))
            for w in warn:
                print("    · %s" % w)
            print("  Решение по ним: 00-board/reports/integrator_s84_circularity_answer.md")
        else:
            print("ИТОГ: ПРИНЯТО — все проверки пройдены.")
        print("Дальше: CI на новом коммите → merge PR → тег v%s → Release."
              % VERSION)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
