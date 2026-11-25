#!/usr/bin/env python3
"""Разброс средних цветов вариантов ossified_flesh — метрика Д6 (волна 22)."""
import itertools, os, sys
from PIL import Image

THRESHOLD = 12.0

def mean_rgb(path):
    im = Image.open(path).convert("RGBA")
    opaque = [p for p in im.getdata() if p[3] == 255]
    if not opaque:
        raise SystemExit(f"{path}: нет непрозрачных пикселей")
    n = len(opaque)
    return tuple(sum(p[i] for p in opaque) / n for i in range(3)), n

def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    if os.path.isdir(d):
        files = [os.path.join(d, f) for f in sorted(os.listdir(d))
                 if f.endswith(".png") and "ossified_flesh" in f]
    else:
        files = [d]
    if len(files) < 2:
        raise SystemExit("нужно минимум 2 PNG с ossified_flesh")
    means = {}
    for f in files:
        m, n = mean_rgb(f)
        means[os.path.basename(f)] = m
        print(f"{os.path.basename(f):26s} средний RGB = "
              f"({m[0]:6.2f}, {m[1]:6.2f}, {m[2]:6.2f})  непрозрачных px: {n}")
    worst = (0.0, "")
    print()
    for a, b in itertools.combinations(sorted(means), 2):
        d_ = sum(abs(means[a][i] - means[b][i]) for i in range(3)) / 3.0
        print(f"пара {a} <-> {b}: {d_:6.2f}")
        if d_ > worst[0]:
            worst = (d_, f"{a} <-> {b}")
    print()
    print(f"РАЗБРОС = {worst[0]:.2f}   худшая пара: {worst[1]}")
    print("ИТОГ:", "СХОДИТСЯ" if worst[0] <= THRESHOLD else "ЕСТЬ ЗАМЕЧАНИЯ")
    return 0 if worst[0] <= THRESHOLD else 2

if __name__ == "__main__":
    sys.exit(main())
