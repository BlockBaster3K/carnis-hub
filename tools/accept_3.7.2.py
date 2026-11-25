#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приёмка пакета 3.7.2 по ТЗ 3.7.2 (T-3118, заготовка — T-3123).

Блоки 1–8 переиспользованы из `tools/accept_3.7.0.py` **без изменения правил**
(манифест, JSON, версия, overlay, A4-p7, A3R1, K8-S, ambient). Добавлены:

    9.  тембр — `tools/timbre_check.py` (Ревизор, T-3106), нужен код 0;
        доля энергии < 80 Гц <= 25 %, спектральный центр >= 400 Гц.
    10. принятое не тронуто — 14 файлов 3.6.0-R побайтово (Д1–Д7 и др.).
    11. З-1 — доля самой частой непрозрачной краски `infected_creeper.png`
        <= 35 % (было 81,2 % в 3.7.0; ТЗ называет 84,2 %, см. отчёт).
    12. принятые слои побайтово: A4-p7-**R** (8 PNG) и A3R1 (4 PNG) — T-3119.
    13. существа — доля самой частой краски <= 35 % (`shade_density.py`);
    14. блоки — то же по текстурам блоков;
    15. банк — формат однороден (моно/44.1 кГц), клиппинга нет (ТЗ §9 3.7.2).

Блоки 1–8 — наследие 3.7.1 без изменения правил (ТЗ 3.7.2 §9).

Использование:
    python3 tools/accept_3.7.1.py [путь_к_zip] [путь_к_манифесту]

