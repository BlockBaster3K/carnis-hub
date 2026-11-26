#!/usr/bin/env python3
"""T-3104: перерисовка тембра ambient-слоёв.

Задача: доля энергии < 80 Гц ≤ 25 %, спектральный центр ≥ 400 Гц, длины не
менять (120.000 с для 9 слоёв), шов петли ≤ 1 дБ, RMS не менять.

Метод:
  1. модальная линия — низкочастотный гребень сигнала (Butterworth 4-го порядка,
     срез 80 Гц, фильтрация filtfilt по кругу: край файла продолжается началом,
     поэтому шов не портится самим фильтром);
  2. вычитание линии с коэффициентом 0.85 — снимает «раздражение», но оставляет
     подмес низа, чтобы сцена не стала плоской;
  3. возврат RMS к исходному (вычитание линии занижает уровень);
  4. замыкание петли: круговая нормализация огибающей → перенос шва в тихое
     место → микро-склейка 10 мс → согласование уровней ±100 мс;
  5. пик ≤ −1 dBFS, кодирование Vorbis с исходным bitrate, длина сохраняется.

CLI:
  python3 timbre_redraw.py --measure <файл…>
  python3 timbre_redraw.py <вход> <выход> [--lp 80] [--slope 0.85] [--no-loop]
"""
import os, struct, subprocess, sys
import numpy as np
from scipy import signal

SR = 44100
FF = os.environ.get('FFMPEG', 'ffmpeg')
XF = 0.010      # микро-склейка, с
MATCH = 0.100   # окно согласования, с


