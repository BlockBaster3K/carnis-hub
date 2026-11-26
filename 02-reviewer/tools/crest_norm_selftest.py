#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crest_norm_selftest.py — негативный и положительный тесты crest-нормы З-28.

Норма (решение Архитектора З-28): эталон crest — **round-trip** (оригинал →
декод → перекод тем же кодеком/битрейтом → декод), Δcrest считается против
него, поэтому шум кодека не принимается за дефект обработки.

Норма обязана (условие приёмки, R19):
  1. **ловить изменение динамики**: лимитер и компрессор обязаны дать
     |Δcrest| >> 0,05 дБ. (Полочный фильтр ВЧ — НЕ цель нормы: crest почти
     не меняется от EQ, поэтому тембр проверяется `timbre_check.py`,
     а здесь печатается справочно и на код не влияет — замер 2026-11-22.)
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


def limiter_hard(x, gain_db=12.0, ceiling=0.9):
    """Жёсткий лимитер: усиление + обрезка по потолку. Crest обязан упасть."""
    return np.clip(x * (10 ** (gain_db / 20.0)), -ceiling, ceiling)


def compressor_tanh(x, drive=6.0, ceiling=0.9):
    """Мягкий компрессор: tanh-насыщение. Crest тоже обязан упасть."""
    y = np.tanh(x * drive)
    peak = np.abs(y).max()
    return y * (ceiling / peak) if peak > 0 else y


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
            "limiter": limiter_hard(x),               # динамика: обрезка по потолку
            "compr": compressor_tanh(x),              # динамика: tanh-насыщение
            "shelf": high_shelf(x, sr),               # EQ — справочно, не цель нормы
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
                # строка таблицы: "<файл>  crest_было  crest_стало  Δ  допуск [!]"
                # Δ — ВТОРОЕ число с конца; последнее — колонка допуска
                # (прежняя редакция брала последнее число и печатала «0.050»
                #  вместо 0.10 — ложное «расхождение» 2026-11-22)
                nums = re.findall(r"[-+]?\d+\.\d+", d_line[0])
                if len(nums) >= 2:
                    delta = abs(float(nums[-2]))
            expect = {"gain": "ok", "limiter": "over", "compr": "over",
                      "shelf": "info", "transcode": "ok"}[label]
            got_over = r.returncode == 2
            if label == "gain":
                marked = "Только усиление" in out
                ok = (not got_over) and marked
                detail = "Δ=%.3f дБ, маркировка gain: %s" % (
                    delta if delta is not None else -1, "да" if marked else "НЕТ")
            elif label in ("limiter", "compr"):
                ok = got_over and (delta is not None and delta > 0.05)
                detail = "Δ=%.3f дБ, норма %s" % (
                    delta if delta is not None else -1,
                    "сработала" if got_over else "ПРОПУСТИЛА")
            elif label == "shelf":
                # информационно: EQ почти не меняет crest — это не дефект нормы,
                # тембр проверяет timbre_check.py
                ok = True
                detail = "Δ=%.3f дБ (справочно: EQ — не цель crest)" % (
                    delta if delta is not None else -1)
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
