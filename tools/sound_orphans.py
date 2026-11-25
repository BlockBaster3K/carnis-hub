#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sound_orphans.py — аудит сиротских .ogg (K8-S, ТЗ 3.7.0 §3).

Сирота = файл .ogg лежит в пакете, но ни одно событие sounds.json на него
не ссылается. Критерий приёмки 3.7.0 §3: «либо 0 файлов-сирот в JAR,
либо оба подключены и слышны».

Также ловит обратную ошибку: ссылка в sounds.json на несуществующий файл
(«ссылка в пустоту») — она ломает звук на клиенте.

С T-3185 ловит и **третье** направление, которое раньше не проверял никто:
событие `ModSounds` объявлено, звук в банке есть, а **вызова в коде нет** —
звук загружен, но недостижим (находка Звука: 11 событий / 15 файлов).
Такое событие теперь **проваливает проверку** (fail-closed), а не пишется
предупреждением.

Использование:
    python3 tools/sound_orphans.py <каталог|zip> [--quiet]

Код возврата:
    0 — сирот 0, ссылок в пустоту 0, недостижимых событий 0;
    2 — есть замечания по ассетам (сироты/ссылки в пустоту) — исторический код;
    3 — есть **недостижимые события** (T-3185): отдельный код нужен потому, что
        гейты `accept_3.7.x.py` трактуют код 2 как «пропущено/замечания» и
        пакет проходит (это и была дыра). Код 3 гейт валит как ✗;
    1 — ошибка запуска / нечего проверять (fail-closed).
