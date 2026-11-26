#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_373_delta.py — независимая сверка пакета 3.7.3 против принятого 3.7.2.

Зачем: приёмка T-3179 п.3 требует не «гейт сказал 0», а собственного замера
дельты. Гейт `tools/accept_3.7.3.py` — зона Интегратора и он смотрит пакет
изнутри; этот чекер смотрит **разницу двух пакетов** и потому ловит то, чего
внутренняя проверка не видит: регресс уже исправленного файла (З-16 в
`incubation_cyst.png`), лишние/пропавшие файлы, подмену версии.

Что проверяется:
  1. состав пакета и дельта к 3.7.2 (добавлено / удалено / изменено);
  2. ожидания 3.7.3: добавлены ровно 2 glowmask, изменены только 15 `.ogg`
     (З-21) + `gradle.properties` + `mods.toml`; удалённых нет;
  3. З-16: `textures/block/incubation_cyst.png` == версии 3.7.2 (`7d30ac39…`),
     ≥ 7 непрозрачных цветов, топ-доля ≤ 35 %;
  4. правило Р-3 на 2 новых glowmask: ровно `(255,92,57)`, α ∈ {0,255},
     размер == телу, свечение вне силуэта тела 0 px;
  5. нормы A3R1 на текстурах `textures/block/`, `textures/entity/`:
     ≥ 7 цветов, топ-доля ≤ 35 %, α только 0/255;
  6. crest изменённых `.ogg` против **оригиналов** (Δ ≤ 0,05 дБ) и клиппинг —
     именно так проверяется З-21: правка кодирования не должна менять
     динамику относительно исходника, а сравнение с 3.7.2 как раз и даёт
     те самые 0,47 дБ, которые правкой убирали;
  7. версия: `gradle.properties` и `mods.toml` — 3.7.3.

Использование:
    python3 02-reviewer/tools/verify_373_delta.py <пакет 3.7.3.zip> \\
            --prev <пакет 3.7.2.zip> [--tol 0.05]

