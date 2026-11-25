#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/build_3.7.0_assembly.py — исполнение ТЗ T-3103 «шаг в шаг».

ЗАЧЕМ ЭТОТ ФАЙЛ. Кодер стоит на T-3103 с 2026-11-20; это единственный стоп
волны 31. ТЗ в `.workflow/TASK_BOARD.md` расписано по шагам и не оставляет
вариантов — значит его можно исполнить детерминированно. Скрипт делает ровно
шаги 1–6 ТЗ и НИЧЕГО больше:

    1. ambient-фикс в HiveAmbientSoundHandler.java (4 числа);
    2. sounds.json: убрать pitch у 6 ambient-событий, выставить volume
       (кровать 0.45, close 0.25), hive.pulse pitch → 1.0;
    3. скопировать 9 ambient-.ogg из 03-sound/sounds/ побайтово;
    4. вернуть amalgam_breath_01/02 + ссылка с volume 0.35;
    5. версия 3.7.0 в четырёх местах — проверить;
    6. собрать project-3.7.0-clean.zip + .manifest.txt.

Зона: `01-coder/3.7.0/` (ТЗ T-3103, п. «Зона»). Скрипт правит только её.
A4-p7 и A3R1 НЕ вносит — их вносит Кодер из сдач Художника (иное ТЗ, иное
решение). Скрипт идемпотентен: повторный запуск не ломает результат.

Использование:
    python3 tools/build_3.7.0_assembly.py [--dry-run] [--repo=<корень>]

Коды: 0 — сделано, 1 — расхождение/ошибка.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

# Корень репозитория определяется по ЦЕЛЕВОМУ каталогу пакета, а не по месту
# скрипта: иначе запуск из копии дерева правил бы настоящий репозиторий
# (проверено на себе 2026-11-25 — откатил). --repo=<путь> задаёт явно.
_arg_repo = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--repo=")]
if _arg_repo:
    REPO = os.path.abspath(_arg_repo[0])
else:
    _here = os.path.abspath(__file__)
    _guess = None
    # ищем вверх каталог, где есть 01-coder/<версия> и 03-sound/sounds
    d = os.path.dirname(_here)
    for _ in range(6):
        if os.path.isdir(os.path.join(d, "03-sound", "sounds")) and \
                os.path.isdir(os.path.join(d, "01-coder")):
            _guess = d
            break
        d = os.path.dirname(d)
    REPO = _guess if _guess else os.path.dirname(os.path.dirname(_here))
PKG = os.path.join(REPO, "01-coder", "3.7.0")
BANK = os.path.join(REPO, "03-sound", "sounds")
ZIP_OUT = os.path.join(PKG, "project-3.7.0-clean.zip")
MAN_OUT = os.path.join(PKG, "project-3.7.0-clean.manifest.txt")
HANDLER = os.path.join(PKG, "src", "main", "java", "com", "carnis", "mod",
                       "client", "sound", "HiveAmbientSoundHandler.java")
SOUNDS_JSON = os.path.join(PKG, "src", "main", "resources", "assets", "carnis",
                           "sounds.json")
SOUND_DIR = os.path.join(PKG, "src", "main", "resources", "assets", "carnis",
                         "sounds")
VERSION = "3.7.0"

# Шаг 3: девять ambient-слоёв (пути относительно sounds/).
NINE = ["hive/amb_surface", "hive/amb_deep", "hive/amb_core",
        "hive/amb_threshold", "amb/hive_ambient_01", "amb/hive_ambient_02",
        "amb/hive_ambient_03", "amb/hive_ambient_close_01",
        "amb/hive_ambient_close_02"]
# Шаг 4
BREATHS = ["hive/amalgam_breath_01", "hive/amalgam_breath_02"]
AMBIENT_EVENTS = ("hive.ambient", "hive.ambient_close", "hive.ambient_surface",
                  "hive.ambient_deep", "hive.ambient_core",
                  "hive.ambient_threshold")

DRY = "--dry-run" in sys.argv
log = []
errors = []


def say(msg):
    log.append(msg)
    print(msg)


def fail(msg):
    errors.append(msg)
    print("  ✗ " + msg)


