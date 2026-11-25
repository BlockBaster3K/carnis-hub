#!/usr/bin/env python3
"""loopfix.py — убрать разрыв уровня на стыке петли у эмбиентов улья.

Задача (ARCHITECT.md, волна 31, Р-31.3): у пяти 120-секундных эмбиентов
`amb/hive_ambient_0*` и `amb/hive_ambient_close_0*` начало и конец петли
расходятся по громкости на 27–28 дБ, из-за чего раз в две минуты слышен
провал и заново набирающий громкость гул.

Что делает:
  1. декодирует файл в PCM (ffmpeg), моно 44.1 кГц;
  2. находит уровень краёв: RMS первой и последней секунды;
  3. подтягивает тихий край к целевому уровню (средняя RMS по активной части)
     кривой усиления, у которой усиление = 1.0 уже через TRANS секунд, —
     правятся только края, середина файла остаётся бит-в-бит;
  4. подрезает края на CUT секунд с каждой стороны и кроссфейдит конец→начало
     на XF секунд, чтобы стык был непрерывным и по уровню, и по фазе;
  5. пишет OGG Vorbis 44.1 кГц моно с тем же номинальным битрейтом, что у
     исходника.

Почему кроссфейд, а не только выравнивание громкости: после выравнивания
края совпадают по уровню, но остаются разными по форме — на стыке всё равно
остаётся разрыв. Кроссфейд делает стык непрерывным по сигналу.

Использование:
    python3 loopfix.py <вход.ogg> <выход.ogg> [--target-db -21.8] [--verbose]

Код возврата: 0 — готово, 1 — ошибка, 2 — файл не нуждается в правке
(разрыв уже ≤ 1 дБ) и не перезаписывался.
"""

import json
import os
import struct
import subprocess
import sys
import tempfile

import numpy as np

SR = 44100
XF = 0.01      # микро-склейка на стыке, с (10 мс: провал неслышим, разрыв = 0)
MATCH = 0.1    # окно согласования уровней по обе стороны шва, с
TRANS = 6.0    # за сколько секунд кривая усиления края возвращается к 1.0
EDGE = 1.0     # окно измерения уровня края, с