"""

import io
import json
import os
import re
import sys
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# З-26: allowlist «задел». Часть событий недостижима СОЗНАТЕЛЬНО — например
# FLAMETHROWER_FIRE: механики огнемёта в моде ещё нет, но звук записан и лежит
# в банке как задел. Такое событие надо отличать от недостижимого по ошибке:
# первое печатается строкой, второе валит проверку.
ALLOWLIST = os.path.join(REPO_ROOT, "00-board", "reports",
                         "sound_orphans_allowlist.md")
ALLOW_MARK = re.compile(r"^\s*[-*]\s*`?([A-Z][A-Z0-9_]+)`?\s*[\u2014-]\s*(.+)$")


def load_allowlist(path=None):
    """Прочитать allowlist. Возвращает {ИМЯ: причина} или None, если файла нет.

    None (файла нет) — это «проверка не выполнена», а не «всё разрешено»:
    иначе достаточно удалить файл, чтобы любое недостижимое событие
    перестало валиться.
    """
    path = path or ALLOWLIST
    if not os.path.isfile(path):
        return None
    allowed = {}
    for line in open(path, encoding="utf-8"):
        m = ALLOW_MARK.match(line)
        if m:
            allowed[m.group(1)] = m.group(2).strip()
    return allowed


ASSETS = "assets/carnis/"
SOUNDS_JSON = ASSETS + "sounds.json"
SOUNDS_DIR = ASSETS + "sounds/"


def norm(path):
    """assets/carnis/sounds/block/x.ogg -> carnis:block/x"""
    p = path.replace("\\", "/")
    i = p.find(SOUNDS_DIR)
    if i < 0:
        return None
    rel = p[i + len(SOUNDS_DIR):]
    if not rel.endswith(".ogg"):
        return None
    return "carnis:" + rel[:-4]


def collect(src):
    """Вернуть (множество ссылок, множество файлов, dict sounds.json)."""
    files = set()
    data = None

    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                k = norm(n)
                if k:
                    files.add(k)
            want = [n for n in z.namelist()
                    if n.replace("\\", "/").endswith(SOUNDS_JSON)]
            if want:
                with z.open(want[0]) as f:
                    data = json.load(io.BytesIO(f.read()))
    else:
        # Ищем sounds.json, затем считаем .ogg РЯДОМ с ним (в той же ветке
        # assets/carnis/). Иначе можно взять generated/sounds.json и считать
        # файлы в main/resources — два разных пути, ложные «ссылки в пустоту».
        sj = os.path.join(src, SOUNDS_JSON)
        if not os.path.exists(sj):
            for dp, _, fs in os.walk(src):
                if "sounds.json" in fs:
                    sj = os.path.join(dp, "sounds.json")
                    break
        if os.path.exists(sj):
            with open(sj, encoding="utf-8") as f:
                data = json.load(f)
            sdir = os.path.join(os.path.dirname(sj), "sounds")
            for dp, _, fs in os.walk(sdir):
                for f in fs:
                    if f.endswith(".ogg"):
                        full = os.path.join(dp, f)
                        rel = os.path.relpath(full, sdir).replace(os.sep, "/")
                        files.add("carnis:" + rel[:-4])

    if data is None:
        raise SystemExit("ОШИБКА: не найден %s в %s" % (SOUNDS_JSON, src))

    refs = set()
    for _ev, body in data.items():
        for s in body.get("sounds", []):
            name = s if isinstance(s, str) else s.get("name", "")
            if name:
                refs.add(name)
    return refs, files, data


RE_CONST = re.compile(
    r"RegistryObject\s*<\s*SoundEvent\s*>\s+([A-Z0-9_]+)\s*=\s*[^;]*?\"([^\"]+)\"",
    re.S)


def read_sources(src):
    """Вернуть {имя файла: текст} для всех .java в пакете/каталоге."""
    out = {}
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.endswith(".java"):
                    try:
                        out[n.split("/")[-1]] = z.read(n).decode("utf-8", "replace")
                    except (KeyError, OSError):
                        pass
    else:
        for dp, _, fs in os.walk(src):
            for f in fs:
                if f.endswith(".java"):
                    try:
                        with open(os.path.join(dp, f), encoding="utf-8",
                                  errors="replace") as fh:
                            out[f] = fh.read()
                    except OSError:
                        pass
    return out


def unreachable_events(sources):
    """События ModSounds без единого вызова в коде -> список (константа, ключ).

    Достижимо, если имя константы встречается как `ModSounds.ИМЯ` вне
    ModSounds.java либо импортировано статически и используется по имени.
    """
    mod = sources.get("ModSounds.java")
    if not mod:
        return None
    consts = RE_CONST.findall(mod)
    if not consts:
        return None
    others = {k: v for k, v in sources.items() if k != "ModSounds.java"}
    static_imported = set()
    for text in others.values():
        for m in re.finditer(r"import\s+static\s+[\w.]*ModSounds\.([A-Z0-9_]+)\s*;", text):
            static_imported.add(m.group(1))
    dead = []
    for name, key in consts:
        used = False
        pat_qual = re.compile(r"\bModSounds\s*\.\s*" + name + r"\b")
        for text in others.values():
            if pat_qual.search(text):
                used = True
                break
        if not used and name in static_imported:
            pat_bare = re.compile(r"(?<![\w.])" + name + r"\b")
            for text in others.values():
                body = re.sub(r"import\s+static[^;]*;", "", text)
                if pat_bare.search(body):
                    used = True
                    break
        if not used:
            dead.append((name, key))
    return dead


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in sys.argv
    assets_only = "--assets-only" in sys.argv
    use_allow = "--no-allowlist" not in sys.argv
    if not args:
        print(__doc__)
        return 1
    src = args[0]
    if not zipfile.is_zipfile(src) and not os.path.isdir(src):
        print("ОШИБКА: нет такого каталога или zip: %s" % src)
        return 1

    try:
        refs, files, data = collect(src)
    except SystemExit as e:
        print(e)
        return 1

    orphans = sorted(files - refs)
    dangling = sorted(refs - files)

    if not quiet:
        print("Аудит сирот .ogg (K8-S, ТЗ 3.7.0 §3)")
        print("Пакет:     %s" % src)
        print("Событий в sounds.json: %d, ссылок на файлы: %d, файлов .ogg: %d"
              % (len(data), len(refs), len(files)))
        print()

    if orphans:
        print("СИРОТЫ (%d) — файл есть, ссылок нет:" % len(orphans))
        for o in orphans:
            print("  - %s.ogg" % o)
    elif not quiet:
        print("Сирот нет: 0")

    if dangling:
        print()
        print("ССЫЛКИ В ПУСТОТУ (%d) — sounds.json зовёт несуществующий файл:"
              % len(dangling))
        for d in dangling:
            print("  - %s" % d)

    # --- третье направление: событие объявлено, но не вызывается (T-3185)
    dead = None
    if not assets_only:
        sources = read_sources(src)
        dead = unreachable_events(sources)
        if dead is None:
            print()
            print("ПРОВЕРКА НЕДОСТИЖИМЫХ СОБЫТИЙ НЕ ВЫПОЛНЕНА: в источнике нет "
                  "ModSounds.java (нужен пакет/каталог с кодом)")
            print("ИТОГ: НЕ ПРОВЕРЕНО — fail-closed (для одних ассетов: --assets-only)")
            return 2
        print()
        # З-26: разделяем «сознательный задел» и «недостижимо по ошибке».
        allowed, allow_unknown = {}, []
        if dead and use_allow:
            table = load_allowlist()
            if table is None:
                print("ALLOWLIST НЕ НАЙДЕН: %s" % ALLOWLIST)
                print("ИТОГ: НЕ ПРОВЕРЕНО — fail-closed (З-26: без файла "
                      "allowlist «задел» не отличить от ошибки)")
                return 2
            dead_names = {n for n, _k in dead}
            rest = []
            for name, key in dead:
                if name in table:
                    allowed[name] = (key, table[name])
                else:
                    rest.append((name, key))
            allow_unknown = sorted(set(table) - dead_names)
            dead = rest
        if allowed:
            print("ЗАДЕЛ ПО ALLOWLIST (%d) — недостижимо сознательно (З-26):"
                  % len(allowed))
            for name, (key, why) in sorted(allowed.items()):
                print("  ~ ModSounds.%-28s (ключ \"%s\") — %s" % (name, key, why))
            print()
        if dead:
            print("НЕДОСТИЖИМЫЕ СОБЫТИЯ (%d) — объявлены в ModSounds, вызова в коде нет:"
                  % len(dead))
            for name, key in dead:
                print("  - ModSounds.%-28s (ключ \"%s\")" % (name, key))
        elif not allowed:
            print("Недостижимых событий нет: 0")
        if allow_unknown:
            print()
            print("! в allowlist %d записей, которых нет среди недостижимых: %s"
                  % (len(allow_unknown), ", ".join(allow_unknown[:6])))
            print("  (не валит проверку — устаревшие строки, стоит убрать)")

    print()
    if orphans or dangling or dead:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — сирот %d, ссылок в пустоту %d, "
              "недостижимых событий %d"
              % (len(orphans), len(dangling), len(dead or [])))
        # 3 — чтобы гейт (для которого 2 = «пропущено») не пропустил пакет
        return 3 if dead else 2
    print("ИТОГ: СХОДИТСЯ — сирот 0, ссылок в пустоту 0, недостижимых событий 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