# ------------------------------------------------------------------ шаг 1
def step1_handler():
    say("")
    say("ШАГ 1. ambient-фикс в HiveAmbientSoundHandler.java")
    if not os.path.exists(HANDLER):
        fail("нет файла %s" % os.path.relpath(HANDLER, REPO))
        return
    txt = open(HANDLER, encoding="utf-8").read()
    orig = txt

    subs = [
        (r"PULSE_INTERVAL_TICKS = 268;\s*// 13\.4 seconds",
         "PULSE_INTERVAL_TICKS = 450; // 22.5 seconds", "интервал пульса 268→450"),
        (r"targetVolume = 0\.85F \* \(float\)",
         "targetVolume = 0.45F * (float)", "громкость кровати 0.85F→0.45F"),
        (r"Mth\.clamp\(targetVolume, 0\.0F, 0\.85F\)",
         "Mth.clamp(targetVolume, 0.0F, 0.45F)", "кламп 0.85F→0.45F"),
        (r"targetVolume \* 0\.6F",
         "Mth.clamp(targetVolume * 0.55F, 0.0F, 0.25F)",
         "close-слой 0.6F→clamp(0.55F, 0..0.25F)"),
    ]
    for pat, rep, human in subs:
        n = len(re.findall(pat, txt))
        if n:
            txt = re.sub(pat, rep, txt)
            say("  ✓ %s (совпадений %d)" % (human, n))
        else:
            say("  · %s — уже сделано" % human)

    if txt != orig:
        if DRY:
            say("  [dry-run] файл не записан")
        else:
            open(HANDLER, "w", encoding="utf-8").write(txt)
            say("  записан хендлер")

    # самопроверка
    t = open(HANDLER, encoding="utf-8").read()
    m = re.search(r"PULSE_INTERVAL_TICKS\s*=\s*(\d+)", t)
    val = int(m.group(1)) if m else -1
    if not (420 <= val <= 480):
        fail("PULSE_INTERVAL_TICKS = %d, нужно 420–480" % val)
    else:
        say("  ✓ PULSE_INTERVAL_TICKS = %d" % val)
    if "0.85F" in t:
        fail("в файле осталось 0.85F")
    if "0.45F" not in t:
        fail("в файле нет 0.45F")


