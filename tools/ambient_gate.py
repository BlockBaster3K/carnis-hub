#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ambient_gate.py — приёмка ambient-фикса (ТЗ Архитектора «СРОЧНО 2», решения Р-31.2).

Считает ровно четыре числа, ничего не додумывая:

  1. пауза между пульсами = PULSE_INTERVAL_TICKS/20 - max(эффективная длина пульса)  >= 3,0 с
  2. pitch всех слоёв hive.pulse / hive.ambient / hive.ambient_close               == 1,0
  3. сумма громкостей одновременно звучащих слоёв (кровать + close)                <= 0,7
  4. эффективные длины слоёв внутри события равны (±0,05 с) — либо в коде
     видно, что одновременно играет только один слой

Вход: каталог пакета (например 01-coder/3.7.0) или zip-пакет.

Использование:
    python3 tools/ambient_gate.py <каталог|zip> [<каталог|zip> ...]

Код возврата: 0 — ИТОГ: СХОДИТСЯ, 2 — ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ, 1 — запуск/вход.

Значения, которые не удалось извлечь, печатаются как «НЕ НАЙДЕНО» и считаются
замечанием: молча подставлять нули нельзя — это был бы выдуманный вердикт.
"""
import io
import json
import os
import re
import struct
import sys
import zipfile

HANDLER = "src/main/java/com/carnis/mod/client/sound/HiveAmbientSoundHandler.java"
SOUNDS = "src/main/resources/assets/carnis/sounds.json"
SOUND_DIR = "src/main/resources/assets/carnis/sounds/"
EVENTS = {"hive.pulse": "пульс",
          "hive.ambient": "кровать",
          "hive.ambient_close": "close-слой"}
PAUSE_MIN_S = 3.0
VOLUME_MAX = 0.7
LEN_TOL_S = 0.05


def read_bytes(src, rel):
    if os.path.isdir(src):
        p = os.path.join(src, rel)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return f.read()
        return None
    with zipfile.ZipFile(src) as z:
        try:
            return z.read(rel)
        except KeyError:
            return None


def ogg_duration(data):
    """Длительность Ogg Vorbis по granuleposition последней страницы."""
    i = 0
    rate = None
    last = None
    while True:
        i = data.find(b"OggS", i)
        if i < 0:
            break
        nseg = data[i + 26]
        gran = struct.unpack("<q", data[i + 6:i + 14])[0]
        seg = data[i + 27:i + 27 + nseg]
        body = i + 27 + nseg + sum(seg)
        if gran > 0:
            last = gran
        if rate is None:
            j = data.find(b"\x01vorbis", i, body)
            if j >= 0:
                rate = struct.unpack("<I", data[j + 12:j + 16])[0]
        i = body
    if not rate or not last:
        return None
    return last / rate


def check(src):
    print("=== %s" % src)
    problems = []

    def note(msg):
        problems.append(msg)
        print("  [!] " + msg)

    code = read_bytes(src, HANDLER)
    sounds_raw = read_bytes(src, SOUNDS)
    if code is None:
        print("ОШИБКА: нет %s" % HANDLER)
        return None, 1
    if sounds_raw is None:
        print("ОШИБКА: нет %s" % SOUNDS)
        return None, 1
    code = code.decode("utf-8", "replace")
    sounds = json.loads(sounds_raw.decode("utf-8"))

    # --- 1. PULSE_INTERVAL_TICKS и пауза ---
    m = re.search(r"PULSE_INTERVAL_TICKS\s*=\s*(\d+)", code)
    interval_ticks = int(m.group(1)) if m else None
    print("\n1) Пауза между пульсами")
    if interval_ticks is None:
        note("в коде не найден PULSE_INTERVAL_TICKS")
        interval_s = None
    else:
        interval_s = interval_ticks / 20.0
        print("   PULSE_INTERVAL_TICKS = %d → интервал %.2f с" % (interval_ticks, interval_s))

    pulse = sounds.get("hive.pulse", {})
    pulse_lens = []
    for s in pulse.get("sounds", []):
        name = (s["name"] if isinstance(s, dict) else s).replace("carnis:", "")
        pitch = float(s.get("pitch", 1.0)) if isinstance(s, dict) else 1.0
        data = read_bytes(src, SOUND_DIR + name + ".ogg")
        if data is None:
            note("нет файла %s.ogg" % name)
            continue
        d = ogg_duration(data)
        if d is None:
            note("не удалось измерить длину %s.ogg" % name)
            continue
        pulse_lens.append((name, d, pitch, d / pitch))
        print("   %-24s %.3f с, pitch %.2f → эффективная %.3f с" % (name, d, pitch, d / pitch))
    if interval_s is not None and pulse_lens:
        longest = max(p[3] for p in pulse_lens)
        pause = interval_s - longest
        ok = pause >= PAUSE_MIN_S
        print("   пауза = %.2f - %.3f = %.3f с (нужно ≥ %.1f) %s"
              % (interval_s, longest, pause, PAUSE_MIN_S, "OK" if ok else "FAIL"))
        if not ok:
            note("пауза между пульсами %.2f с < %.1f с" % (pause, PAUSE_MIN_S))

    # --- 2. pitch всех слоёв ---
    print("\n2) pitch слоёв ambient")
    for ev, human in EVENTS.items():
        entries = sounds.get(ev, {}).get("sounds", [])
        if not entries:
            note("событие %s отсутствует в sounds.json" % ev)
            continue
        pitches = [float(s.get("pitch", 1.0)) if isinstance(s, dict) else 1.0 for s in entries]
        ok = all(abs(p - 1.0) < 1e-9 for p in pitches)
        print("   %-22s %-12s pitch %s %s" % (ev, human, pitches, "OK" if ok else "FAIL"))
        if not ok:
            note("%s: pitch не 1,0 — %s" % (ev, pitches))

    # --- 3. суммарная громкость одновременных слоёв ---
    print("\n3) Громкость одновременных слоёв")
    bed_m = re.search(r"([\d.]+)F\s*\*\s*\(float\)", code) or re.search(r"targetVolume\s*=\s*([\d.]+)F", code)
    clamp_m = re.search(r"Mth\.clamp\(targetVolume,\s*([\d.]+)F,\s*([\d.]+)F\)", code)
    close_m = re.search(r"targetVolume\s*\*\s*([\d.]+)F", code)
    bed = float(clamp_m.group(2)) if clamp_m else (float(bed_m.group(1)) if bed_m else None)
    close = float(close_m.group(1)) if close_m else None
    if bed is None:
        note("не найдена предельная громкость кровати в коде")
    if close is None:
        note("не найден множитель close-слоя в коде")
    if bed is not None and close is not None:
        total = bed + bed * close
        ok = total <= VOLUME_MAX + 1e-9
        print("   кровать %.2f + close %.2f×%.2f = %.2f (порог ≤ %.1f) %s"
              % (bed, bed, close, total, VOLUME_MAX, "OK" if ok else "FAIL"))
        if not ok:
            note("суммарная громкость %.2f > %.1f" % (total, VOLUME_MAX))

    # --- 4. эффективные длины равны либо слои не играют одновременно ---
    print("\n4) Эффективные длины слоёв")
    # close-слой существует в коде → он может звучать одновременно с кроватью,
    # значит длины обязаны совпадать (иначе биение).
    plays_together = re.search(r"closeSound\s*=\s*new|closeSound\.setTarget", code) is not None
    exclusive = not plays_together
    if plays_together:
        print("   в коде есть close-слой (closeSound) — слои могут звучать одновременно, "
              "значит длины обязаны совпадать")
    for ev, human in EVENTS.items():
        entries = sounds.get(ev, {}).get("sounds", [])
        effs = []
        for s in entries:
            name = (s["name"] if isinstance(s, dict) else s).replace("carnis:", "")
            pitch = float(s.get("pitch", 1.0)) if isinstance(s, dict) else 1.0
            data = read_bytes(src, SOUND_DIR + name + ".ogg")
            if data is None:
                continue
            d = ogg_duration(data)
            if d:
                effs.append(d / pitch)
        if len(effs) < 2:
            print("   %-22s %-12s слоёв %d — сравнивать нечего" % (ev, human, len(effs)))
            continue
        spread = max(effs) - min(effs)
        ok = spread <= LEN_TOL_S
        print("   %-22s %-12s эффективные %s разброс %.3f с (нужно ≤ %.2f) %s"
              % (ev, human, ["%.2f" % x for x in effs], spread, LEN_TOL_S, "OK" if ok else "FAIL"))
        if not ok:
            if exclusive:
                print("      (одновременных слоёв в коде нет — длины можно не выравнивать)")
            else:
                note("%s: эффективные длины расходятся на %.3f с" % (ev, spread))

    if plays_together:
        def effs_of(ev):
            out = []
            for s_ in sounds.get(ev, {}).get("sounds", []):
                name = (s_["name"] if isinstance(s_, dict) else s_).replace("carnis:", "")
                pitch = float(s_.get("pitch", 1.0)) if isinstance(s_, dict) else 1.0
                data = read_bytes(src, SOUND_DIR + name + ".ogg")
                if data is None:
                    continue
                d = ogg_duration(data)
                if d:
                    out.append(d / pitch)
            return out
        bed_effs = effs_of("hive.ambient")
        close_effs = effs_of("hive.ambient_close")
        if bed_effs and close_effs:
            cross = max(bed_effs + close_effs) - min(bed_effs + close_effs)
            ok = cross <= LEN_TOL_S
            print("   кровать+close вместе: разброс %.3f с (нужно ≤ %.2f) %s"
                  % (cross, LEN_TOL_S, "OK" if ok else "FAIL"))
            if not ok:
                note("слои играют одновременно, но их эффективные длины расходятся на %.3f с" % cross)

    print()
    if problems:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — %d" % len(problems))
        for i, p in enumerate(problems, 1):
            print("  %2d. %s" % (i, p))
        return problems, 2
    print("ИТОГ: СХОДИТСЯ")
    return problems, 0


def main():
    if len(sys.argv) < 2:
        print("использование: python3 tools/ambient_gate.py <каталог|zip> [...]")
        return 1
    worst = 0
    for src in sys.argv[1:]:
        if not os.path.exists(src):
            print("ОШИБКА: нет такого каталога или zip: %s" % src)
            worst = max(worst, 1)
            continue
        _, rc = check(src)
        worst = max(worst, rc or 0)
        print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
