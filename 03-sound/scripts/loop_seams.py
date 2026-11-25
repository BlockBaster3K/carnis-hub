#!/usr/bin/env python3
"""Замер шва петли: как громко файл стыкуется сам с собой (T-3133).

Шов — разница уровней между концом и началом файла. Если петля склеена с
разрывом, в игре это слышно как щелчок раз в длину петли. Метод — как в
02-reviewer/timbre_methodology.md: окно 100 мс (критерий), 10-мс справочно,
PCM 44,1 кГц моно.

Дополнительно (сверх ТЗ) считается «энергия в шве»: RMS первого и последнего
10 мс окна относительно RMS всего файла. У разовых событий (удар, breathing)
края тихие по природе — для них шов бессмыслен, и это видно по числам.

CLI: python3 loop_seams.py <файл…>   → печатает таблицу, ничего не пишет
"""
import subprocess, sys, os
import numpy as np

SR = 44100
FF = os.environ.get('FFMPEG', 'ffmpeg')


def decode(path):
    out = subprocess.run([FF, '-v', 'quiet', '-i', path, '-f', 'f32le', '-ac', '1',
                          '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def rms_db(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)


def seam(y):
    m100, m10 = int(0.1 * SR), int(0.01 * SR)
    d = np.abs(np.diff(y))
    jump = abs(y[-1] - y[0])
    body = rms_db(y)
    return dict(
        seam100=abs(rms_db(y[:m100]) - rms_db(y[-m100:])),
        seam10=abs(rms_db(y[:m10]) - rms_db(y[-m10:])),
        jump=jump,
        jump_rel=jump / max(np.percentile(d, 99.9), 1e-12),
        edge_head=rms_db(y[:m10]) - body,
        edge_tail=rms_db(y[-m10:]) - body,
        dur=len(y) / SR,
    )


if __name__ == '__main__':
    files = sys.argv[1:]
    if not files:
        print(__doc__)
        sys.exit(1)
    print(f"{'файл':42s} {'длит':>7s} {'шов100':>7s} {'шов10':>7s} {'скачок':>8s} "
          f"{'край нач':>9s} {'край кон':>9s}  вердикт")
    bad = []
    for f in files:
        y = decode(f)
        s = seam(y)
        # петля = края не «в тишине»: и начало, и конец в пределах 20 дБ от тела
        is_loop = s['edge_head'] > -20 and s['edge_tail'] > -20
        verdict = ('ПЕТЛЯ, разрыв > 1 дБ' if s['seam100'] > 1.0 else 'петля, шов чист')
        if not is_loop:
            verdict = 'разовое событие (края в тишине)'
        elif s['seam100'] > 1.0:
            bad.append((f, s['seam100']))
        print(f"{os.path.basename(f)[:-4]:42s} {s['dur']:7.2f} {s['seam100']:7.2f} "
              f"{s['seam10']:7.2f} {s['jump_rel']:7.2f}× {s['edge_head']:+9.1f} "
              f"{s['edge_tail']:+9.1f}  {verdict}")
    print(f"\nразрывов > 1 дБ: {len(bad)}")
    for f, v in bad:
        print(f"  {f} — {v:.2f} дБ")
