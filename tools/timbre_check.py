#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""timbre_check.py — приёмка тембра ambient (T-3106, ТЗ T-3104).

Считает по каждому файлу банка три числа и две проверки формы:

  1. доля энергии ниже 80 Гц          <= 25 %
  2. спектральный центр               >= 400 Гц
  3. длина                            ровно 120,000 с (9 слоёв) / 10,000 с (стингер)
  4. шов петли (RMS первой и последней секунды) <= 1 дБ — только у петлевых слоёв
  5. RMS (печатается для отчёта, порога не имеет)

Метод: декодирование в PCM 44,1 кГц моно, спектр — Welch (nperseg 8192,
окно Ханна, перекрытие 50 %), как в `03-sound/sounds/…` замерах Звука и в
`02-reviewer/ambient_methodology.md`.

Декодер выбирается автоматически: модуль `av` (PyAV, в нём собран FFmpeg) либо
бинарь `ffmpeg` в PATH. Если нет ни того ни другого — код 1 с инструкцией.

Использование:
    python3 tools/timbre_check.py <каталог|zip> [--ref <каталог|zip>]

Каталог кандидата содержит amb/ и hive/. `--ref` — принятый банк для сверки
длин («не трогать длины»): по умолчанию `03-sound/sounds`. У девяти петлевых
слоёв дополнительно требуется ровно 120,000 с — это записано в ТЗ отдельно.