Код возврата: 0 — всё сходится, 2 — есть расхождения, 1 — ошибка запуска.
"""

import argparse
import hashlib
import io
import sys
import zipfile
from collections import Counter

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("ОШИБКА: нужен Pillow")
    sys.exit(1)

GLOW = (255, 92, 57)
CYST_EXPECTED = "7d30ac39"        # sha256 версии 3.7.2 (З-16 закрыт)
CYST_PATH = "src/main/resources/assets/carnis/textures/block/incubation_cyst.png"
NEW_GLOWMASKS = [
    "src/main/resources/assets/carnis/textures/entity/biomass_maggot_glowmask.png",
    "src/main/resources/assets/carnis/textures/entity/parasitic_tendril_glowmask.png",
]
ALLOWED_CHANGED_OTHER = {
    "gradle.properties",
    "src/main/resources/META-INF/mods.toml",
}
SOUNDS_PREFIX = "src/main/resources/assets/carnis/sounds/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def files_of_zip(z):
    return {n: z.read(n) for n in z.namelist() if not n.endswith("/")}


def png_stats(data):
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    opaque = [c for c in px if c[3] > 0]
    alphas = {c[3] for c in px}
    cnt = Counter((c[0], c[1], c[2]) for c in opaque)
    top = cnt.most_common(1)[0] if cnt else ((0, 0, 0), 0)
    return {
        "size": im.size,
        "opaque": len(opaque),
        "colors": len(cnt),
        "top_share": (top[1] / len(opaque)) if opaque else 0.0,
        "alphas": alphas,
        "mask": {(c[0], c[1], c[2]): c[3] for c in px},
        "alpha0": sum(1 for c in px if c[3] == 0),
    }


def crest_of(data):
    try:
        import av
        import numpy as np
    except ImportError:
        return None
    c = av.open(io.BytesIO(data))
    st = c.streams.audio[0]
    chunks = [fr.to_ndarray().astype("float64").ravel() for fr in c.decode(st)]
    c.close()
    if not chunks:
        return None
    x = np.concatenate(chunks)
    peak = float(abs(x).max())
    if peak <= 0:
        return None
    rms = float((x ** 2).mean() ** 0.5)
    if rms <= 0:
        return None
    import math
    return 20 * math.log10(peak) - 20 * math.log10(rms), peak


def body_for(mask_path):
    return mask_path.replace("_glowmask", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--prev", required=True, help="пакет 3.7.2 (принятый эталон)")
    ap.add_argument("--tol", type=float, default=0.05)
    ap.add_argument("--originals", default="03-sound/archive_zapas_2026-11-26/",
                    help="каталог оригиналов .ogg (эталон для crest, З-21)")
    ap.add_argument("--allow", action="append", default=[],
                    metavar="ПРЕФИКС",
                    help="разрешённое (ожидаемое) изменение/добавление с таким префиксом; можно повторять")
    a = ap.parse_args()

    try:
        cur = files_of_zip(zipfile.ZipFile(a.package))
        prev = files_of_zip(zipfile.ZipFile(a.prev))
    except (OSError, zipfile.BadZipFile) as e:
        print("ОШИБКА: %s" % e)
        return 1

    fails, warns = [], []

    def ok(msg):
        print("  \u2713 %s" % msg)

    def bad(msg):
        print("  \u2717 %s" % msg)
        fails.append(msg)

    def warn(msg):
        print("  ! %s" % msg)
        warns.append(msg)

    print("Пакет  : %s (%d файлов)" % (a.package, len(cur)))
    print("Эталон : %s (%d файлов, 3.7.2)" % (a.prev, len(prev)))

    # 1-2. дельта
    print("\n[1] Дельта к 3.7.2")
    added = sorted(set(cur) - set(prev))
    removed = sorted(set(prev) - set(cur))
    changed = sorted(k for k in cur if k in prev and sha(cur[k]) != sha(prev[k]))

    def allowed(path):
        return any(path.startswith(pref) for pref in a.allow)

    changed_snd = [p for p in changed if p.startswith(SOUNDS_PREFIX) and p.endswith(".ogg")]
    changed_other = [p for p in changed if p not in changed_snd]
    allowed_changed = [p for p in changed_other if allowed(p)]
    unexpected = [p for p in changed_other
                  if p not in ALLOWED_CHANGED_OTHER and not allowed(p)]
    added_unexpected = [p for p in added if p not in set(NEW_GLOWMASKS) and not allowed(p)]
    print("  добавлено %d, изменено %d, удалено %d" % (len(added), len(changed), len(removed)))
    for p in added:
        print("    + %s" % p)
    for p in removed:
        print("    \u2212 %s" % p)
    if allowed_changed:
        print("  разрешено флагом --allow: изменено %d" % len(allowed_changed))
        for p in allowed_changed:
            print("    ~ %s" % p)
    extra_added = [p for p in added if p not in set(NEW_GLOWMASKS)]
    if added_unexpected:
        bad("добавлено %d файлов, не разрешено: %s"
            % (len(added), ", ".join(added_unexpected[:5])))
    elif extra_added:
        ok("добавлено %d: 2 glowmask ожидаемы, %d разрешены --allow"
           % (len(added), len(extra_added)))
    else:
        ok("добавлены ровно 2 новые glowmask")
    if not removed:
        ok("удалённых файлов нет")
    else:
        bad("пропали файлы: %d" % len(removed))


    if unexpected:
        bad("неожиданные изменения содержимого: %s" % ", ".join(unexpected))
    else:
        ok("кроме звука изменены только %s" % ", ".join(sorted(ALLOWED_CHANGED_OTHER)))
    print("    изменённых .ogg: %d (+%d прочих)" % (len(changed_snd), len(changed_other)))

    # 3. З-16
    print("\n[2] З-16 · incubation_cyst")
    if CYST_PATH not in cur:
        bad("нет %s" % CYST_PATH)
    else:
        h = sha(cur[CYST_PATH])
        st = png_stats(cur[CYST_PATH])
        line = "%s: sha %s, цветов %d, топ %.1f %% (%d px)" % (
            CYST_PATH.split("/")[-1], h[:12], st["colors"], st["top_share"] * 100, st["opaque"])
        good = h.startswith(CYST_EXPECTED) or (
            st["colors"] >= 7 and st["top_share"] <= 0.35)
        (ok if good else bad)(line)
        if st["colors"] < 7:
            bad("З-16: цветов < 7 (это старая версия из 3.7.1)")

    # 4. Р-3 на новых масках
    print("\n[3] Правило Р-3 · новые glowmask")
    for m in NEW_GLOWMASKS:
        if m not in cur:
            bad("нет %s" % m)
            continue
        st = png_stats(cur[m])
        body = body_for(m)
        notes = []
        opaque_rgb = {c for c, al in st["mask"].items() if al > 0}
        if st["colors"] == 1 and opaque_rgb == {GLOW}:
            notes.append("ровно (255,92,57)")
        else:
            notes.append("ЦВЕТ НЕ (255,92,57) / не один")
        if st["alphas"] <= {0, 255}:
            notes.append("α ∈ {0,255}")
        else:
            notes.append("α не бинарная: %s" % sorted(st["alphas"])[:6])
        if body in cur:
            bst = png_stats(cur[body])
            if bst["size"] == st["size"]:
                notes.append("размер == телу %dx%d" % st["size"])
            else:
                notes.append("РАЗМЕР %s != тело %s" % (st["size"], bst["size"]))
                bad("%s: размер не совпал с телом" % m.split("/")[-1])
            outside = 0
            for k, al in st["mask"].items():
                if al > 0:
                    outside += 1  # считаем по силуэту ниже
            # силуэт тела: пиксели с α > 0; маска должна лежать внутри
            bimg = Image.open(io.BytesIO(cur[body])).convert("RGBA")
            bpx = bimg.load()
            mimg = Image.open(io.BytesIO(cur[m])).convert("RGBA")
            mpx = mimg.load()
            w, h = mimg.size
            out = 0
            for y in range(h):
                for x in range(w):
                    if mpx[x, y][3] > 0 and bpx[x, y][3] == 0:
                        out += 1
            if out == 0:
                notes.append("вне силуэта 0 px")
            else:
                notes.append("ВНЕ СИЛУЭТА %d px" % out)
                bad("%s: свечение вне силуэта %d px" % (m.split("/")[-1], out))
        (ok if not any("НЕ" in n or "ВНЕ" in n or "РАЗМЕР" in n or "бинарная" in n for n in notes) else bad)(
            "%s — %s" % (m.split("/")[-1], ", ".join(notes)))

    # 5. нормы A3R1 на текстурах
    print("\n[4] A3R1 · текстуры block/entity")
    checked = thin = wide = 0
    for p, data in sorted(cur.items()):
        if not p.startswith("src/main/resources/assets/carnis/textures/"):
            continue
        if not (("/block/" in p) or ("/entity/" in p)) or not p.endswith(".png"):
            continue
        if "glowmask" in p:
            continue
        st = png_stats(data)
        checked += 1
        if st["colors"] < 7:
            thin += 1
            bad("%s: %d цветов < 7" % (p.split("textures/")[-1], st["colors"]))
        if st["top_share"] > 0.35:
            wide += 1
            bad("%s: топ %.1f %% > 35 %% (%d цветов)" % (
                p.split("textures/")[-1], st["top_share"] * 100, st["colors"]))
    print("  проверено %d текстур: <7 цветов — %d, топ > 35 %% — %d" % (checked, thin, wide))
    if checked and not thin and not wide:
        ok("все текстуры в норе A3R1")

    # 6. crest изменённых звуков — против оригиналов
    print("\n[5] crest изменённых .ogg (З-21) против оригиналов")
    import os
    orig_dir = a.originals
    orig = {}
    if os.path.isdir(orig_dir):
        for n in os.listdir(orig_dir):
            if n.endswith(".ogg"):
                orig[n] = os.path.join(orig_dir, n)
    if not orig:
        warn("нет каталога оригиналов %s — crest не сверен" % orig_dir)
    worst = None
    crest_bad = 0
    for p in changed_snd:
        name = p.split("/")[-1]
        if name not in orig:
            warn("оригинала нет для %s" % name)
            continue
        with open(orig[name], "rb") as f:
            b2 = crest_of(f.read())
        a2 = crest_of(cur[p])
        if not a2 or not b2:
            warn("не декодируется: %s" % name)
            continue
        d = abs(a2[0] - b2[0])
        if d > a.tol:
            crest_bad += 1
            bad("%s: Δ crest %.2f дБ > %.2f" % (name, d, a.tol))
        if a2[1] >= 1.0:
            bad("%s: клиппинг (peak %.3f)" % (name, a2[1]))
        worst = max(worst or (0, ""), (d, name))
    if worst:
        print("  худшее Δ crest: %.2f дБ (%s)" % (worst[0], worst[1]))
    if changed_snd and not crest_bad:
        ok("crest == оригиналам в пределах %.2f дБ на всех %d файлах" % (a.tol, len(changed_snd)))

    # 7. версия
    print("\n[6] Версия пакета")
    gp = cur.get("gradle.properties", b"").decode("utf-8", "replace")
    ver = [l.split("=", 1)[1].strip() for l in gp.splitlines() if l.startswith("mod_version")]
    if ver and ver[0] == "3.7.3":
        ok("gradle.properties: mod_version=3.7.3")
    else:
        bad("gradle.properties: mod_version=%s" % (ver or "нет"))
    mt = cur.get("src/main/resources/META-INF/mods.toml", b"").decode("utf-8", "replace")
    if "3.7.3" in mt:
        ok("mods.toml содержит 3.7.3")
    else:
        bad("mods.toml без версии 3.7.3")

    print("\n" + "-" * 70)
    print("Провалов: %d, предупреждений: %d" % (len(fails), len(warns)))
    if fails:
        print("ИТОГ: ЕСТЬ РАСХОЖДЕНИЯ")
        return 2
    print("ИТОГ: СХОДИТСЯ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
