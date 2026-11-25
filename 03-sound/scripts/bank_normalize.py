#!/usr/bin/env python3
"""Нормализация пиков банка до нормы «peak ≤ −1 dBFS» (подготовлено, НЕ применено).

Задача-кандидат из T-3113 §2.2: 7 файлов имеют peak −0.77…−0.97 dBFS при норме
≤ −1 dBFS. В игре это не клиппит (громкость задаётся в sounds.json), но норму
банка нарушает. Правка — чистый сдвиг усиления: crest не меняется, форма не
меняется, длина не меняется.

CLI:
  python3 bank_normalize.py --dry <файл…>      # только показать, ничего не писать
  python3 bank_normalize.py --apply <файл…>    # записать (нужна санкция Архитектора)
  python3 bank_normalize.py --apply --out DIR <файл…>   # писать в другой каталог

Целевой пик −1.05 dBFS: 0.05 дБ запаса, чтобы после повторного кодирования
Vorbis пик не вылез обратно выше −1.00.
"""
import os, struct, subprocess, sys
import numpy as np

SR = 44100
FF = os.environ.get('FFMPEG', 'ffmpeg')
TARGET = -1.05


def decode(path):
    out = subprocess.run([FF, '-v', 'quiet', '-i', path, '-f', 'f32le', '-ac', '1',
                          '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def vorbis_bitrate(path):
    d = open(path, 'rb').read()
    i = d.find(b'\x01vorbis')
    return struct.unpack('<i', d[i + 20:i + 24])[0] // 1000


def db(x):
    return 20 * np.log10(x + 1e-12)


def normalise(path, out_path, target=TARGET):
    y = decode(path)
    pk = float(np.abs(y).max())
    pk_db = db(pk)
    if pk_db <= -1.0:
        return None                      # уже в норме, не трогаем
    g = 10 ** ((target - pk_db) / 20.0)
    z = y * g
    br = vorbis_bitrate(path)
    subprocess.run([FF, '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1',
                    '-i', '-', '-c:a', 'libvorbis', '-b:a', f'{br}k', out_path],
                   input=z.astype(np.float32).tobytes(), check=True)
    # контроль после кодирования
    z2 = decode(out_path)
    return dict(before=pk_db, after=db(float(np.abs(z2).max())),
                gain=db(g), dur_ok=abs(len(z2) - len(y)) <= 2,
                size=os.path.getsize(out_path))


if __name__ == '__main__':
    a = sys.argv[1:]
    apply = '--apply' in a
    out_dir = None
    if '--out' in a:
        out_dir = a[a.index('--out') + 1]
        a = [x for x in a if x not in ('--out', out_dir)]
    files = [x for x in a if not x.startswith('--')]
    if not files:
        print(__doc__)
        sys.exit(1)
    changed = 0
    for f in files:
        if apply:
            dst = os.path.join(out_dir, os.path.basename(f)) if out_dir else f
            r = normalise(f, dst)
            if r is None:
                print(f"{f:48s} уже в норме — не тронут")
            else:
                changed += 1
                print(f"{f:48s} {r['before']:6.2f} → {r['after']:6.2f} dBFS  {r['gain']:+.2f} дБ  "
                      f"длина ок: {r['dur_ok']}")
        else:
            y = decode(f)
            pk = db(float(np.abs(y).max()))
            if pk <= -1.0:
                print(f"{f:48s} {pk:6.2f} dBFS — уже в норме")
            else:
                print(f"{f:48s} {pk:6.2f} → {TARGET:6.2f} dBFS  сдвиг {TARGET - pk:+.2f} дБ  "
                      f"(crest и форма не меняются)")
                changed += 1
    print(f"\n{'ГОТОВО К ПРАВКЕ' if apply else 'ТРЕБУЕТ ПРАВКИ'}: {changed} файлов")