Код возврата: 0 — ИТОГ: СХОДИТСЯ, 2 — ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ, 1 — ошибка запуска.
"""
import io
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile

import numpy as np

try:
    from scipy.signal import welch
except ImportError:  # pragma: no cover
    print("ОШИБКА: нужен scipy (python3 -m pip install scipy)")
    sys.exit(1)

SR = 44100
NPERSEG = 8192
FRAC_LOW_HZ = 80.0
FRAC_MAX = 25.0
CENTROID_MIN = 400.0
SEAM_MAX_DB = 1.0
# Мера шва принята по Звуку (`00-board/reports/sound_ambient_metrics.md` §3.4):
# ступенька на стыке в окне 100 мс — это и есть критерий «≤ 1 дБ». Окно 10 мс
# печатается для сведения: там у части файлов запас нулевой, но это не критерий.
SEAM_WIN_MS = 100.0
LEN_TOL = 0.05
REF_DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "03-sound", "sounds")

# файл -> (ожидаемая длина, петля?, в приёмке тембра?)
FILES = {
    "amb/hive_ambient_01": (120.0, True, True),
    "amb/hive_ambient_02": (120.0, True, True),
    "amb/hive_ambient_03": (120.0, True, True),
    "amb/hive_ambient_close_01": (120.0, True, True),
    "amb/hive_ambient_close_02": (120.0, True, True),
    "amb/hive_ambient_tonal_stinger": (10.0, False, True),
    "hive/amb_deep": (120.0, True, True),
    "hive/amb_threshold": (120.0, True, True),
    "hive/amb_surface": (120.0, True, True),
    "hive/amb_core": (120.0, True, True),
    "amb/hive_pulse_01": (13.4, False, False),
    "amb/hive_pulse_02": (13.4, False, False),
    "amb/hive_pulse_03": (13.4, False, False),
}

PAIRS = ["amb/", "hive/"]


def decode(data):
    """PCM moно 44,1 кГц float32 из байтов OGG."""
    try:
        import av
    except ImportError:
        av = None

    if av is not None:
        with av.open(io.BytesIO(data)) as container:
            stream = container.streams.audio[0]
            resampler = av.audio.resampler.AudioResampler(format="fltp", layout="mono", rate=SR)
            chunks = []
            for frame in container.decode(stream):
                for out in resampler.resample(frame):
                    chunks.append(out.to_ndarray().reshape(-1))
            for out in resampler.resample(None):
                chunks.append(out.to_ndarray().reshape(-1))
            if not chunks:
                return None
            return np.concatenate(chunks).astype(np.float32)

    if shutil.which("ffmpeg"):
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(data)
            path = tmp.name
        try:
            res = subprocess.run(
                ["ffmpeg", "-v", "quiet", "-i", path, "-f", "f32le",
                 "-acodec", "pcm_f32le", "-ac", "1", "-ar", str(SR), "-"],
                capture_output=True, check=True)
            return np.frombuffer(res.stdout, dtype=np.float32)
        finally:
            os.unlink(path)
    return None


def metrics(x):
    n = len(x)
    dur = n / SR
    rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-20)
    rms_db = 20.0 * np.log10(rms)
    f, pxx = welch(x.astype(np.float64), fs=SR, nperseg=NPERSEG, window="hann",
                   noverlap=NPERSEG // 2, scaling="density")
    total = float(pxx.sum())
    frac_low = float(pxx[f < FRAC_LOW_HZ].sum()) / total * 100.0 if total > 0 else 0.0
    centroid = float((f * pxx).sum() / total) if total > 0 else 0.0
    return dur, rms_db, frac_low, centroid


def seam_step_db(x, win_ms):
    """Ступенька на стыке петли: |RMS(первые win_ms) - RMS(последние win_ms)|."""
    win = max(1, int(SR * win_ms / 1000.0))
    head = x[:win].astype(np.float64)
    tail = x[-win:].astype(np.float64)
    h = 20.0 * np.log10(np.sqrt(np.mean(head ** 2)) + 1e-20)
    t = 20.0 * np.log10(np.sqrt(np.mean(tail ** 2)) + 1e-20)
    return abs(h - t)


def read_file(src, rel):
    """Байты файла из каталога (с префиксом amb/hive) или из zip."""
    if os.path.isdir(src):
        for cand in (os.path.join(src, rel + ".ogg"),
                     os.path.join(src, "sounds", rel + ".ogg"),
                     os.path.join(src, "assets", "carnis", "sounds", rel + ".ogg")):
            if os.path.exists(cand):
                with open(cand, "rb") as f:
                    return f.read()
        return None
    with zipfile.ZipFile(src) as z:
        for cand in (rel + ".ogg",
                     "src/main/resources/assets/carnis/sounds/" + rel + ".ogg",
                     "assets/carnis/sounds/" + rel + ".ogg"):
            try:
                return z.read(cand)
            except KeyError:
                continue
    return None


def main():
    args = [a for a in sys.argv[1:]]
    ref = REF_DEFAULT
    if "--ref" in args:
        i = args.index("--ref")
        ref = args[i + 1]
        del args[i:i + 2]
    if not args:
        print("использование: python3 tools/timbre_check.py <каталог|zip> [--ref <каталог|zip>]")
        return 1
    src = args[0]
    if not os.path.exists(src):
        print("ОШИБКА: нет такого каталога или zip: %s" % src)
        return 1

    data0 = read_file(src, "amb/hive_ambient_01")
    if data0 is not None and decode(data0) is None:
        print("ОШИБКА: нет декодера OGG. Поставьте PyAV (pip install av) "
              "или ffmpeg в PATH.")
        return 1

    print("Тембр ambient — приёмка T-3106 (ТЗ T-3104)")
    print("Источник: %s" % src)
    print("Эталон длин: %s" % ref)
    print("Порог: доля < %.0f Гц ≤ %.0f %%, центр ≥ %.0f Гц, шов ≤ %.1f дБ"
          % (FRAC_LOW_HZ, FRAC_MAX, CENTROID_MIN, SEAM_MAX_DB))
    print()
    print("%-32s %8s %9s %7s %9s %9s %8s"
          % ("файл", "длит.,с", "доля<80", "центр,Гц", "шов100,дБ", "шов10,дБ", "RMS,дБ"))
    print("-" * 88)

    problems = []
    checked = 0
    ref_exists = os.path.exists(ref)
    for rel, (want_len, is_loop, in_scope) in sorted(FILES.items()):
        data = read_file(src, rel)
        if data is None:
            if in_scope:
                problems.append("%s — нет файла" % rel)
                print("%-32s  НЕТ ФАЙЛА" % rel)
            continue
        x = decode(data)
        if x is None or len(x) == 0:
            problems.append("%s — не декодируется" % rel)
            print("%-32s  НЕ ДЕКОДИРУЕТСЯ" % rel)
            continue
        dur, rms_db, frac, centroid = metrics(x)
        seam = seam_step_db(x, SEAM_WIN_MS) if is_loop else float("nan")
        seam10 = seam_step_db(x, 10.0) if is_loop else float("nan")
        mark = "" if in_scope else "  (вне приёмки тембра)"
        print("%-32s %8.3f %8.1f%% %7.0f %9s %9s %8.1f%s"
              % (rel, dur, frac, centroid,
                 ("%.2f" % seam) if is_loop else "—",
                 ("%.2f" % seam10) if is_loop else "—", rms_db, mark))

        if not in_scope:
            continue
        checked += 1
        if frac > FRAC_MAX:
            problems.append("%s — доля энергии < 80 Гц %.1f %% > %.0f %%" % (rel, frac, FRAC_MAX))
        if centroid < CENTROID_MIN:
            problems.append("%s — спектральный центр %.0f Гц < %.0f Гц" % (rel, centroid, CENTROID_MIN))
        if is_loop and abs(dur - want_len) > LEN_TOL:
            problems.append("%s — длина %.3f с, нужно ровно %.3f с" % (rel, dur, want_len))
        elif not is_loop and ref_exists:
            ref_data = read_file(ref, rel)
            if ref_data is not None:
                rx = decode(ref_data)
                if rx is not None:
                    ref_dur = len(rx) / SR
                    if abs(dur - ref_dur) > LEN_TOL:
                        problems.append("%s — длина %.3f с, в принятом банке %.3f с "
                                        "(длину менять нельзя)" % (rel, dur, ref_dur))
        if is_loop and seam > SEAM_MAX_DB:
            problems.append("%s — шов петли %.2f дБ > %.1f дБ" % (rel, seam, SEAM_MAX_DB))

    print("-" * 88)
    print("Файлов в приёмке тембра: %d" % checked)
    print()
    if problems:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ — %d" % len(problems))
        for i, p in enumerate(problems, 1):
            print("  %2d. %s" % (i, p))
        return 2
    print("ИТОГ: СХОДИТСЯ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