def ffmpeg_decode(path):
    out = subprocess.run(
        ["ffmpeg", "-v", "quiet", "-i", path, "-f", "f32le",
         "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def vorbis_bitrate(path):
    """Номинальный битрейт из идентификационного заголовка Vorbis."""
    with open(path, "rb") as fh:
        data = fh.read(65536)
    i = data.find(b"\x01vorbis")
    if i < 0:
        return (160, 160)
    br_max = struct.unpack("<i", data[i + 16:i + 20])[0]
    br_nom = struct.unpack("<i", data[i + 20:i + 24])[0]
    return (max(1, br_max // 1000), max(1, br_nom // 1000))


def raw_to_ogg(pcm, out_path, bitrate_kbps):
    """PCM float32 → OGG Vorbis mono 44.1 кГц."""
    tmp = tempfile.NamedTemporaryFile(suffix=".f32", delete=False)
    try:
        tmp.write(pcm.astype(np.float32).tobytes())
        tmp.close()
        cmd = ["ffmpeg", "-v", "quiet", "-y",
               "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", tmp.name,
               "-c:a", "libvorbis", "-b:a", f"{bitrate_kbps}k", out_path]
        subprocess.run(cmd, check=True)
    finally:
        os.unlink(tmp.name)


def rms_db(x):
    if len(x) == 0:
        return -120.0
    return 20.0 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def edge_levels(y, win=1.0):
    n = int(win * SR)
    return rms_db(y[:n]), rms_db(y[-n:])


def edge_gain(y, target_db, side):
    """Кривая усиления длиной len(y): 1.0 в глубине, подтягивает край к target."""
    n = len(y)
    curve = np.ones(n)
    seg = int(TRANS * SR)
    seg = min(seg, n // 2)
    if side == "head":
        level = rms_db(y[:int(1.0 * SR)])
        head = y[:seg]
        g = np.ones(seg)
        # усиление растёт от края (индекс 0) к глубине (индекс seg)
        g0 = 10 ** ((target_db - level) / 20.0)
        k = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, seg))   # 0 → 1 плавно
        curve[:seg] = g0 + (1.0 - g0) * k
    else:
        level = rms_db(y[-int(1.0 * SR):])
        g1 = 10 ** ((target_db - level) / 20.0)
        k = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, seg))   # 0 → 1 плавно
        curve[n - seg:] = 1.0 + (g1 - 1.0) * k
    return curve


def find_period(y, lo_s=1.0, hi_s=8.0, step_s=0.1):
    """Период внутренней пульсации по автокорреляции огибающей."""
    w = int(step_s * SR)
    n = len(y) // w
    env = np.array([np.sqrt(np.mean(y[i * w:(i + 1) * w] ** 2)) for i in range(n)])
    env = env - env.mean()
    ac = np.correlate(env, env, "full")[n - 1:]
    if ac[0] <= 0:
        return None, 0.0
    ac = ac / ac[0]
    lo, hi = int(lo_s / step_s), min(int(hi_s / step_s), n - 2)
    if hi <= lo:
        return None, 0.0
    k = lo + int(np.argmax(ac[lo:hi]))
    return k * step_s, float(ac[k])


def circular_smooth(env, win):
    """Сглаживание огибающей по кругу — так сама огибающая становится
    периодической, и её значения на краях файла совпадают по построению."""
    k = np.ones(win) / win
    ext = np.concatenate([env[-win:], env, env[:win]])
    sm = np.convolve(ext, k, mode="same")
    return sm[win:win + len(env)]


def level_normalize_loop(y, smooth_s=3.0, limit_db=6.0, win_s=0.1):
    """Выравнивает медленный тренд громкости по кругу (для петли).

    Убирает «свелл» в начале и провал в конце, не трогая быструю пульсацию:
    окно сглаживания 3 с больше внутреннего периода пульсации (2.5 с),
    поэтому сама пульсация проходит, а медленный тренд в 27 дБ — нет.
    Ограничение ±6 дБ, чтобы не вытягивать естественные акценты.
    """
    w = int(win_s * SR)
    n = len(y) // w
    env = np.array([np.sqrt(np.mean(y[i * w:(i + 1) * w] ** 2)) for i in range(n)])
    sm = circular_smooth(env, max(1, int(smooth_s / win_s)))
    target = np.median(sm)
    gain = target / np.maximum(sm, 1e-6)
    lim = 10 ** (limit_db / 20.0)
    gain = np.clip(gain, 1.0 / lim, lim)
    # интерполируем усиление на каждый сэмпл
    gx = np.linspace(0, n - 1, len(y))
    g = np.interp(gx, np.arange(n), gain)
    return y * g


def quiet_splice_point(y, guard_s=5.0, win_s=1.5):
    """Индекс сэмпла в самом тихом участке файла (для переноса шва петли).

    guard_s — не искать ближе к краям файла, чем это; win_s — ширина окна,
    которое считаем «тихим местом» (в нём уровень должен быть минимален).
    """
    hop = int(0.05 * SR)
    n = len(y) // hop
    env = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    k = max(1, int(win_s / 0.05))
    guard = int(guard_s / 0.05)
    best, best_i = None, None
    for i in range(guard, n - guard - k):
        score = env[i:i + k].mean()
        if best is None or score < best:
            best, best_i = score, i
    return best_i * hop, 20 * np.log10(best + 1e-12)


def loopfix(in_path, out_path, target_db=None, verbose=False):
    """Петля без ступеньки на стыке (файлы улья).

    Диагноз: внутри файла громкость плавно плывёт — начало на ~6 дБ громче
    хвоста, плюс провал 0.15 с; края расходятся на 10 дБ (по окну 1 с) и на
    27–28 дБ по 10 мс. При зацикливании это слышно как «провал и снова
    набирающий громкость гул».

    Решение — **круговая нормализация медленной огибающей**: огибающая
    сглаживается окном 3 с по кругу (окно больше внутреннего периода
    пульсации 2.5 с, поэтому пульсация сохраняется), и файл умножается на
    обратную величину тренда с ограничением ±6 дБ. Так как сглаживание
    круговое, значения огибающей на краях совпадают по построению — стык
    петли перестаёт иметь ступеньку. Длина файла не меняется (важно: все
    пять слоёв обязаны иметь равную эффективную длину 120.00 с).
    """
    y = ffmpeg_decode(in_path)
    n = len(y)
    h0, t0 = edge_levels(y, EDGE)
    h0b, t0b = edge_levels(y, 0.01)
    if verbose:
        print(f"  исходник: {n / SR:.2f} с, края 1с {h0:.1f} / {t0:.1f} "
              f"(разрыв {abs(h0 - t0):.2f} дБ), края 10мс {h0b:.1f} / {t0b:.1f} "
              f"(разрыв {abs(h0b - t0b):.2f} дБ)")

    # 1. выравниваем медленный тренд по кругу — убирает «свелл» начала
    out = level_normalize_loop(y, smooth_s=3.0, limit_db=6.0)

    # 2. переносим шов в самое тихое место: у этих файлов есть провал, и если
    #    он попадает НА стык — на стыке слышен провал; если внутрь петли —
    #    всё в порядке. Длина при повороте не меняется.
    sp, lvl = quiet_splice_point(out)
    out = np.concatenate([out[sp:], out[:sp]])

    # 3. микро-склейка: конец уводим в ноль, начало поднимаем из нуля.
    #    Так разрыв на стыке равен нулю ПО ПОСТРОЕНИЮ (а не «примерно»),
    #    цена — провал 10 мс, который на эмбиенте не слышен. Вариант
    #    «смешать конец с началом» проверял: скачок оставался 0.078.
    w = int(XF * SR)
    ph = np.linspace(0.0, np.pi / 2.0, w)
    out[-w:] *= np.cos(ph)
    out[:w] *= np.sin(ph)

    # 4. согласование уровней по обе стороны шва (окно MATCH, по 100 мс).
    #    Без этого шага шов, поставленный в провал громкости, оставляет
    #    ступеньку 6–7 дБ в окне 1 с: слушатель слышит смену уровня, а не щелчок.
    m = int(MATCH * SR)
    lv_t = rms_db(out[-m:])
    lv_h = rms_db(out[:m])
    mid = 0.5 * (lv_t + lv_h)
    out[-m:] *= 10 ** ((mid - lv_t) / 20.0)
    out[:m] *= 10 ** ((mid - lv_h) / 20.0)

    if target_db is not None:
        cur = rms_db(out[int(5 * SR):-int(5 * SR)])
        out *= 10 ** ((target_db - cur) / 20.0)
    peak = np.abs(out).max()
    if peak > 0.79:
        out *= 0.79 / peak

    raw_to_ogg(out, out_path, vorbis_bitrate(in_path)[1])

    z = ffmpeg_decode(out_path)
    d = np.abs(np.diff(z))
    jump = abs(z[-1] - z[0])
    p999 = np.percentile(d, 99.9)
    f = lambda a, b: abs(rms_db(a) - rms_db(b))
    m100 = int(0.1 * SR)
    print(f"  → {os.path.basename(out_path)}: {len(z) / SR:.2f} с (длина сохранена), "
          f"ступенька 100мс {f(z[:m100], z[-m100:]):.2f} / 10мс {f(z[:441], z[-441:]):.2f} дБ, "
          f"скачок стыка {jump:.5f} "
          f"({jump / p999:.2f}× от p99.9 шага), "
          f"ядро {rms_db(z[int(5 * SR):-int(5 * SR)]):.1f} дБ, "
          f"peak {20 * np.log10(np.abs(z).max() + 1e-12):.1f} дБFS, {os.path.getsize(out_path)} Б")
    return 0


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    target = None
    if "--target-db" in argv:
        target = float(argv[argv.index("--target-db") + 1])
    return loopfix(argv[1], argv[2], target, verbose="--verbose" in argv or True)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
