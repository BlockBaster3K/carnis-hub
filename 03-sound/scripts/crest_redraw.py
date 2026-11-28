#!/usr/bin/env python3
"""Приведение crest сэмплов ВНУТРИ события к одной цели — мягким срезом.

Зачем. Норма «разброс внутри события ≤ 3 дБ» меряется по RMS, а потолок пика —
по пику. Если crest (пик − RMS) у сэмплов разный, выравнивание RMS упирается в
потолок: чтобы поднять тихий, приходится поднимать и его пик. Проверено в S127:

  combat.flesh_hit: RMS расходится 4.63 дБ, пик всего 1.12 дБ → разница в ФОРМЕ
  (crest 18.02 / 19.47 / 21.53). Растянуть громкостью нельзя, не пробив −1.20.

Одинаковый crest делает выравнивание тривиальным: все пики встают на одно
значение, RMS выравнивается до 0.00 дБ, потолок не при чём.

Метод — срез пиков выше k*RMS (жёсткий, не tanh). Выбор измерен, не на глаз:
  * tanh меняет 2.6–3.8 % отсчётов и уводит crest НИЖЕ цели (16.32 при 18.00);
  * срез меняет 0.00–0.09 % отсчётов (2, 17, 21 отсчёт из 27–34 тысяч);
  * побочный продукт среза — гармоники: энергия > 10 кГц растёт на 0.02 / 0.18 /
    0.87 дБ. Меньше 1 дБ, сообщается в отчёте по каждому файлу.
Если нужен более мягкий вариант — параметр --method tanh, но он НЕ попадает в
цель по crest и требует второй итерации.

Длина сохраняется сэмпл-в-сэмпл (подбор паддинга до кодирования: Vorbis отдаёт
точную длину при правильном pad). Форма вне срезанных отсчётов не меняется.

CLI:
  python3 crest_redraw.py --measure combat/flesh_hit_01.ogg ...
  python3 crest_redraw.py --target 18.0 --out-dir /tmp/x  a.ogg b.ogg
"""
import argparse
import math
import os
import subprocess
import sys

import numpy as np

SR = 44100
FF = os.environ.get("FFMPEG") or ""


def _ffmpeg():
    global FF
    if FF:
        return FF
    try:
        import imageio_ffmpeg
        FF = imageio_ffmpeg.get_ffmpeg_exe()
        return FF
    except Exception:                                   # noqa: BLE001
        FF = "ffmpeg"
        return FF


