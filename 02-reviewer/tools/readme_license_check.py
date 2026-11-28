#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""readme_license_check.py — проверка R23 для приёмки 3.8.0 (шесть пунктов).

Зачем: приёмка 3.8.0 включает R23 пп.1–6 (README в пакете; шесть имён
зависимостей; CC-BY-NC-SA-3.0 отдельно от MIT; фраза «работает без
необязательных»; `mandatory=true` только GeckoLib; `LICENSE` MIT в пакете),
но `tools/accept_3.8.0.py` этих проверок **не содержит вообще**. Пока блока нет
в гейте, эти шесть пунктов проверяются руками — то есть не проверяются.
Этот чекер закрывает разрыв и годится на роль блока гейта.

Дополнительно (R23, вторая часть — «GPL-код не попал в JAR»): ищет файлы
с заголовком GPL/GNU General Public License и сторонние `.jar` в пакете.

Использование:
    python3 02-reviewer/tools/readme_license_check.py <zip|каталог>

Код возврата: 0 — все шесть пунктов выполнены; 2 — есть провалы; 1 — ошибка.
"""

import os
import re
import sys
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

# Пункт 2: шесть имён. Алиасы — как их реально пишут в README.
DEPS = [
    ("Curios", r"curios"),
    ("Patchouli", r"patchouli"),
    ("GeckoLib", r"geckolib"),
    ("SmartBrainLib (SBL)", r"smartbrainlib|\bSBL\b"),
    ("Lodestone", r"lodestone"),
    ("Sound Physics Remastered", r"sound\s*physics"),
]

CC = "CC-BY-NC-SA-3.0"
CC_RX = re.compile(r"cc[-\s]?by[-\s]?nc[-\s]?sa[-\s]?(?:3\.0|v?3)", re.I)
MIT_RX = re.compile(r"\bMIT\b")
ASSET_CONTEXT = re.compile(r"лор|иллюстрац|ассет|asset|арт|art\b|журнал|texture|модел", re.I)
OPTIONAL_RX = re.compile(r"без\s+(?:них|него|необязательн\w*|всех|этих|них\s+необязательн)", re.I)
OPTIONAL_RX2 = re.compile(r"необязательн\w*|опциональн\w*", re.I)


def read_text(z, name):
    try:
        return z.read(name).decode("utf-8", "replace")
    except (KeyError, OSError):
        return ""


def load(src):
    """Вернуть (dict путь->текст для мелких текстовых, список имён, mods.toml)."""
    texts, names, mods = {}, [], None
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            names = z.namelist()
            for n in names:
                low = n.lower()
                if low.endswith("mods.toml"):
                    mods = read_text(z, n)
                if low.endswith(("readme.md", "readme.txt", "license", "license.txt",
                                 "license.md", ".java", ".kt", ".gradle",
                                 ".properties", ".toml", ".json", ".cfg")):
                    if z.getinfo(n).file_size <= 400_000:
                        texts[n] = read_text(z, n)
    else:
        for dp, _, fs in os.walk(src):
            for f in fs:
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, src).replace(os.sep, "/")
                names.append(rel)
                low = f.lower()
                if low == "mods.toml":
                    mods = open(full, encoding="utf-8", errors="replace").read()
                if low.endswith(("readme.md", "readme.txt", "license", "license.txt",
                                 "license.md", ".java", ".kt", ".gradle",
                                 ".properties", ".toml", ".json", ".cfg")):
                    if os.path.getsize(full) <= 400_000:
                        texts[rel] = open(full, encoding="utf-8",
                                          errors="replace").read()
    return texts, names, mods


def find(texts, *pats):
    for path, body in texts.items():
        if any(re.search(p, os.path.basename(path), re.I) for p in pats):
            return path, body
    return None, None


def check_mandatory(mods):
    """mandatory=true разрешён только для GeckoLib. Вернуть (ok, [плохие])."""
    if not mods:
        return None, []
    bad = []
    blocks = re.split(r"(?=\[\[dependencies)", mods)
    for b in blocks:
        if "mandatory" not in b:
            continue
        head = b.split("\n", 1)[0]
        if not re.search(r"mandatory\s*=\s*true", b):
            continue
        if re.search(r'modId\s*=\s*"(?:geckolib|forge|minecraft|javafml|lowcodefml)"',
                     b, re.I):
            continue
        bad.append(head.strip().strip("[]") or "(без имени)")
    return (len(bad) == 0), bad


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    if not (zipfile.is_zipfile(src) or os.path.isdir(src)):
        print("ОШИБКА: нет такого каталога или zip: %s" % src)
        return 1

    texts, names, mods = load(src)
    print("R23 — README и лицензии (шесть пунктов приёмки 3.8.0)")
    print("Пакет: %s (%d файлов)" % (src, len(names)))
    fails = []

    # 1. README в пакете
    rpath, readme = find(texts, r"^readme")
    if rpath:
        print("  ✓ 1. README в пакете: %s (%d символов)" % (rpath, len(readme)))
    else:
        print("  ✗ 1. README в пакете — НЕТ")
        fails.append("README отсутствует в пакете")
        readme = ""

    # 2. шесть имён зависимостей
    missing = [n for n, rx in DEPS if readme and not re.search(rx, readme, re.I)]
    if readme and not missing:
        print("  ✓ 2. шесть зависимостей названы: %s"
              % ", ".join(n for n, _ in DEPS))
    else:
        print("  ✗ 2. не названы в README: %s"
              % (", ".join(missing) if readme else "(README нет)"))
        fails.append("README: нет имён зависимостей %s" % ", ".join(missing))

    # 3. CC-BY-NC-SA-3.0 отдельно от MIT
    has_cc = bool(readme and CC_RX.search(readme))
    has_mit = bool(readme and MIT_RX.search(readme))
    ctx = False
    if has_cc:
        for m in CC_RX.finditer(readme):
            w = readme[max(0, m.start() - 300):m.end() + 300]
            if ASSET_CONTEXT.search(w):
                ctx = True
                break
    if has_cc and has_mit and ctx:
        print("  ✓ 3. %s указана отдельно от MIT (и привязана к ассетам/лору)" % CC)
    else:
        why = []
        if not has_cc:
            why.append("нет %s" % CC)
        if not has_mit:
            why.append("нет MIT")
        if has_cc and not ctx:
            why.append("%s не привязана к лору/иллюстрациям" % CC)
        print("  ✗ 3. лицензии: %s" % "; ".join(why))
        fails.append("лицензии: " + "; ".join(why))

    # 4. «работает без необязательных»
    ok4 = bool(readme and OPTIONAL_RX.search(readme)
               and OPTIONAL_RX2.search(readme))
    if ok4:
        print("  ✓ 4. фраза «работает без необязательных» есть")
    else:
        print("  ✗ 4. нет фразы про работу без необязательных зависимостей")
        fails.append("README: нет фразы «работает без необязательных»")

    # 5. mandatory=true только GeckoLib
    ok5, bad = check_mandatory(mods)
    if ok5 is None:
        print("  ✗ 5. mods.toml не найден — мягкость зависимостей не проверить")
        fails.append("mods.toml отсутствует")
    elif ok5:
        print("  ✓ 5. mandatory=true только у GeckoLib")
    else:
        print("  ✗ 5. mandatory=true не только у GeckoLib: %s" % "; ".join(bad))
        fails.append("mandatory=true у: " + "; ".join(bad))

    # 6. LICENSE MIT в пакете
    lpath, lic = find(texts, r"^license")
    mit_text = bool(lic and (re.search(r"MIT License", lic, re.I)
                             or re.search(r"Permission is hereby granted", lic)))
    if mit_text:
        print("  ✓ 6. LICENSE MIT в пакете: %s" % lpath)
    else:
        print("  ✗ 6. LICENSE с текстом MIT в пакете — %s"
              % ("нет файла" if not lpath else "текст не MIT"))
        fails.append("LICENSE MIT отсутствует")

    # 7. R23 (вторая часть): GPL-код не попал в пакет
    gpl = []
    jars = [n for n in names if n.lower().endswith(".jar")]
    for n, body in texts.items():
        if n.lower().endswith(("readme.md", "readme.txt")):
            continue  # в README слово GPL встречается как упоминание лицензий
        if re.search(r"GNU General Public License|GNU GPL|GPLv2|GPL-2\.0|GPL-3\.0",
                     body):
            gpl.append(n)
    if not jars and not gpl:
        print("  ✓ 7. GPL-заголовков и сторонних .jar нет")
    else:
        print("  ✗ 7. GPL/сторонние бинарники: jar %d, файлов с GPL %d %s"
              % (len(jars), len(gpl), gpl[:5]))
        fails.append("GPL/сторонние .jar: %s" % (jars[:3] + gpl[:3]))

    # 8. Сторонние лицензии == канон (первоисточник — LICENSE библиотек)
    bad8 = check_third_party_licenses(readme)
    if bad8 is None:
        print("  - 8. сверка лицензий с каноном пропущена (нет README)")
    elif bad8:
        print("  ✗ 8. лицензии расходятся с фактом: %s" % "; ".join(bad8))
        fails.append("лицензии: " + "; ".join(bad8))
    else:
        print("  ✓ 8. сторонние лицензии совпадают с каноном (6 библиотек)")

    print()
    if fails:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — провалов %d" % len(fails))
        return 2
    print("ИТОГ: СХОДИТСЯ — все шесть пунктов R23 выполнены")
    return 0



# Пункт 8 (2026-11-26, найдено Интегратором): лицензии сторонних библиотек
# должны совпадать с фактом, а не «выглядеть правдоподобно». В README 3.8.0
# стояло: Patchouli — MPL-2.0 (факт CC-BY-NC-SA-3.0), SmartBrainLib —
# LGPL-3.0-or-later (факт MPL-2.0), Sound Physics — LGPLv3 (факт GPL-3.0).
# Последнее опаснее всех: строгая копилефт-лицензия была записана в сторону
# ослабления, то есть README разрешал то, чего GPL-3.0 не разрешает.
# Канон ниже сверен с файлами LICENSE самих библиотек (GitHub API, поле
# license.spdx_id), а не с пересказом в досках. Правку канона делает
# Архитектор; чекер лишь требует сходимости README с каноном.
CANON_LICENSES = {
    "GeckoLib": "MIT",
    "Curios": "LGPL-3.0-or-later",
    "Patchouli": "CC-BY-NC-SA-3.0",
    "SmartBrainLib": "MPL-2.0",
    "Lodestone": "LGPL-3.0",
    "Sound Physics": "GPL-3.0",
}

# В README лицензия написана рядом с именем в таблице: «| Patchouli | MPL-2.0 |»
LICENSE_ROW_RX = re.compile(
    r"\|\s*([^|\n]+?)\s*\|\s*([^|\n]*?(?:MIT|LGPL[^|\n]*|MPL[^|\n]*|"
    r"GPL[^|\n]*|CC-BY[^|\n]*))\s*\|")


def check_third_party_licenses(readme):
    """Пункт 8: таблица сторонних лицензий в README == канон."""
    if not readme:
        return None  # README нет — это валит пункт 1, не дублируем
    rows = {}
    for line in readme.split("\n"):
        m = LICENSE_ROW_RX.search(line)
        if not m:
            continue
        name, lic = m.group(1).strip(), m.group(2).strip()
        for key in CANON_LICENSES:
            if key.lower() in name.lower() or (key == "Sound Physics"
                                               and "sound physics" in name.lower()):
                rows[key] = lic
    bad = []
    for key, want in CANON_LICENSES.items():
        got = rows.get(key)
        if got is None:
            bad.append("%s: не указана" % key)
        elif want.split()[0].lower() not in got.lower():
            bad.append("%s: в README «%s», факт «%s»" % (key, got, want))
    return bad


if __name__ == "__main__":
    sys.exit(main())
