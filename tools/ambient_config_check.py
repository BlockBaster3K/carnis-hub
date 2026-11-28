#!/usr/bin/env python3
"""S8: ambient-конфиг — проверка чисел в коде, а не «на глаз».

Норма (из выжимки роли, S8):
  * интервал пульса 420…480 тиков (цель 450);
  * bed (постель) 0.45, потолок;
  * close 0.25, потолок;
  * сумма bed + close <= 0.70;
  * pitch = 1.0 (тон не сдвигать: сдвиг питча меняет воспринимаемую громкость
    и ломает уже посчитанные множители).

Инструмент читает ФАЙЛ КОДА и достаёт значения регулярками, но не «угадывает»:
если поле не найдено — это код 3 (не проверено), а не «ok».

Коды: 0 — в норме; 2 — расхождение; 3 — не проверено.
"""
import argparse
import re
import sys

RULES = {
    "PULSE_INTERVAL_TICKS": (420, 480, "интервал пульса, тиков"),
}
BED_MAX = 0.45
CLOSE_MAX = 0.25
SUM_MAX = 0.70
PITCH_EXPECT = 1.0


def find_const(src, name):
    m = re.search(r"\b%s\s*=\s*(-?[\d.]+)[fF]?\s*;" % re.escape(name), src)
    return float(m.group(1)) if m else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--java", required=True,
                    help="путь к HiveAmbientSoundHandler.java")
    a = ap.parse_args(argv)
    try:
        src = open(a.java, encoding="utf-8").read()
    except OSError as exc:
        print("ОШИБКА: %s" % exc)
        return 3

    problems = []
    unknown = []

    pulse = find_const(src, "PULSE_INTERVAL_TICKS")
    if pulse is None:
        unknown.append("PULSE_INTERVAL_TICKS")
    elif not (RULES["PULSE_INTERVAL_TICKS"][0] <= pulse
              <= RULES["PULSE_INTERVAL_TICKS"][1]):
        problems.append("интервал пульса %.0f тиков вне 420…480" % pulse)

    # bed: 0.45F * (...) и clamp(..., 0.0F, 0.45F)
    # bed — clamp(targetVolume, 0.0F, X) БЕЗ множителя;
    # close — clamp(targetVolume * K, 0.0F, X) С множителем.
    # Первая версия брала любой clamp(...targetVolume...) и путала их:
    # close показывался как 0.45, сумма 0.90 — ложное расхождение.
    bed_caps = re.findall(r"clamp\(targetVolume,\s*0\.0F,\s*([\d.]+)F\)", src)
    bed_base = re.findall(r"(\d+\.\d+)F\s*\*\s*\(float\)", src)
    bed = None
    if bed_caps:
        bed = max(float(x) for x in bed_caps)
    if bed is None and bed_base:
        bed = max(float(x) for x in bed_base)
    if bed is None:
        unknown.append("bed")
    elif bed > BED_MAX + 1e-9:
        problems.append("bed %.2f > %.2f" % (bed, BED_MAX))

    # close: 0.55F * targetVolume, clamp(..., 0.0F, 0.25F)
    close_caps = re.findall(r"clamp\(targetVolume\s*\*\s*[\d.]+F,\s*0\.0F,\s*([\d.]+)F\)", src)
    close = max(float(x) for x in close_caps) if close_caps else None
    if close is None:
        unknown.append("close")
    elif close > CLOSE_MAX + 1e-9:
        problems.append("close %.2f > %.2f" % (close, CLOSE_MAX))

    if bed is not None and close is not None:
        if bed + close > SUM_MAX + 1e-9:
            problems.append("сумма bed+close %.2f > %.2f" % (bed + close, SUM_MAX))

    # pitch живёт в HiveAmbientSoundInstance, а не в обработчике. Читаем рядом:
    # сдвиг питча меняет воспринимаемую громкость и ломает уже посчитанные
    # множители (2.263 / 0.731), поэтому pitch обязан быть ровно 1.0.
    import os
    inst = os.path.join(os.path.dirname(a.java), "HiveAmbientSoundInstance.java")
    pitch = None
    if os.path.isfile(inst):
        itxt = open(inst, encoding="utf-8").read()
        m = re.search(r"this\.pitch\s*=\s*([\d.]+)F", itxt)
        if m:
            pitch = float(m.group(1))
    if pitch is None:
        unknown.append("pitch (не найден this.pitch в HiveAmbientSoundInstance)")
    elif abs(pitch - PITCH_EXPECT) > 1e-9:
        problems.append("pitch %.2f != %.1f — сдвиг ломает посчитанные множители"
                        % (pitch, PITCH_EXPECT))

    print("файл: %s" % a.java)
    print("  интервал пульса: %s" % ("%.0f тиков" % pulse if pulse else "не найден"))
    print("  bed: %s | close: %s | сумма: %s"
          % ("%.2f" % bed if bed is not None else "?",
             "%.2f" % close if close is not None else "?",
             "%.2f" % (bed + close) if None not in (bed, close) else "?"))
    print("  нормы: интервал 420…480, bed <= %.2f, close <= %.2f, сумма <= %.2f"
          % (BED_MAX, CLOSE_MAX, SUM_MAX))
    print("  pitch: %s" % ("%.1f" % pitch if pitch is not None else "?"))
    for u in unknown:
        print("  НЕ НАЙДЕНО: %s — проверить не удалось" % u)
    for p in problems:
        print("  ✗ %s" % p)

    if problems:
        print("ИТОГ: расхождений %d" % len(problems))
        return 2
    if unknown:
        print("ИТОГ: нарушений 0, но НЕ ПРОВЕРЕНО: %s (это не «чисто»)" % ", ".join(unknown))
        return 3
    print("ИТОГ: ambient-конфиг в норме")
    return 0


if __name__ == "__main__":
    sys.exit(main())
