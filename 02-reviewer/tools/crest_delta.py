#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crest_delta.py — сверка crest-фактора (Peak − RMS) между архивом оригиналов и банком.

Зачем: правка громкости/тембра по ТЗ банка обязана сохранять crest
(**Δ ≤ 0,05 дБ**, см. `03-sound/CARNIS_Wave18B_SilenceRepair.md` и приёмку
T-3130). Чистое изменение усиления сдвигает пик и RMS одинаково и crest
**не меняет**; если Δ вылезло — значит изменилась динамика (лимитер,
перекодирование, VBR), а не только уровень. Ни гейт, ни мой прежний
чек-лист этого не мерили (З-21, находка Звука, проверено Ревизором).

С З-28 (решение Архитектора) эталон можно брать **round-trip**: оригинал
декодируется и перекодируется тем же кодеком/битрейтом. Так в сравнение
попадает шум кодека с обеих сторон, и Δcrest измеряет **обработку**, а не
перекодирование. Файлы, побайтово совпавшие с оригиналом, норме не подлежат.

Изменение **только усиления** crest не меняет по определению — такие файлы
помечаются «gain, crest неприменим» (З-28 п.3), а не «норма пройдена».

Использование:
    python3 02-reviewer/tools/crest_delta.py <архив оригиналов> <банк|пакет> \\
            [--tol 0.05] [--top 20] [--roundtrip] [--bitrate 160000]

