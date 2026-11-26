#!/usr/bin/env python3
"""Требования к установке против факта в пакете (I100).

Зачем
-----
Волна 58 требует описать, что нужно на сервере, что на клиенте и что
необязательно. Текст такого документа устаревает молча: Кодер добавит
зависимость в `mods.toml`, а игрок продолжит читать «ничего не нужно» и
получит краш.

Эта проверка сверяет ДОКУМЕНТ с `mods.toml` пакета, а не с текстом ТЗ.

Коды
----
0 — документ и пакет согласованы
2 — расхождение: в пакете есть жёсткая зависимость, не описанная в документе,
    либо документ требует того, чего в пакете нет
1 — документ или пакет не найдены (fail-closed)
"""
import os
import re
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(REPO, "00-board", "reports", "install_requirements.md")

# Моды, которые документ обязан описывать построчно.
WATCHED = ["curios", "patchouli", "smartbrainlib", "lodestone",
           "soundphysics", "geckolib", "forge", "minecraft"]


def read_mods_toml(zip_path):
    """{modId: mandatory} из mods.toml пакета."""
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.endswith("META-INF/mods.toml")]
        if not names:
            return None
        text = z.read(names[0]).decode("utf-8", "replace")
    deps = {}
    blocks = re.split(r"\[\[dependencies\.", text)[1:]
    for b in blocks:
        mid = re.search(r'modId\s*=\s*"([^"]+)"', b)
        mand = re.search(r"mandatory\s*=\s*(true|false)", b)
        if mid:
            deps[mid.group(1).lower()] = (mand.group(1) == "true") if mand else True
    return deps


def doc_mentions(text, lib):
    """Говорит ли документ про библиотеку."""
    return re.search(lib, text, re.IGNORECASE) is not None


# ⛔ Первая версия читала ПРОЗУ документа и на живом файле дала 11 ложных ✗:
# строка «Curios, Patchouli, SmartBrainLib, Lodestone, Sound Physics —
# **не требуются**» перечисляет пять библиотек сразу, и «отрицание рядом»
# относится к любой из них, а не к той, которую искали. Разбор прозы
# ненадёжен по своей природе. Поэтому документ объявляет требования
# МАШИНОЧИТАЕМО: блок ``` с парами «библиотека: required|not-required```.
# Гейт читает объявление, а не догадывается по словам.
DECL = re.compile(r"^\s*([a-z0-9_]+)\s*:\s*(required|not-required)\s*$", re.I)


def read_declaration(text):
    """{lib: bool} из первого ```-блока, где есть хоть одна пара required."""
    in_block = False
    decl = {}
    for ln in text.splitlines():
        if ln.strip().startswith("```"):
            in_block = not in_block
            continue
        if not in_block:
            continue
        m = DECL.match(ln)
        if m:
            decl[m.group(1).lower()] = m.group(2).lower() == "required"
    return decl


def main(argv):
    if len(argv) != 2:
        print("usage: deps_install_check.py <package.zip>", file=sys.stderr)
        return 1
    zip_path = argv[1]
    if not os.path.isfile(zip_path):
        print("ПАКЕТ НЕ НАЙДЕН: %s" % zip_path)
        return 1
    if not os.path.isfile(DOC):
        print("ДОКУМЕНТ НЕ НАЙДЕН: %s" % DOC)
        return 1

    deps = read_mods_toml(zip_path)
    if deps is None:
        print("В ПАКЕТЕ НЕТ mods.toml — требования к установке не проверить")
        return 1
    text = open(DOC, encoding="utf-8").read()
    decl = read_declaration(text)
    if not decl:
        print("В ДОКУМЕНТЕ НЕТ МАШИНОЧИТАЕМОГО БЛОКА требований — сверять нечего")
        return 1

    fail = []
    print("Требования к установке против mods.toml")
    print("  пакет:    %s" % os.path.basename(zip_path))
    print("  документ: %s" % os.path.basename(DOC))
    print()
    print("  %-14s %-10s %-10s %s" % ("мод", "в пакете", "в док.", "итог"))
    for lib in WATCHED:
        in_pkg = deps.get(lib)
        mandatory = in_pkg is True
        mentioned = lib in decl
        required = decl.get(lib, False)
        if mandatory and not mentioned:
            ok, why = False, "обязателен в пакете, в документе не упомянут"
        elif mandatory and not required:
            ok, why = False, "обязателен в пакете, документ считает необязательным"
        elif not mandatory and mentioned and required:
            ok, why = False, "в пакете не обязателен, документ требует"
        elif in_pkg is None and required:
            ok, why = False, "в пакете нет, а документ требует"
        elif in_pkg is None and not mentioned:
            ok, why = False, "в пакете нет и в документе не объявлена"
        else:
            ok, why = True, "сходится"
        if not ok:
            fail.append("%s: %s" % (lib, why))
        mark = "✓" if ok else "✗"
        print("  %s %-12s %-10s %-10s %s"
              % (mark, lib,
                 "нет" if in_pkg is None else ("обяз." if mandatory else "мягко"),
                 "требует" if required else ("упомянут" if mentioned else "—"),
                 why))
    print()
    if fail:
        print("ИТОГ: РАСХОЖДЕНИЙ %d" % len(fail))
        for f in fail:
            print("  ✗ %s" % f)
        return 2
    print("ИТОГ: СХОДИТСЯ — документ описывает ровно те зависимости, что в пакете")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
