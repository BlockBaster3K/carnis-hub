#!/usr/bin/env python3
"""Метрики OGG: RMS, peak, crest, спектральный центр, доля энергии < 80 / < 120 Гц, хвост.

Использование: python3 tools/sound_metrics.py <файл> [<файл> ...]
Пути — относительно /home/user/hub5/03-sound/sounds, если не абсолютные.
"""
import os
import sys

import numpy as np
import soundfile as sf

BANK = "/home/user/hub5/03-sound/sounds"


def analyze(path):
    x, sr = sf.read(path, dtype="float64", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    n = len(x)
    rms = float(np.sqrt(np.mean(x ** 2)))
    peak = float(np.max(np.abs(x)))
    crest = peak / rms if rms > 0 else 0.0

    # Спектральный центр и доли энергии (по мощности).
    win = 4096
    hop = 2048
    w = np.hanning(win)
    acc = np.zeros(win // 2 + 1)
    total = 0.0
    for start in range(0, max(1, n - win + 1), hop):
        seg = x[start:start + win]
        if len(seg) < win:
            break
        spec = np.abs(np.fft.rfft(seg * w)) ** 2
        acc += spec
        total += float(spec.sum())
    freqs = np.fft.rfftfreq(win, 1.0 / sr)
    if total > 0:
        centroid = float((freqs * acc).sum() / acc.sum())
        e80 = float(acc[freqs < 80].sum() / acc.sum())
        e120 = float(acc[freqs < 120].sum() / acc.sum())
    else:
        centroid = e80 = e120 = float("nan")

    # Хвост: доля времени в конце, где сигнал тише порога.
    thr = max(peak * 10 ** (-55 / 20), 1e-9)
    tail = 0
    for v in reversed(x):
        if abs(v) >= thr:
            break
        tail += 1
    return dict(dur=n / sr, rms=rms, peak=peak, crest=crest, centroid=centroid,
                e80=e80, e120=e120, tail_s=tail / sr, sr=sr)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    print(f"{'файл':34} {'длит.':>7} {'RMS':>8} {'peak':>8} {'crest':>7} "
          f"{'центр':>7} {'<80Гц':>7} {'<120Гц':>7} {'хвост':>7}")
    for a in sys.argv[1:]:
        p = a if os.path.isabs(a) else os.path.join(BANK, a)
        m = analyze(p)
        name = os.path.basename(p)
        print(f"{name:34} {m['dur']:6.3f}с {20*np.log10(m['rms']):7.2f} "
              f"{20*np.log10(m['peak']):7.2f} {m['crest']:6.1f} "
              f"{m['centroid']:6.0f}Гц {m['e80']*100:6.2f}% {m['e120']*100:6.2f}% "
              f"{m['tail_s']:6.2f}с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