# ------------------------------------------------------------------ шаг 2
def step2_sounds_json():
    say("")
    say("ШАГ 2. sounds.json — pitch и volume ambient")
    if not os.path.exists(SOUNDS_JSON):
        fail("нет sounds.json")
        return
    d = json.load(open(SOUNDS_JSON, encoding="utf-8"))
    removed = set_vol = 0
    for ev in AMBIENT_EVENTS:
        body = d.get(ev)
        if not body:
            fail("в sounds.json нет события %s" % ev)
            continue
        want = 0.25 if ev == "hive.ambient_close" else 0.45
        for s in body.get("sounds", []):
            if not isinstance(s, dict):
                continue
            if "pitch" in s:
                del s["pitch"]
                removed += 1
            s["volume"] = want
            set_vol += 1
    say("  ✓ убрано pitch: %d" % removed)
    say("  ✓ выставлено volume: %d (кровать 0.45, close 0.25)" % set_vol)

    pulse = d.get("hive.pulse", {})
    n_p = 0
    for s in pulse.get("sounds", []):
        if isinstance(s, dict):
            s["pitch"] = 1.0
            n_p += 1
    say("  ✓ hive.pulse pitch → 1.0 (%d записей)" % n_p)

    if DRY:
        say("  [dry-run] sounds.json не записан")
    else:
        json.dump(d, open(SOUNDS_JSON, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        say("  записан sounds.json")

    chk = json.load(open(SOUNDS_JSON, encoding="utf-8"))
    bad = []
    for ev in AMBIENT_EVENTS:
        for s in chk.get(ev, {}).get("sounds", []):
            if isinstance(s, dict) and s.get("pitch") not in (None, 1.0):
                bad.append("%s: %s" % (ev, s.get("pitch")))
    if bad:
        fail("pitch не 1.0: %s" % "; ".join(bad[:3]))
    else:
        say("  ✓ самопроверка: pitch ambient = 1.0")


# ------------------------------------------------------------------ шаг 3
def step3_copy_nine():
    say("")
    say("ШАГ 3. девять ambient-.ogg из банка — побайтово")
    same = copied = 0
    for rel in NINE:
        src = os.path.join(BANK, rel + ".ogg")
        dst = os.path.join(SOUND_DIR, rel + ".ogg")
        if not os.path.exists(src):
            fail("нет в банке: %s.ogg" % rel)
            continue
        if os.path.exists(dst) and open(src, "rb").read() == open(dst, "rb").read():
            same += 1
            continue
        if DRY:
            say("  [dry-run] скопировал бы %s.ogg" % rel)
            copied += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        copied += 1
        say("  ✓ %s.ogg ← банк (%d Б)" % (rel, os.path.getsize(dst)))
    say("  итог: скопировано %d, уже совпадало %d из %d" % (copied, same, len(NINE)))
    # самопроверка побайтово
    if not DRY:
        bad = 0
        for rel in NINE:
            src = os.path.join(BANK, rel + ".ogg")
            dst = os.path.join(SOUND_DIR, rel + ".ogg")
            if not os.path.exists(dst) or \
                    open(src, "rb").read() != open(dst, "rb").read():
                fail("расхождение после копирования: %s.ogg" % rel)
                bad += 1
        if not bad:
            say("  ✓ самопроверка: 9/9 совпадают с банком")


# ------------------------------------------------------------------ шаг 4
def step4_breaths():
    say("")
    say("ШАГ 4. amalgam_breath_01/02 — вернуть в пакет и в sounds.json")
    for rel in BREATHS:
        src = os.path.join(BANK, rel + ".ogg")
        dst = os.path.join(SOUND_DIR, rel + ".ogg")
        if not os.path.exists(src):
            fail("нет в банке: %s.ogg" % rel)
            continue
        if os.path.exists(dst):
            say("  · %s.ogg уже есть (%d Б)" % (rel, os.path.getsize(dst)))
            continue
        if DRY:
            say("  [dry-run] вернул бы %s.ogg" % rel)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        say("  ✓ вернул %s.ogg (%d Б)" % (rel, os.path.getsize(dst)))

    d = json.load(open(SOUNDS_JSON, encoding="utf-8"))
    body = d.get("hive.amalgam_breath")
    if body is None:
        fail("в sounds.json нет события hive.amalgam_breath")
        return
    names = [s.get("name") if isinstance(s, dict) else s
             for s in body.get("sounds", [])]
    have = any("amalgam_breath" in str(n) for n in names)
    if have:
        say("  · ссылки на amalgam_breath уже есть: %s" % names)
    else:
        say("  · сейчас событие ссылается на: %s" % names)
        say("    (ТЗ Р-31.2: добавить оба файла с volume 0.35)")
        add = [{"name": "carnis:%s" % r, "volume": 0.35, "weight": 1}
               for r in BREATHS]
        # убрать volume 0.25-ссылку на flesh_amalgam_ambient, оставить её? ТЗ
        # говорит «добавить», не «заменить» → добавляем, не удаляя существующую.
        body.setdefault("sounds", []).extend(add)
        if DRY:
            say("  [dry-run] дописал бы 2 ссылки volume 0.35")
        else:
            json.dump(d, open(SOUNDS_JSON, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
            say("  ✓ дописаны 2 ссылки volume 0.35")

    chk = json.load(open(SOUNDS_JSON, encoding="utf-8"))
    ns = [s.get("name") if isinstance(s, dict) else s
          for s in chk.get("hive.amalgam_breath", {}).get("sounds", [])]
    for rel in BREATHS:
        want = "carnis:%s" % rel
        if want not in ns:
            fail("в hive.amalgam_breath нет ссылки %s" % want)
        else:
            say("  ✓ ссылка на месте: %s" % want)


# ------------------------------------------------------------------ шаг 5
def step5_version():
    say("")
    say("ШАГ 5. версия %s в четырёх местах" % VERSION)
    gp = os.path.join(PKG, "gradle.properties")
    vals = {}
    for line in open(gp, encoding="utf-8"):
        if line.startswith("mod_version="):
            vals["gradle.properties"] = line.split("=", 1)[1].strip()
    mt = os.path.join(PKG, "src", "main", "resources", "META-INF", "mods.toml")
    if os.path.exists(mt):
        for line in open(mt, encoding="utf-8"):
            s = line.strip()
            if s.startswith("version=") and "mods.toml version" not in vals:
                vals["mods.toml version"] = s.split("=", 1)[1].strip().strip('"')
            if s.startswith("displayVersion="):
                vals["displayVersion"] = s.split("=", 1)[1].strip().strip('"')
    vals["каталог"] = os.path.basename(PKG)
    ok = 0
    for k, v in vals.items():
        good = v == VERSION
        ok += good
        say("  %s %s = %s" % ("✓" if good else "✗", k, v))
        if not good:
            fail("%s = %s, ожидалось %s" % (k, v, VERSION))
    if ok < 4:
        fail("версия только в %d из 4 мест" % ok)
    else:
        say("  ✓ версия в 4 из 4 мест")


# ------------------------------------------------------------------ шаг 6
def step6_zip():
    say("")
    say("ШАГ 6. сборка ZIP + манифест")
    files = []
    for dp, dns, fs in os.walk(PKG):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for f in fs:
            if f in ("MANIFEST.txt", os.path.basename(ZIP_OUT),
                     os.path.basename(MAN_OUT)):
                continue
            p = os.path.join(dp, f)
            files.append(os.path.relpath(p, PKG).replace(os.sep, "/"))
    files.sort()
    say("  файлов к упаковке: %d" % len(files))
    if DRY:
        say("  [dry-run] ZIP не собираю")
        return
    if os.path.exists(ZIP_OUT):
        os.remove(ZIP_OUT)
    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files:
            z.write(os.path.join(PKG, rel), rel)
    import hashlib
    lines = []
    for rel in files:
        h = hashlib.sha256(open(os.path.join(PKG, rel), "rb").read()).hexdigest()
        lines.append("%s  %s" % (h, rel))
    open(MAN_OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    say("  ✓ %s — %d Б" % (os.path.basename(ZIP_OUT), os.path.getsize(ZIP_OUT)))
    say("  ✓ %s — %d строк" % (os.path.basename(MAN_OUT), len(lines)))

    # самопроверка: sha256sum -c в распакованном дереве
    tmp = os.path.join(REPO, ".tmp_verify_370")
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    with zipfile.ZipFile(ZIP_OUT) as z:
        z.extractall(tmp)
    r = subprocess.run(["sha256sum", "-c", "--quiet", MAN_OUT], cwd=tmp,
                       capture_output=True, text=True)
    bad = [l for l in (r.stdout + r.stderr).split("\n")
           if l.strip() and "OK" not in l]
    shutil.rmtree(tmp)
    if bad:
        fail("манифест не сходится: %d строк" % len(bad))
        for l in bad[:3]:
            say("      " + l)
    else:
        say("  ✓ самопроверка: sha256sum -c по %d файлам" % len(lines))


def main():
    print("Исполнение ТЗ T-3103 (сборка пакета %s)" % VERSION)
    print("Пакет: %s" % os.path.relpath(PKG, REPO))
    if DRY:
        print("РЕЖИМ: --dry-run (ничего не пишется)")
    if not os.path.isdir(PKG):
        print("ОШИБКА: нет каталога %s" % PKG)
        return 1
    step1_handler()
    step2_sounds_json()
    step3_copy_nine()
    step4_breaths()
    step5_version()
    step6_zip()
    print("")
    if errors:
        print("ИТОГ: ОШИБКИ — %d" % len(errors))
        for i, e in enumerate(errors, 1):
            print("  %2d. %s" % (i, e))
        return 1
    print("ИТОГ: СДЕЛАНО — шаги 1–6 ТЗ T-3103 выполнены.")
    print("Дальше (шаг 7 ТЗ): python3 tools/accept_3.7.0.py → нужен код 0.")
    print("ВНИМАНИЕ: A4-p7 и A3R1 этот скрипт НЕ вносит — их вносит Кодер.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
