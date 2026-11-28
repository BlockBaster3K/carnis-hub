#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release_jar_check.py — собран ли опубликованный JAR ровно из принятого пакета.

Зачем (R14, находка импульса 78): релиз 3.7.3 собран из **аннулированного**
пакета — JAR отдан за ту же версию, что принята, а внутри прежние звуки.
Проверка сравнивает АССЕТЫ (то, что игрок реально получает) по sha256:
`assets/carnis/**` в JAR против `src/main/resources/assets/carnis/**` в ZIP.

Лишние файлы в JAR допустимы и перечисляются: Forge-датаген кладёт
`models/`, `blockstates/`, `lang/` при сборке, в «чистом» пакете их нет.
Недостающие файлы и расхождения по байтам — провал.

Использование:
    python3 tools/release_jar_check.py --jar 06-build/jars/carnis-3.8.0.jar \\
            --pkg 01-coder/3.8.0/project-3.8.0-clean.zip
    python3 tools/release_jar_check.py --tag v3.7.3 --version 3.7.3   # из git

Коды возврата: 0 — JAR соответствует пакету, 2 — расхождения, 1 — ошибка запуска.
"""

import argparse
import hashlib
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ASSETS_IN_JAR = "assets/carnis/"
ASSETS_IN_PKG = "src/main/resources/assets/carnis/"
GENERATED = ("models/", "blockstates/", "lang/")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def assets_from_zip(path, prefix):
    out = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.startswith(prefix) and not n.endswith("/"):
                out[n[len(prefix):]] = _sha(z.read(n))
    return out


def jar_from_git(tag):
    """Блоб JAR из коммита тега: возвращает путь к временному файлу или None."""
    try:
        tree = subprocess.run(
            ["git", "-C", REPO, "ls-tree", "-r", tag, "--", "06-build/jars/"],
            capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None, "git ls-tree %s не сработал" % tag
    # В коммите тега лежат JAR всех прошлых версий — брать надо ТУ, что в
    # теге. Ошибка выбора (брался последний по обходу) заставила инструмент
    # сравнивать 3.7.3 с JAR 3.8.0: 322 «лишних» файла и ложный вывод.
    want = tag[1:] if tag.startswith("v") else tag
    jar_name, blob = None, None
    for line in tree.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[3].endswith(".jar"):
            if os.path.basename(parts[3]) == "carnis-%s.jar" % want:
                jar_name, blob = parts[3], parts[2]
                break
    if not blob:
        return None, "в коммите тега %s нет ни одного .jar" % tag
    tmp = os.path.join("/tmp", os.path.basename(jar_name))
    with open(tmp, "wb") as fh:
        r = subprocess.run(["git", "-C", REPO, "cat-file", "blob", blob],
                           stdout=fh)
    if r.returncode != 0:
        return None, "не удалось достать блоб %s" % blob
    return tmp, "из git: %s (тег %s)" % (jar_name, tag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", help="путь к собранному JAR")
    ap.add_argument("--pkg", help="путь к принятому ZIP-пакету")
    ap.add_argument("--tag", help="взять JAR из коммита тега (вместо --jar)")
    a = ap.parse_args()

    origin = a.jar
    if not origin:
        if not a.tag:
            print("ОШИБКА: нужен --jar или --tag")
            return 1
        origin, note = jar_from_git(a.tag)
        if not origin:
            print("ОШИБКА: %s" % note)
            return 1
        print("JAR %s" % note)
    if not a.pkg:
        print("ОШИБКА: нужен --pkg (принятый пакет)")
        return 1

    for path in (origin, a.pkg):
        if not os.path.isfile(path):
            print("ОШИБКА: нет файла %s" % path)
            return 1

    jar_assets = assets_from_zip(origin, ASSETS_IN_JAR)
    pkg_assets = assets_from_zip(a.pkg, ASSETS_IN_PKG)
    if not pkg_assets:
        print("ОШИБКА: в пакете нет %s — сравнивать нечего" % ASSETS_IN_PKG)
        return 1
    if not jar_assets:
        print("ОШИБКА: в JAR нет %s — это не собранный мод" % ASSETS_IN_JAR)
        return 1

    missing = sorted(set(pkg_assets) - set(jar_assets))
    extra = sorted(set(jar_assets) - set(pkg_assets))
    differ = sorted(k for k in set(pkg_assets) & set(jar_assets)
                    if pkg_assets[k] != jar_assets[k])
    generated = [k for k in extra if k.startswith(GENERATED)]
    unexpected = [k for k in extra if k not in generated]

    print("пакет: ассетов %d | JAR: ассетов %d" % (len(pkg_assets), len(jar_assets)))
    print("нет в JAR: %d | расхождений по байтам: %d | лишних: %d "
          "(датаген %d, прочие %d)"
          % (len(missing), len(differ), len(extra), len(generated),
             len(unexpected)))
    for k in differ[:10]:
        print("   ! %-48s пакет %s  JAR %s"
              % (k, pkg_assets[k][:12], jar_assets[k][:12]))
    for k in missing[:10]:
        print("   ! нет в JAR: %s" % k)

    if missing or differ or unexpected:
        print("ИТОГ: JAR НЕ СООТВЕТСТВУЕТ принятому пакету — релиз собран "
              "не из тех байтов")
        return 2
    print("ИТОГ: JAR соответствует пакету (все %d ассетов совпали по sha256)"
          % len(pkg_assets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
