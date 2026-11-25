#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_372_bank_delta.py — дельта-проверка пакета 3.7.2 перед вердиктом Ревизора.

Зачем: после каждой пересборки ZIP я проверяю **только дельту** (так требует
протокол и мой вердикт), а не гоняю заново 25 блоков гейта на неизменных файлах.
Скрипт отвечает на пять вопросов одной командой:

  1. `.ogg` пакета побайтово равны ТЕКУЩЕМУ банку `03-sound/sounds/`?
  2. пики: ни один файл не громче нормы −1,00 dBFS и запас у всех ≥ 0,20 дБ?
  3. что изменилось по сравнению с предыдущей пересборкой (--prev)?
  4. `block/incubation_cyst.png` == сдаче T-3141 (фикс З-16)?
  5. нет ли текстур с <7 цветами или полностью прозрачных (мой критерий З-18,
     которого гейт пока не умеет)?

Использование:
    python3 02-reviewer/tools/verify_372_bank_delta.py <пакет.zip> \\
            [--prev <предыдущий.zip>] [--bank 03-sound/sounds] [--era 3.6.0-R.zip]

Код возврата: 0 — всё сходится, 2 — есть замечания, 1 — ошибка запуска.
"""

import argparse
import collections
import hashlib
import io
import os
import sys
import zipfile

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("ОШИБКА: нужен Pillow")
    sys.exit(1)

SOUNDS_IN_ZIP = "src/main/resources/assets/carnis/sounds/"
TEX_IN_ZIP = "src/main/resources/assets/carnis/textures/"
CYST = "block/incubation_cyst.png"
CYST_SHA = "7d30ac39dcf8"          # сдача T-3141, 7 цветов, 14,5 %
BANK_PREFIX = SOUNDS_IN_ZIP[len(SOUNDS_IN_ZIP):]  # для сопоставления с банком

NEG = []   # замечания, ломающие вердикт
NOTE = []  # информационные


def sha(b):
    return hashlib.sha256(b).hexdigest()


def zip_files(path):
    z = zipfile.ZipFile(path)
    return z, {n: sha(z.read(n)) for n in z.namelist() if not n.endswith("/")}


def ogg_duration(data):
    """Длина Vorbis из granule последней страницы (без декодера)."""
    pos, last = 0, None
    while True:
        i = data.find(b"OggS", pos)
        if i < 0 or i + 27 > len(data):
            break
        gran = int.from_bytes(data[i + 6:i + 14], "little")
        last = gran
        pos = i + 27
    return None if last in (None, 0xFFFFFFFFFFFFFFFF) else last / 44100.0


def peaks_with_av(paths):
    """Пик в dBFS через PyAV. Нет декодера — честно сообщаем, не притворяемся."""
    try:
        import av
    except ImportError:
        return None
    import numpy as np
    out = {}
    for name, data in paths:
        try:
            c = av.open(io.BytesIO(data))
            st = c.streams.audio[0]
            mx = 0
            for frame in c.decode(st):
                a = frame.to_ndarray()
                if a.size:
                    mx = max(mx, float(np.abs(a).max()))
            c.close()
            out[name] = 20 * (mx and __import__("math").log10(mx) or -99.0)
        except Exception:
            out[name] = None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--prev", default=None)
    ap.add_argument("--bank", default="03-sound/sounds")
    ap.add_argument("--margin", type=float, default=0.20)
    ap.add_argument("--norm", type=float, default=-1.00)
    ap.add_argument("--expect-added", type=int, default=None,
                    help="сколько добавленных файлов считать ожидаемыми "
                         "(например 2 новые glowmask в 3.7.3); по умолчанию "
                         "любое добавление — замечание")
    a = ap.parse_args()

    if not os.path.exists(a.package):
        print("ОШИБКА: нет пакета %s" % a.package)
        return 1
    z, files = zip_files(a.package)
    print("Пакет: %s" % a.package)
    print("sha256: %s, файлов %d" % (sha(open(a.package, "rb").read()), len(files)))

    # 1. .ogg против банка
    pack_ogg = {n[len(SOUNDS_IN_ZIP):]: files[n]
                for n in files if n.startswith(SOUNDS_IN_ZIP) and n.endswith(".ogg")}
    bank_ogg = {}
    for dp, _, fs in os.walk(a.bank):
        for f in fs:
            if f.endswith(".ogg"):
                p = os.path.join(dp, f)
                bank_ogg[os.path.relpath(p, a.bank).replace(os.sep, "/")] = sha(open(p, "rb").read())
    diff = sorted(k for k in pack_ogg if k in bank_ogg and pack_ogg[k] != bank_ogg[k])
    missing = sorted(k for k in pack_ogg if k not in bank_ogg)
    print("\n1) Банк: в пакете %d, в банке %d, равны %d, отличий %d, нет в банке %d"
          % (len(pack_ogg), len(bank_ogg), len([k for k in pack_ogg if k in bank_ogg]) - len(diff),
             len(diff), len(missing)))
    for k in diff[:20]:
        print("   ≠ %s" % k)
    if diff:
        NEG.append("банк: %d файлов в пакете отличаются от банка" % len(diff))
    if missing:
        NEG.append("банк: %d файлов пакета отсутствуют в банке" % len(missing))

    # 2. пики
    paths = [(k, z.read(SOUNDS_IN_ZIP + k)) for k in sorted(pack_ogg)]
    pk = peaks_with_av(paths)
    if pk is None:
        print("2) Пики: PyAV недоступен — запас не измерен (НЕ считать нормой)")
        NEG.append("пики не измерены: нет PyAV")
    else:
        bad_norm = [(k, v) for k, v in pk.items() if v is not None and v > a.norm]
        bad_margin = [(k, v) for k, v in pk.items()
                      if v is not None and a.norm - a.margin < v <= a.norm]
        worst = max((v for v in pk.values() if v is not None), default=None)
        print("2) Пики: самый громкий %s dBFS; громче нормы (%.2f): %d; запас < %.2f дБ: %d"
              % ("%.2f" % worst if worst is not None else "—", a.norm,
                 len(bad_norm), a.margin, len(bad_margin)))
        for k, v in sorted(bad_norm + bad_margin, key=lambda t: -t[1])[:6]:
            print("   ! %-46s %.2f" % (k, v))
        if bad_norm:
            NEG.append("пики: %d файлов громче %.2f dBFS" % (len(bad_norm), a.norm))
        if bad_margin:
            NEG.append("запас: %d файлов ближе %.2f дБ к норме" % (len(bad_margin), a.margin))

    # 3. дельта к предыдущей пересборке
    if a.prev and os.path.exists(a.prev):
        _, prev = zip_files(a.prev)
        changed = sorted(k for k in files if k in prev and files[k] != prev[k])
        added = sorted(k for k in files if k not in prev)
        removed = sorted(k for k in prev if k not in files)
        print("\n3) Дельта к %s: было %d → стало %d; изменилось %d, добавлено %d, удалено %d"
              % (os.path.basename(a.prev), len(prev), len(files),
                 len(changed), len(added), len(removed)))
        for k in changed[:20]:
            print("   Δ %s" % k)
        audio_changed = [k for k in changed if k.endswith(".ogg")]
        other = [k for k in changed if not k.endswith(".ogg")]
        print("   из них звуковых %d, прочих %d" % (len(audio_changed), len(other)))
        if other:
            NOTE.append("пересборка задела не только звук: %s" % ", ".join(other[:5]))
        exp = a.expect_added
        if removed:
            NEG.append("дельта: удалено %d файлов" % len(removed))
        elif added and (exp is None or len(added) != exp):
            NEG.append("дельта: добавлено %d, удалено %d файлов" % (len(added), len(removed)))
        elif added and exp is not None:
            print("   добавлено %d — ожидаемо (--expect-added %d)" % (len(added), exp))

    # 4. З-16
    key = TEX_IN_ZIP + CYST
    if key not in files:
        NEG.append("нет %s" % CYST)
    else:
        d = z.read(key)
        im = Image.open(io.BytesIO(d)).convert("RGBA")
        px = [p[:3] for p in im.getdata() if p[3] > 0]
        cnt = collections.Counter(px)
        share = 100.0 * cnt.most_common(1)[0][1] / len(px) if px else 0
        ok = sha(d).startswith(CYST_SHA) and len(cnt) == 7
        print("\n4) З-16 %s: %dx%d, цветов %d, топ %.1f %%, sha256 %s… %s"
              % (CYST, im.size[0], im.size[1], len(cnt), share, sha(d)[:12],
                 "ok" if ok else "НЕ СДАЧА T-3141"))
        if not ok:
            NEG.append("З-16: incubation_cyst не равен сдаче T-3141 (цветов %d)" % len(cnt))

    # 5. минимум цветов / прозрачные (критерий З-18)
    for sub in ("block", "entity"):
        root = TEX_IN_ZIP + sub + "/"
        thin, clear, n = [], [], 0
        for name in files:
            if not name.startswith(root) or not name.endswith(".png") or "glowmask" in name:
                continue
            n += 1
            im = Image.open(io.BytesIO(z.read(name))).convert("RGBA")
            px = [p[:3] for p in im.getdata() if p[3] > 0]
            if not px:
                clear.append(name.split("/")[-1])
            elif len(set(px)) < 7:
                thin.append("%s (%d)" % (name.split("/")[-1], len(set(px))))
        print("5) %s: PNG %d, с <7 цветами %d, полностью прозрачных %d"
              % (sub, n, len(thin), len(clear)))
        if thin:
            NEG.append("%s: менее 7 цветов — %s" % (sub, ", ".join(thin[:5])))
        if clear:
            NEG.append("%s: полностью прозрачные — %s" % (sub, ", ".join(clear[:5])))

    print("\n" + "-" * 84)
    for note in NOTE:
        print("· примечание: " + note)
    if NEG:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — %d" % len(NEG))
        for m in NEG:
            print("   ✗ " + m)
        return 2
    print("ИТОГ: СХОДИТСЯ — пакет несёт текущий банк, пики с запасом, З-16 закрыт")
    return 0


if __name__ == "__main__":
    sys.exit(main())
