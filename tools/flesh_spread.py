#!/usr/bin/env python3
"""Разброс средних цветов вариантов ossified_flesh — метрика Д6 (волна 22)."""
import hashlib, itertools, os, sys, warnings
from PIL import Image

# Pillow 13 помечает getdata() устаревшим, но текст скрипта утверждён заказчиком;
# предупреждение глушим, чтобы не засорять вывод проверки.
warnings.filterwarnings("ignore", category=DeprecationWarning)

THRESHOLD = 12.0

def mean_rgb(path):
    im = Image.open(path).convert("RGBA")
    opaque = [p for p in im.getdata() if p[3] == 255]
    if not opaque:
        raise SystemExit(f"{path}: нет непрозрачных пикселей")
    n = len(opaque)
    return tuple(sum(p[i] for p in opaque) / n for i in range(3)), n

def pixel_diff(a, b):
    ia = Image.open(a).convert("RGBA").getdata()
    ib = Image.open(b).convert("RGBA").getdata()
    pa, pb = list(ia), list(ib)
    n = min(len(pa), len(pb))
    return sum(1 for i in range(n) if pa[i] != pb[i]) / n

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
    for f in sorted(files):
        h = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
        print(f"SHA-256 {f}: {h}")
    identical = False
    for a, b in itertools.combinations(files, 2):
        share = pixel_diff(a, b)
        print(f"различие пикселей {os.path.basename(a)} <-> {os.path.basename(b)}: {share*100:.2f} %")
        if share == 0.0:
            identical = True
    if identical:
        print("ВНИМАНИЕ: есть пара побайтово идентичных файлов — варианты не различаются")
    print()
    print(f"РАЗБРОС = {worst[0]:.2f}   худшая пара: {worst[1]}")
    ok = worst[0] <= THRESHOLD and not identical
    print("ИТОГ:", "СХОДИТСЯ" if ok else "ЕСТЬ ЗАМЕЧАНИЯ")
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