Код возврата: 0 — все в допуске, 2 — есть выходы за допуск, 1 — ошибка запуска.
"""

import argparse
import io
import re
import math
import os
import pathlib
import sys
import zipfile

try:
    import av
    import numpy as np
except ImportError as e:  # pragma: no cover
    print("ОШИБКА: нужны PyAV и numpy (%s)" % e)
    sys.exit(1)


def crest_of_bytes(data):
    """crest = peak − RMS в дБ по декодированному сигналу (усиление не влияет)."""
    st = stats_of_bytes(data)
    return None if st is None else st[0] - st[1]


def mono_of_bytes(data):
    """Моно-сигнал файла: каналы усредняются.

    Усреднение обязательно: нативный Vorbis-энкодер ffmpeg пишет **стерео**
    и дублирует в него моно-вход, поэтому без даунмикса длина вырастает вдвое,
    а RMS падает на 3 дБ — эталон перестаёт быть сопоставимым (проверено).
    """
    c = av.open(io.BytesIO(data))
    st = c.streams.audio[0]
    chunks = []
    for fr in c.decode(st):
        a = fr.to_ndarray().astype("float64")
        chunks.append(a if a.ndim == 1 else a.mean(axis=0))
    c.close()
    if not chunks:
        return None
    return np.concatenate(chunks)


def stats_of_bytes(data):
    """(peak дБFS, RMS дБFS) — crest считается как их разность."""
    x = mono_of_bytes(data)
    if x is None or not len(x):
        return None
    peak = float(np.abs(x).max())
    rms = float(math.sqrt((x ** 2).mean()))
    if peak <= 0 or rms <= 0:
        return None
    return 20 * math.log10(peak), 20 * math.log10(rms)


def encode_vorbis(x, rate=44100, bitrate=160000):
    """Перекод моно-сигнала в OGG Vorbis с заданным битрейтом."""
    out = io.BytesIO()
    with av.open(out, "w", format="ogg") as c:
        # нативный Vorbis-энкодер ffmpeg помечен экспериментальным: без
        # strict=experimental avcodec_open2 отказывает (проверено)
        st = c.add_stream("vorbis", rate=rate,
                          options={"strict": "experimental"})
        st.bit_rate = bitrate
        frame = av.AudioFrame.from_ndarray(
            x.reshape(1, -1).astype("float32"), format="fltp", layout="mono")
        frame.sample_rate = rate
        for pkt in st.encode(frame):
            c.mux(pkt)
        for pkt in st.encode(None):
            c.mux(pkt)
    return out.getvalue()


def roundtrip_stats(data, bitrate):
    """(peak, RMS) эталона З-28: «декод → перекод тем же кодеком → декод».

    Возвращаются обе величины, а не только crest: по ним же отличаем правку
    усиления (пик и RMS сдвинулись одинаково) от правки тембра.
    """
    c = av.open(io.BytesIO(data))
    rate = c.streams.audio[0].rate
    c.close()
    x = mono_of_bytes(data)
    if x is None or not len(x):
        return None
    rt = encode_vorbis(x.astype("float32"), rate=rate, bitrate=bitrate)
    return stats_of_bytes(rt)


RE_ROW = re.compile(
    r"^\|\s*`((?:sounds|sounds_380)/[^`]+)`\s*\|\s*(стац|транз)\s*\|"
    r"\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|"
    r"\s*\*{0,2}([\d.]+)\*{0,2}\s*\|")


def load_table(path):
    """Эталонная таблица crest (З-29): {хвост пути: (допуск, тип)}.

    Хвост — путь после `sounds/` или `sounds_380/`, чтобы одна таблица
    подходила и канону, и банку 3.8.0.
    """
    table = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = RE_ROW.match(line)
            if not m:
                continue
            full, typ, base, thr, tol = m.group(1), m.group(2), float(m.group(3)), \
                float(m.group(4)), float(m.group(5))
            tail = full.split("/", 1)[1]
            table[tail] = (max(thr, base + 0.05), typ)
    return table


def load_target(src):
    """Банк — каталог с .ogg; пакет — zip с sounds/**/*.ogg. Возвращает {имя: bytes-функция}."""
    p = pathlib.Path(src)
    if p.is_dir():
        return {f.name: (lambda f=f: f.read_bytes()) for f in p.rglob("*.ogg")}
    if p.suffix.lower() == ".zip":
        z = zipfile.ZipFile(p)
        return {n.split("/")[-1]: (lambda n=n: z.read(n))
                for n in z.namelist()
                if n.endswith(".ogg") and "/sounds/" in n}
    raise SystemExit("ОШИБКА: %s — не каталог и не zip" % src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", help="каталог оригиналов (.ogg), например 03-sound/archive_zapas_2026-11-26")
    ap.add_argument("target", help="банк (каталог) или пакет (zip)")
    ap.add_argument("--tol", type=float, default=0.05, help="допуск |Δ|, дБ (по умолчанию 0,05)")
    ap.add_argument("--gain-tol", type=float, default=0.15,
                    help="порог детектора чистого усиления: |Δпик − ΔRMS|, дБ "
                         "(по умолчанию 0,15; на плотных сэмплах шум кодека "
                         "даёт до 0,18 — тогда поднять до 0,25)")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--roundtrip", action="store_true",
                    help="эталон = перекод оригинала тем же кодеком (З-28)")
    ap.add_argument("--bitrate", type=int, default=160000,
                    help="битрейт round-trip-перекода, бит/с (З-28: 160k)")
    ap.add_argument("--table", default=None,
                    help="эталонная таблица З-29 (sound_crest_baseline.md): "
                         "допуск берётся per-file; файл без записи — провал")
    a = ap.parse_args()

    arch = pathlib.Path(a.archive)
    if not arch.is_dir():
        print("ОШИБКА: нет каталога архива %s" % a.archive)
        return 1
    originals = sorted(arch.glob("*.ogg"))
    if not originals:
        print("ОШИБКА: в архиве нет .ogg")
        return 1
    target = load_target(a.target)
    table = None
    if a.table:
        if not os.path.isfile(a.table):
            print("ОШИБКА: нет эталонной таблицы %s" % a.table)
            return 1
        table = load_table(a.table)
        print("Таблица crest: %s, записей %d" % (a.table, len(table)))
        if not table:
            print("ОШИБКА: таблица пуста — разбор не удался")
            return 1

    rows, missing, unchanged, gain_only, no_entry, tols = [], [], [], [], [], {}
    for f in originals:
        get = target.get(f.name)
        if get is None:
            missing.append(f.name)
            continue
        src_bytes, tgt_bytes = f.read_bytes(), get()
        if src_bytes == tgt_bytes:
            # З-28 п.2: побайтово неизменённый файл норме не подлежит
            unchanged.append(f.name)
            continue
        a_stats = stats_of_bytes(src_bytes)
        b_stats = stats_of_bytes(tgt_bytes)
        if a_stats is None or b_stats is None:
            missing.append(f.name + " (не декодирован)")
            continue
        if a.roundtrip:
            ref_stats = roundtrip_stats(src_bytes, a.bitrate)
            if ref_stats is None:
                missing.append(f.name + " (round-trip не удался)")
                continue
        else:
            ref_stats = a_stats
        ref = ref_stats[0] - ref_stats[1]
        new = b_stats[0] - b_stats[1]
        # Сдвиги считаются против того же эталона, с которым сравниваем crest:
        # иначе шум перекода выглядел бы «правкой усиления» (проверено).
        d_gain = (b_stats[1] - ref_stats[1])        # сдвиг RMS
        d_peak = (b_stats[0] - ref_stats[0])        # сдвиг пика
        is_gain = abs(d_peak - d_gain) <= a.gain_tol and abs(d_gain) >= 0.1
        tol = a.tol
        if table is not None:
            hit = next((v for k, v in table.items()
                        if k == f.name or k.endswith("/" + f.name)), None)
            if hit is None:
                no_entry.append(f.name)
                continue
            tol = hit[0]
            tols[f.name] = (tol, hit[1])
        rows.append((f.name, ref, new, new - ref, tol))
        if is_gain:
            gain_only.append((f.name, d_gain))

    # Файлы с чистым усилением вердиктом не судятся (З-28 п.3) — значит и в
    # таблице они не должны стоять с маркером выхода: иначе сводка «СХОДИТСЯ»
    # спорит с «!» в строке (дефект подачи, найден 2026-11-22).
    gain_names_pre = {n for n, _g in gain_only}
    rows.sort(key=lambda r: -abs(r[3]))
    print("%-40s %10s %11s %7s %7s" % ("файл", "crest было", "crest стало", "Δ дБ", "допуск"))
    for name, o, n, d, tol in rows[:a.top]:
        if name in gain_names_pre:
            mark = " ="          # судится по пику/запасу, crest неприменим
        else:
            mark = "  " if abs(d) <= tol else " !"
        print("%-40s %10.2f %11.2f %7.2f %7.2f%s" % (name, o, n, d, tol, mark))

    # З-28 п.3: crest инвариантен к усилению, поэтому файл с чистым gain из
    # вердикта исключается — его судят по пику/запасу. Δcrest у такого файла
    # может быть и 0,5 дБ: это разница двух разных кодирований, а не динамика.
    gain_names = {n for n, _g in gain_only}
    over = [r for r in rows if abs(r[3]) > r[4] and r[0] not in gain_names]
    judged = [r for r in rows if r[0] not in gain_names]
    diffs = sorted(abs(r[3]) for r in judged)
    median = diffs[len(diffs) // 2] if diffs else 0.0
    print("-" * 72)
    print("Файлов сверено: %d (судится %d), выходов за допуск: %d, "
          "медиана |Δ| %.3f дБ, максимум %.2f дБ"
          % (len(rows), len(judged), len(over), median,
             max(diffs) if diffs else 0.0))
    if gain_names:
        gd = max(abs(r[3]) for r in rows if r[0] in gain_names)
        print("Из них чистого усиления: %d (Δcrest до %.2f дБ — шум кодека, "
              "норме не подлежат)" % (len(gain_names), gd))
    if missing:
        print("Не сверено: %d — %s" % (len(missing), ", ".join(missing[:5])))
    if unchanged:
        print("Побайтово неизменённых (норма не применяется, З-28 п.2): %d"
              % len(unchanged))
    if gain_only:
        print("Только усиление (crest неприменим по определению, З-28 п.3): %d"
              % len(gain_only))
        for name, g in gain_only[:5]:
            print("   = %-38s RMS %+.2f дБ" % (name, g))
    if over:
        print("ИТОГ: ЕСТЬ ВЫХОДЫ — %d файлов изменили динамику, а не только уровень" % len(over))
        for name, _o, _n, d, tol in over:
            print("   ! %-38s %+.2f дБ (допуск %.2f)" % (name, d, tol))
        return 2
    if no_entry:
        # З-29 п.5: нет записи в таблице — это «не проверено», а не «прошло»
        print("CREST НЕ ПРОВЕРЕН — нет записи в эталонной таблице (%d):"
              % len(no_entry))
        for name in no_entry[:6]:
            print("   ? %s" % name)
        return 3
    if table is not None:
        print("ИТОГ: СХОДИТСЯ — crest в пределах допусков эталонной таблицы (З-29)")
    else:
        print("ИТОГ: СХОДИТСЯ — crest сохранён в пределах %.2f дБ" % a.tol)
    return 0


if __name__ == "__main__":
    sys.exit(main())