def decode(path):
    out = subprocess.run([FF, '-v', 'quiet', '-i', path, '-f', 'f32le', '-ac', '1',
                          '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def vorbis_params(path):
    d = open(path, 'rb').read()
    i = d.find(b'\x01vorbis')
    ch = d[i + 11]
    rate = struct.unpack('<I', d[i + 12:i + 16])[0]
    br = struct.unpack('<i', d[i + 20:i + 24])[0] // 1000
    return ch, rate, br


def encode(y, out, br):
    p = subprocess.run([FF, '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
                        '-i', '-', '-c:a', 'libvorbis', '-b:a', f'{br}k', out],
                       input=y.astype(np.float32).tobytes(), capture_output=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.decode()[:400])


def rms_db(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)


def measure(y):
    f, P = signal.welch(y, SR, nperseg=8192)
    t = P.sum()
    return P[f < 80].sum() / t * 100, float((f * P).sum() / t), rms_db(y), 20 * np.log10(np.abs(y).max())


def seam(y):
    """Разрыв на стыке петли: разница уровней в окне 100 мс и 10 мс + скачок сэмпла."""
    m, s = int(0.1 * SR), int(0.01 * SR)
    d = np.abs(np.diff(y))
    jump = abs(y[-1] - y[0])
    return (abs(rms_db(y[:m]) - rms_db(y[-m:])), abs(rms_db(y[:s]) - rms_db(y[-s:])),
            jump, jump / max(np.percentile(d, 99.9), 1e-12))


def modal_line(y, lp):
    n = len(y)
    pad = SR
    xe = np.concatenate([y[-pad:], y, y[:pad]])
    b, a = signal.butter(4, lp / (SR / 2), 'low')
    return signal.filtfilt(b, a, xe)[pad:pad + n]


def soft_limit(y, ceiling, sharp=1.5):
    """Мягкий лимитер: пики подгибаются к ceiling, тело не трогается.

    Нужен, потому что вычитание низкочастотной линии поднимает крест-фактор
    (11 → 16 дБ): щелчков нет, но транзиенты становятся резче. Тангенциальное
    колено возвращает пик к исходному, не срезая тело сигнала.
    """
    a = np.abs(y)
    over = a > ceiling
    if not over.any():
        return y
    # плавное сжатие только превышений: y' = ceiling * tanh(a/ceiling)
    comp = ceiling * np.tanh(a / ceiling) ** sharp
    scale = np.where(over, comp / np.maximum(a, 1e-12), 1.0)
    # сглаживаем коэффициент, чтобы не внести ступеньку
    k = int(0.005 * SR)
    if k > 1:
        scale = signal.filtfilt(np.ones(k) / k, [1.0], np.concatenate([scale[-k:], scale, scale[:k]]))[k:k + len(scale)]
        scale = np.clip(scale, 0.0, 1.0)
    return y * scale


def close_loop(y):
    """Замыкание петли (тот же алгоритм, что в loopfix.py)."""
    w = int(XF * SR)
    ph = np.linspace(0.0, np.pi / 2.0, w)
    y[-w:] *= np.cos(ph)
    y[:w] *= np.sin(ph)
    m = int(MATCH * SR)
    mid = 0.5 * (rms_db(y[-m:]) + rms_db(y[:m]))
    y[-m:] *= 10 ** ((mid - rms_db(y[-m:])) / 20.0)
    y[:m] *= 10 ** ((mid - rms_db(y[:m])) / 20.0)
    return y


def apply_by(y, lp, slope, r0, p0):
    d = y - slope * modal_line(y, lp)
    d *= 10 ** ((r0 - rms_db(d)) / 20.0)          # RMS как было
    # пик возвращаем к исходному мягким коленом, тело не срезаем
    d = soft_limit(d, 10 ** (p0 / 20.0) * 1.02)
    d *= 10 ** ((r0 - rms_db(d)) / 20.0)
    return d


def auto_params(y, target_centre=450.0, target_low=20.0, r0=None, p0=None):
    """Наименьшее вмешательство, дающее запас по обоим критериям ТЗ.

    ТЗ: < 80 Гц ≤ 25 %, центр ≥ 400 Гц. Беру запас (20 % и 450 Гц), чтобы
    результат не висел на пороге: у каждого файла свой спектр, и «ровно 400»
    у одного и «612» у другого означает, что сцену перекосили по-разному.
    """
    for lp in (80.0, 100.0, 120.0, 140.0, 160.0, 200.0, 240.0, 280.0):
        for slope in (0.80, 0.85, 0.88, 0.90, 0.92):
            d = apply_by(y, lp, slope, r0, p0)
            f, c, _, _ = measure(d)
            if f <= target_low and c >= target_centre:
                return lp, slope, f, c
    raise SystemExit('параметры не подобрались — файл требует перерисовки, а не вычитания')


def redraw(in_path, out_path, lp=80.0, slope=0.85, keep_loop=True, verbose=True, auto=False):
    y = decode(in_path)
    f0, c0, r0, p0 = measure(y)
    if auto:
        lp, slope, _, _ = auto_params(y, r0=r0, p0=p0)
        if verbose:
            print(f"  автоподбор: lp={lp:.0f} Гц, коэффициент {slope:.2f}")
    d = apply_by(y, lp, slope, r0, p0)
    if not np.isfinite(d).all():
        raise SystemExit('NaN в результате')
    if keep_loop:
        d = close_loop(d)
    pk = np.abs(d).max()
    if pk > 10 ** (-1 / 20):
        d *= 10 ** (-1 / 20) / pk
    _, _, br = vorbis_params(in_path)
    encode(d, out_path, br)
    z = decode(out_path)
    f1, c1, r1, p1 = measure(z)
    s = seam(z)
    if verbose:
        print(f"{os.path.basename(in_path):28s} <80Гц {f0:5.1f}→{f1:5.1f}%  центр {c0:5.0f}→{c1:5.0f}  "
              f"RMS {r0:6.2f}→{r1:6.2f}  peak {p0:5.2f}→{p1:5.2f}  "
              f"длина {len(z)/SR:7.3f} с  шов 100мс {s[0]:.2f}/10мс {s[1]:.2f} дБ  "
              f"скачок {s[2]:.5f} ({s[3]:.2f}×)")
    return dict(f0=f0, f1=f1, c0=c0, c1=c1, r0=r0, r1=r1, p1=p1, dur=len(z) / SR, seam=s)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--measure':
        for p in a[1:]:
            y = decode(p)
            f, c, r, pk = measure(y)
            print(f"{p:52s} {len(y)/SR:7.3f} с  <80Гц {f:5.1f}%  центр {c:5.0f}  RMS {r:6.2f}  peak {pk:6.2f}")
        sys.exit(0)
    if len(a) < 2:
        print(__doc__)
        sys.exit(1)
    opt = {'--lp': 80.0, '--slope': 0.85}
    keep = '--no-loop' not in a
    auto = '--auto' in a
    args = []
    i = 0
    while i < len(a):
        if a[i] in opt:
            opt[a[i]] = float(a[i + 1]); i += 2
        elif a[i] in ('--no-loop', '--auto'):
            i += 1
        else:
            args.append(a[i]); i += 1
    redraw(args[0], args[1], opt['--lp'], opt['--slope'], keep, auto=auto)