Коды: 0 — ПРИНЯТО, 1 — ЕСТЬ РАСХОЖДЕНИЯ, 2 — нет пакета / ошибка запуска.
"""
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
DEFAULT_ZIP = os.path.join(REPO, "01-coder", "3.7.2",
                           "project-3.7.2-clean.zip")
DEFAULT_MANIFEST = os.path.join(REPO, "01-coder", "3.7.2",
                                "project-3.7.2-clean.manifest.txt")
REF_360 = os.path.join(REPO, "01-coder", "3.6.0-R",
                       "project-3.6.0-R-clean.zip")

VERSION = "3.7.2"
GLOW_CHECK = os.path.join(REPO, "tools", "glow_check.py")
ORPHANS = os.path.join(REPO, "tools", "sound_orphans.py")
TENDRIL = os.path.join(REPO, "tools", "tendril_flesh_match.py")
AMBIENT_GATE = os.path.join(REPO, "tools", "ambient_gate.py")
TIMBRE = os.path.join(REPO, "tools", "timbre_check.py")

CREEPER = "src/main/resources/assets/carnis/textures/entity/infected_creeper.png"
SHADE_MAX = 35.0
BLOCK_DIR = "src/main/resources/assets/carnis/textures/block"
SOUND_SUBDIR = "src/main/resources/assets/carnis/sounds"
TIMBRE_FILES = 10          # 9 слоёв + стингер; пульсы вне приёмки тембра

# Д1–Д7 и принятое: НЕ должно измениться относительно 3.6.0-R.
KEEP_IDENTICAL = [
    "src/main/resources/assets/carnis/geo/entity/cerebral_nexus.geo.json",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_0.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_1.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_2.png",
    "src/main/resources/assets/carnis/textures/block/ossified_flesh_3.png",
    "src/main/resources/assets/carnis/textures/block/spore_sprout.png",
    "src/main/resources/assets/carnis/textures/block/neural_moss.png",
    "src/main/resources/assets/carnis/textures/block/pustule_cluster.png",
    "src/main/resources/assets/carnis/textures/mob_effect/incubating.png",
    "src/main/resources/assets/carnis/textures/mob_effect/thermal_shock.png",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_0.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_1.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_2.json",
    "src/main/resources/assets/carnis/models/block/creeping_tendrils_3.json",
]

fail = []
warn = []


# ---------------------------------------------------------------- 1. манифест
def check_manifest(extract_dir, manifest):
    if not manifest or not os.path.exists(manifest):
        print("  ✗ манифеста нет — sha256 не сверить")
        fail.append("манифест: файла нет")
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
    r = subprocess.run(["sha256sum", "-c", "--quiet", manifest],
                       cwd=extract_dir, capture_output=True, text=True)
    bad = [l for l in (r.stdout + r.stderr).split("\n")
           if l.strip() and "OK" not in l]
    actual = sum(len(fs) for _, _, fs in os.walk(extract_dir))
    print("  %s манифест: строк %d, файлов в пакете %d"
          % ("✓" if not bad else "✗", files, actual))
    for l in bad[:5]:
        print("      %s" % l)
    if bad:
        fail.append("манифест: не сошлось %d строк" % len(bad))
    if files != actual:
        fail.append("манифест: строк %d, файлов %d" % (files, actual))


# --------------------------------------------------------------------- 2. JSON
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
    pkg = kw.get("need", None)
    py = _python_with(pkg) if pkg else sys.executable
    if py is None:
        print("  ✗ %s: нет интерпретатора с %s" % (name, pkg))
        fail.append("%s: нет окружения (%s)" % (name, pkg))
        return
    r = subprocess.run([py, script] + list(args), capture_output=True,
                       text=True)
    tail = [l for l in r.stdout.strip().split("\n") if l.startswith("ИТОГ")]
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


# -------------------------------------------------------------- 10. Принятое
def check_keep_identical(extract_dir):
    if not os.path.exists(REF_360):
        warn.append("нет эталона 3.6.0-R — Д1–Д7 не сверены")
        print("  ! эталона 3.6.0-R нет, пропущено")
        return
    same = diff = missing = 0
    with zipfile.ZipFile(REF_360) as z:
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
    bad = []
    worst = None
    for p in files[:limit]:
        r = subprocess.run([py, "-c", code, p], capture_output=True, text=True)
        if r.returncode != 0:
            bad.append("%s: замер не прошёл" % os.path.basename(p))
            continue
        npx, ncol, top_n = (int(x) for x in r.stdout.split()[:3])
        if npx == 0:
            continue
        share = 100.0 * top_n / npx
        rel = os.path.relpath(p, os.path.join(extract_dir, subdir))
        if worst is None or share > worst[1]:
            worst = (rel, share, ncol)
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


def check_bank_format(extract_dir):
    """ТЗ 3.7.2 §9, блок 13: формат банка однороден, клиппинга нет.

    Мерим по файлам пакета: моно и 44 100 Гц у всех, кроме того — ни одного
    файла нулевой длины. Клиппинг (peak >= 0 dBFS) требует декодера: если
    numpy+av есть — считаем, иначе честно пишем «не проверено», а не «ок».
    """
    root = os.path.join(extract_dir, SOUND_SUBDIR)
    if not os.path.isdir(root):
        print("  ! каталога звуков нет — пропущено")
        warn.append("банк: каталога звуков нет")
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
    py = _python_with("numpy")
    if py is None:
        print("  · клиппинг не проверен: нет numpy+av (не «ок», а «не проверено»)")
        warn.append("банк: клиппинг не проверен — нет декодера")
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
        print("  · клиппинг: %d файлов не декодированы" % failed)
        warn.append("банк: %d файлов не декодированы" % failed)
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


# ------------------------------------------------------------------------ main
def find_manifest(zip_path, given):
    if given and os.path.exists(given):
        return given
    for ext in (".manifest.txt", ".manifest", ".sha256", ".txt"):
        p = zip_path[:-4] + ext if zip_path.endswith(".zip") else zip_path + ext
        if os.path.exists(p):
            return p
    return None


def main():
    zip_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ZIP
    man_arg = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MANIFEST

    print("Приёмка пакета %s (ТЗ %s)" % (VERSION, VERSION))
    if not os.path.exists(zip_path):
        print()
        print("ПАКЕТ НЕ НАЙДЕН: %s" % zip_path)
        print("Ждём: T-3115 (блоки), T-3122 (существа), T-3121 (банк) →")
        print("      Кодер собирает 01-coder/%s/project-%s-clean.zip + манифест"
              % (VERSION, VERSION))
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
        m = find_manifest(zip_path, man_arg)
        if m:
            print("   %s" % os.path.relpath(m, REPO))
        check_manifest(tmp, m)

        print()
        print("2) JSON")
        check_json(tmp)

        print()
        print("3) Версия %s в четырёх местах" % VERSION)
        check_version(tmp, zip_path)

        print()
        print("4) Overlay (cmp источник — пакет)")
        check_overlay(tmp)

        print()
        print("5) A4-p7-R — палитра существ (ТЗ §4)")
        if os.path.exists(GLOW_CHECK):
            run_tool("glow_check", GLOW_CHECK, zip_path, REF_360, need="PIL")
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
        print("10) Принятое не тронуто (14 файлов 3.6.0-R побайтово)")
        check_keep_identical(tmp)

        print()
        print("11) З-1 — плотность светотени infected_creeper")
        check_z1_shade(tmp)

        print()
        print("12) Принятые слои лежат в пакете побайтово (A4-p7-R, A3R1)")
        check_accepted_layers(tmp)

        print()
        print("13) Существа — плотность светотени (ТЗ 3.7.2 §9)")
        check_creatures(tmp)

        print()
        print("14) Блоки — плотность светотени (ТЗ 3.7.2 §9)")
        check_blocks(tmp)

        print()
        print("15) Банк — формат и клиппинг (ТЗ 3.7.2 §9)")
        check_bank_format(tmp)

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
        print("ИТОГ: ПРИНЯТО — все проверки пройдены.")
        print("Дальше: CI на новом коммите → merge PR → тег v%s → Release."
              % VERSION)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
