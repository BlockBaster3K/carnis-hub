#!/usr/bin/env python3
"""S12: тембровая база банка — спектральный центр, энергия ниже 80 Гц, шов петли.

Нормы (ROADMAP_sound.md, S12):
  * спектральный центр  >= 400 Гц;
  * доля энергии < 80 Гц <= 25 %;
  * шов (разрыв на стыке начала и конца файла) <= 1 дБ.

Шов считается только у петель (ambient/pulse/loop/heartbeat — файлы, которые
играются по кругу). У одноразового удара шва нет по определению: его никто не
склеивает, и разрыв между концом и началом — не дефект.

Метрики считаются по всему файлу (для петель — по всему периоду), БЕЗ
нормализации: это свойство тембра, а не громкости.

Коды: 0 — все в норме; 2 — есть отклонения; 3 — не проверено.
"""
import argparse
import json
import os
import sys

CENTER_MIN = 400.0
LOW_BAND_HZ = 80.0
LOW_SHARE_MAX = 0.25
SEAM_MAX_DB = 1.0
LOOP_MARKERS = ("amb_", "hive_ambient", "hive_pulse", "loop", "heartbeat",
                "purifier_loop", "hive_heartbeat")


def metrics(path):
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, dtype="float64")
    if x.ndim > 1:
        x = x.mean(axis=1)
    if len(x) < 1024:
        return None
    # спектр мощности (Ханн), по всему файлу
    w = np.hanning(len(x))
    spec = np.abs(np.fft.rfft(x * w)) ** 2
    freqs = np.fft.rfftfreq(len(x), 1.0 / sr)
    total = spec.sum()
    if total <= 0:
        return None
    centre = float((freqs * spec).sum() / total)
    low_share = float(spec[freqs < LOW_BAND_HZ].sum() / total)
    # ШОВ — окно 100 мс (критерий по timbre_methodology.md), 10 мс справочно.
    # Первая версия считала только 10 мс и давала числа, несопоставимые с
    # эталонной методикой: на 10 мс шум края доминирует, на 100 мс видно уровень.
    # Оба числа сохраняются, вердикт выносится по 100 мс.
    k = max(1, int(0.01 * sr))
    a = float(np.sqrt(np.mean(x[:k] ** 2)))
    b = float(np.sqrt(np.mean(x[-k:] ** 2)))
    seam = abs(20 * np.log10(max(a, 1e-9)) - 20 * np.log10(max(b, 1e-9)))
    k100 = max(1, int(0.1 * sr))
    a100 = float(np.sqrt(np.mean(x[:k100] ** 2)))
    b100 = float(np.sqrt(np.mean(x[-k100:] ** 2)))
    # Если край — цифровая ТИШИНА (ровно нули), логарифм даёт бессмысленные
    # 230 дБ. Это отдельный класс дефекта: петля кончается провалом в ничто.
    # Пишем seam = None и помечаем silence_edge, чтобы не выдавать артефакт
    # логарифма за «шов 230 дБ».
    silence_edge = (a100 < 1e-7) or (b100 < 1e-7)
    if silence_edge:
        seam100 = float("inf")
    else:
        seam100 = abs(20 * np.log10(a100) - 20 * np.log10(b100))
    return {"center_hz": centre, "low_share": low_share, "seam_db": float(seam100),
            "seam10_db": float(seam), "silence_edge": silence_edge,
            "dur": len(x) / float(sr)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="03-sound/sounds")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="печатать и годные файлы")
    a = ap.parse_args(argv)
    try:
        import numpy  # noqa: F401
        import soundfile  # noqa: F401
    except ImportError:
        print("ОШИБКА: нет numpy/soundfile — тембр не проверить. Это НЕ «чисто».")
        return 3
    if not os.path.isdir(a.bank):
        print("ОШИБКА: банк %s отсутствует" % a.bank)
        return 3

    rows = []
    for dp, _, fs in os.walk(a.bank):
        for f in sorted(fs):
            if not f.endswith(".ogg"):
                continue
            p = os.path.join(dp, f)
            stem = f[:-4]
            try:
                r = metrics(p)
            except Exception as exc:
                rows.append((stem, None, str(exc)[:40]))
                continue
            rows.append((stem, r, None))

    checked = [r for r in rows if r[1]]
    bad_center = [(s, r) for s, r, _ in checked if r["center_hz"] < CENTER_MIN]
    bad_low = [(s, r) for s, r, _ in checked if r["low_share"] > LOW_SHARE_MAX]
    is_loop = lambda s: any(m in s for m in LOOP_MARKERS)
    bad_seam = [(s, r) for s, r, _ in checked
                if is_loop(s) and (r["silence_edge"] or r["seam_db"] > SEAM_MAX_DB)]
    silence = [(s, r) for s, r in bad_seam if r["silence_edge"]]
    errs = [(s, e) for s, r, e in rows if e]

    print("банк: %s — проверено %d файлов" % (a.bank, len(checked)))
    print("нормы: центр >= %.0f Гц, энергия < %.0f Гц <= %.0f%%, шов (петли) <= %.1f дБ"
          % (CENTER_MIN, LOW_BAND_HZ, LOW_SHARE_MAX * 100, SEAM_MAX_DB))
    print()
    print("отклонения: центр %d | низ %d | шов %d | не прочитано %d"
          % (len(bad_center), len(bad_low), len(bad_seam), len(errs)))
    if a.all:
        print()
        print("%-34s %9s %8s %7s" % ("файл", "центр Гц", "<80Гц", "шов дБ"))
        for s, r, _ in checked:
            print("%-34s %9.0f %7.1f%% %7.2f%s"
                  % (s, r["center_hz"], r["low_share"] * 100, r["seam_db"],
                     "  <-- ПЕТЛЯ" if is_loop(s) else ""))
    for title, lst, key, fmt in (
            ("ЦЕНТР НИЖЕ 400 Гц", bad_center, "center_hz", "%.0f Гц"),
            ("ЭНЕРГИЯ < 80 Гц ВЫШЕ 25%", bad_low, "low_share", "%.1f%%"),
            ("ШОВ ПЕТЛИ > 1 дБ", bad_seam, "seam_db", "%.2f дБ")):
        if lst:
            print()
            print(title + ":")
            for s, r in sorted(lst, key=lambda t: -t[1][key])[:25]:
                if key == "seam_db" and r["silence_edge"]:
                    print("  %-34s КРАЙ В ТИШИНЕ (0 отсчётов на конце/начале)"
                          % s)
                    continue
                print("  %-34s %s" % (s, fmt % (r[key] * 100 if key == "low_share"
                                               else r[key])))
            if len(lst) > 25:
                print("  … ещё %d" % (len(lst) - 25))
    if a.json:
        print(json.dumps([{"file": s, **{k: v for k, v in r.items()}}
                          for s, r, _ in checked], ensure_ascii=False))

    n = len(bad_center) + len(bad_low) + len(bad_seam)
    if errs or n:
        print()
        print("ИТОГ: отклонений %d, не прочитано %d из %d — тембровая база НЕ в норме"
              % (n, len(errs), len(checked)))
        return 2
    print()
    print("ИТОГ: все %d файлов в норме" % len(checked))
    return 0


if __name__ == "__main__":
    sys.exit(main())