def decode(path):
    out = subprocess.run([_ffmpeg(), "-v", "quiet", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True)
    if out.returncode != 0:
        raise RuntimeError("не декодируется: %s" % path)
    return np.frombuffer(out.stdout, dtype=np.float32).astype(np.float64)


def crest(y):
    return 20 * math.log10(float(np.abs(y).max())) - \
        20 * math.log10(float(np.sqrt((y ** 2).mean())))


def src_bitrate(path, n_samples):
    """Битрейт исходника по размеру файла: (байт * 8) / длительность."""
    dur = n_samples / float(SR)
    return int(round(os.path.getsize(path) * 8 / dur / 1000.0))


def encode_exact(y, out_path, want, br_candidates):
    """Закодировать так, чтобы декод FFMPEG дал РОВНО want отсчётов.

    Две ловушки, обе стоили времени:

    1. ЧЕМ МЕРИТЬ. libsndfile и ffmpeg считают длину OGG по-разному: у
       combat_flesh_hit_01 libsndfile отдаёт 27086, ffmpeg 26958 (блок Vorbis,
       128 отсчётов). Проект мерит ffmpeg (bank_normalize._rewrite_exact),
       поэтому и здесь эталон — ffmpeg.

    2. КАКИМ БИТРЕЙТОМ. Точная длина достижима не при любом битрейте: у этого
       файла на 160k нужного значения нет ни при каком паддинге (сетка длин
       прыгает 27008 → 27054 → 27086), а на 128k — достигается сразу при
       pad 128. Поэтому кандидаты перебираются от битрейта ИСХОДНИКА, а не от
       «универсального 160k». Перекодирование в родном битрейте заодно меньше
       искажает звук.
    """
    data = y.astype(np.float32)

    def _try(codec_args, pad):
        subprocess.run([_ffmpeg(), "-v", "error", "-y", "-f", "f32le",
                        "-ar", str(SR), "-ac", "1", "-i", "-"] + codec_args +
                       [out_path],
                       # .astype(np.float32) ОБЯЗАТЕЛЕН: np.zeros(pad) — это
                       # float64, конкатенация промотирует весь буфер, и ffmpeg,
                       # читая f32le, получает РОВНО вдвое больше отсчётов
                       # (8-байтовые числа читаются как пары 4-байтовых).
                       # Из-за этого все шесть файлов «не достигали длины».
                       input=np.concatenate([data, np.zeros(pad, np.float32)]
                                            ).astype(np.float32).tobytes(),
                       check=True)
        return len(decode(out_path)) == want

    for br in br_candidates:
        for pad in range(0, 2049, 32):
            if _try(["-c:a", "libvorbis", "-b:a", "%dk" % br], pad):
                return br, pad
    for q in ("3", "4", "5"):
        for pad in range(0, 513, 32):
            if _try(["-c:a", "libvorbis", "-q:a", q], pad):
                return "VBR q%s" % q, pad
    raise RuntimeError("точная длина недостижима: хотим %d, ffmpeg даёт %d"
                       % (want, len(decode(out_path))))


def redraw(x, target_crest, method="clip", max_iter=12):
    """Довести crest до target_crest ИТЕРАЦИЯМИ.

    Одного прохода мало: срез понижает пик, но одновременно понижает и RMS,
    поэтому crest после среза оказывается ВЫШЕ цели (у hive_spread_01_creep:
    цель 18.0, после одного прохода 18.65). Итерируем, пока не сойдётся:
    каждый шаг пересчитывает порог от текущего RMS.
    """
    y = np.array(x, dtype=np.float64)
    c = None
    for _ in range(max_iter):
        rms = float(np.sqrt((y ** 2).mean()))
        c = rms * 10 ** (target_crest / 20.0)
        if method == "tanh":
            y = c * np.tanh(y / c)
        else:
            y = np.clip(y, -c, c)
        if abs(crest(y) - target_crest) <= 0.02:
            break
    nclip = int(np.count_nonzero(np.abs(x) > (c or 0)))
    return y, c, nclip


def hf_share(z, f0=10000):
    X = np.abs(np.fft.rfft(z)) ** 2
    f = np.fft.rfftfreq(len(z), 1.0 / SR)
    return 10 * math.log10(X[f > f0].sum() / X.sum() + 1e-20)


def measure(paths):
    print("%-34s %7s %7s %6s %8s %8s" % ("файл", "RMS", "пик", "crest",
                                         "длина", "сейчас"))
    for p in paths:
        x = decode(p)
        rms = 20 * math.log10(np.sqrt((x ** 2).mean()))
        pk = 20 * math.log10(np.abs(x).max())
        print("%-34s %7.2f %7.2f %6.2f %8d %8.2f" %
              (os.path.basename(p), rms, pk, pk - rms, len(x), len(x) / SR))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--target", type=float, default=None, help="целевой crest, дБ")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--method", default="clip", choices=("clip", "tanh"))
    ap.add_argument("--br", default="160k")
    a = ap.parse_args(argv)

    if a.measure or a.target is None:
        return measure(a.files)
    if not a.out_dir:
        ap.error("нужен --out-dir")
    os.makedirs(a.out_dir, exist_ok=True)

    print("%-30s %6s %6s %6s %7s %8s %8s %9s %-9s" %
          ("файл", "crest0", "crest1", "срез", "длина", "пик0", "пик1",
           ">10кГц Δ", "кодек"))
    bad = 0
    for p in a.files:
        x = decode(p)
        want = len(x)
        y, c, nclip = redraw(x, a.target, a.method)
        dst = os.path.join(a.out_dir, os.path.basename(p))
        # Битрейт выбираем ПО РЕЗУЛЬТАТУ, а не по исходнику: кодек добавляет
        # собственный crest (шумовые пики), и на низком битрейте цель
        # недостижима — у flesh_hit_03 при 96k выходило 18.61 при цели 18.0.
        # Высокий битрейт меньше искажает форму, поэтому перебираем от
        # высокого и берём первый, попавший в ±0.15 дБ.
        cands = list(dict.fromkeys(
            [224, 192, 160, 144, 128, 112, 96] +
            [src_bitrate(p, want), int(a.br.rstrip("k"))]))
        cands = [c for c in cands if c > 0]
        best = None
        for br_c in cands:
            try:
                _, pad_used = encode_exact(y, dst, want, [br_c])
            except RuntimeError:
                continue
            err = abs(crest(decode(dst)) - a.target)
            if best is None or err < best[0]:
                best = (err, br_c, pad_used)
            if err <= 0.15:                  # попали — дальше не ищем
                break
        if best is None:
            print("  ✗ %s: точная длина недостижима ни в одном режиме" %
                  os.path.basename(p))
            bad += 1
            continue
        # Перекодировать лучшим режимом заново (детерминированно) — так в
        # каталоге остаётся ровно один файл, без промежуточных копий.
        encode_exact(y, dst, want, [best[1]])
        used = best[1]
        z = decode(dst)                      # мерим ПОСЛЕ кодирования, а не до
        c0, c1 = crest(x), crest(z)
        pk0, pk1 = 20 * math.log10(np.abs(x).max()), 20 * math.log10(np.abs(z).max())
        ok_len = "OK" if len(z) == want else "%+d" % (len(z) - want)
        ok_c = abs(c1 - a.target) <= 0.3
        bad += 0 if (ok_len == "OK" and ok_c) else 1
        print("%-30s %6.2f %6.2f %6d %7s %8.2f %8.2f %9.2f %-9s %s" %
              (os.path.basename(p), c0, c1, nclip, ok_len, pk0, pk1,
               hf_share(z) - hf_share(x), used,
               "" if ok_c else "✗ crest вне ±0.3"))
    print("\nфайлов с замечаниями: %d из %d" % (bad, len(a.files)))
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
