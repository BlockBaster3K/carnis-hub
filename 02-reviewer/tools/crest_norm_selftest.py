#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crest_norm_selftest.py — негативный и положительный тесты crest-нормы З-28.

Норма (решение Архитектора З-28): эталон crest — **round-trip** (оригинал →
декод → перекод тем же кодеком/битрейтом → декод), Δcrest считается против
него, поэтому шум кодека не принимается за дефект обработки.

Норма обязана (условие приёмки, R19):
  1. **ловить изменение тембра**: файл, у которого изменена спектральная
     окраска (не громкость), обязан дать |Δcrest| > 0,05 дБ;
  2. **не ловить шум кодека**: чистый перекод без обработки обязан уложиться
     в допуск;
  3. **честно маркировать чистый gain**: crest инвариантен к усилению,
     такой файл печатается «crest неприменим» (З-28 п.3), а не «пройдено».

Тестовые файлы строятся из реального файла канона: gain (−0,5 дБ), тембр
(полочный фильтр +6 дБ выше 4 кГц), контроль (чистый перекод).

Запуск: python3 02-reviewer/tools/crest_norm_selftest.py [файл-канона.ogg]
Код 0 — норма ведёт себя как обещано, 1 — расхождение.
"""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TOOL = os.path.join(HERE, "crest_delta.py")
ARCHIVE = os.path.join(REPO, "03-sound", "archive_zapas_2026-11-26")

try:
    import av
except ImportError:
    print("ОШИБКА: нужен PyAV")
    sys.exit(1)


def decode(path):
    c = av.open(path)
    st = c.streams.audio[0]
    sr = st.rate
    chunks = [fr.to_ndarray().astype("float32").ravel() for fr in c.decode(st)]
    c.close()
    return np.concatenate(chunks), sr


def encode(x, sr, bitrate=160000):
    out = io.BytesIO()
    with av.open(out, "w", format="ogg") as c:
        st = c.add_stream("vorbis", rate=sr,
                          options={"strict": "experimental"})
        st.bit_rate = bitrate
        frame = av.AudioFrame.from_ndarray(
            x.reshape(1, -1).astype("float32"), format="fltp", layout="mono")
        frame.sample_rate = sr
        for pkt in st.encode(frame):
            c.mux(pkt)
        for pkt in st.encode(None):
            c.mux(pkt)
    return out.getvalue()


def high_shelf(x, sr, gain_db=6.0, corner=4000.0):
    """Однополюсный полочный фильтр ВЧ: меняет тембр, RMS почти сохраняет."""
    a = np.exp(-2.0 * np.pi * corner / sr)
    # НЧ-составляющая (сглаженная) — вычитаем её из сигнала и возвращаем с усилением
    low = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = a * acc + (1 - a) * v
        low[i] = acc
    high = x - low
    g = 10 ** (gain_db / 20.0)
    y = low + high * g
    # нормируем RMS к исходному, чтобы тест был именно про тембр, а не про громкость
    rms_x = np.sqrt((x ** 2).mean())
    rms_y = np.sqrt((y ** 2).mean())
    if rms_y > 0:
        y *= rms_x / rms_y
    peak = np.abs(y).max()
    if peak > 0.9:
        y *= 0.9 / peak
    return y


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if src is None:
        cands = sorted(f for f in os.listdir(ARCHIVE) if f.endswith(".ogg"))
        if not cands:
            print("ОШИБКА: нет архива оригиналов %s" % ARCHIVE)
            return 1
        src = os.path.join(ARCHIVE, cands[0])
    if not os.path.isfile(src):
        print("ОШИБКА: нет файла %s" % src)
        return 1

    name = os.path.basename(src)
    x, sr = decode(src)
    tmp = tempfile.mkdtemp(prefix="crest_selftest_")
    bad = 0
    try:
        orig_dir = os.path.join(tmp, "orig")
        os.makedirs(orig_dir)
        shutil.copy(src, os.path.join(orig_dir, name))

        cases = {
            "gain": x * (10 ** (-0.5 / 20.0)),        # только громкость
            "timbre": high_shelf(x, sr),              # только тембр
            "transcode": x.copy(),                    # чистый перекод
        }
        for label, sig in cases.items():
            d = os.path.join(tmp, label)
            os.makedirs(d)
            with open(os.path.join(d, name), "wb") as f:
                f.write(encode(sig, sr))
            r = subprocess.run([sys.executable, TOOL, orig_dir, d,
                                "--roundtrip", "--tol", "0.05", "--top", "1"],
                               capture_output=True, text=True)
            out = r.stdout
            d_line = [ln for ln in out.splitlines() if ln.startswith(name)]
            delta = None
            if d_line:
                # строка таблицы: "... 0.75 !" — берём последнее число, а не
                # последний токен (после числа может стоять маркер «!»)
                m = re.search(r"([-+]?\d+\.\d+)\s*!?\s*$", d_line[0])
                if m:
                    delta = abs(float(m.group(1)))
            expect = {"gain": "ok", "timbre": "over", "transcode": "ok"}[label]
            got_over = r.returncode == 2
            if label == "gain":
                marked = "Только усиление" in out
                ok = (not got_over) and marked
                detail = "Δ=%.3f дБ, маркировка gain: %s" % (
                    delta if delta is not None else -1, "да" if marked else "НЕТ")
            elif label == "timbre":
                ok = got_over and (delta is not None and delta > 0.05)
                detail = "Δ=%.3f дБ, норма %s" % (
                    delta if delta is not None else -1,
                    "сработала" if got_over else "ПРОПУСТИЛА")
            else:
                ok = not got_over
                detail = "Δ=%.3f дБ (шум кодека)" % (delta if delta is not None else -1)
            print("%-10s ожидание %-5s | %s | %s"
                  % (label, expect, "OK" if ok else "РАСХОЖДЕНИЕ", detail))
            if not ok:
                bad += 1
                for ln in out.splitlines()[-6:]:
                    print("     " + ln)
        print("\nСлучаев: %d, расхождений: %d" % (len(cases), bad))
        return 0 if bad == 0 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
