#!/usr/bin/env python3
"""Чекер плотности светотени (T-3109): доля самой частой непрозрачной краски и число цветов.

Коды возврата:
  0 — все проверенные текстуры укладываются в пороги
  2 — есть замечания (доля > max_share или цветов < min_colors)
  1 — ошибка запуска
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image


def check_image(im: Image.Image, name: str, max_share: float, min_colors: int) -> tuple[bool, str]:
    rgba = im.convert("RGBA")
    px = [p[:3] for p in rgba.getdata() if p[3] > 0]
    if not px:
        return False, f"  {name:36s} 0 непрозрачных пикселей"
    cnt = Counter(px)
    top_col, top_n = cnt.most_common(1)[0]
    share = top_n / len(px)
    n_colors = len(cnt)
    ok = (share <= max_share) and (n_colors >= min_colors)
    status = "OK" if ok else "ЗАМЕЧАНИЕ"
    return ok, (
        f"  {name:36s} цветов={n_colors:2d}  "
        f"топ={top_col} {top_n}/{len(px)} ({share * 100:5.1f}%)  {status}"
    )


def print_recipe(im: Image.Image, name: str) -> None:
    rgba = im.convert("RGBA")
    px = [p[:3] for p in rgba.getdata() if p[3] > 0]
    if not px:
        return
    mr = sum(p[0] for p in px) / len(px)
    mg = sum(p[1] for p in px) / len(px)
    mb = sum(p[2] for p in px) / len(px)
    clamp = lambda v: max(0, min(255, int(round(v))))
    ramp = [(clamp(mr + d), clamp(mg + d * 0.7), clamp(mb + d * 0.7)) for d in (-30, -20, -10, 0, 10, 20, 30)]
    print(f"    РЕЦЕПТ {name}: средний=({mr:.1f},{mg:.1f},{mb:.1f}) -> 7 квантилей по ~{100/7:.1f}%: {ramp}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Чекер плотности светотени (T-3109)")
    ap.add_argument("target", help="Путь к PNG или ZIP")
    ap.add_argument("--max-share", type=float, default=0.35, help="Макс. доля одной краски (по умолч. 0.35)")
    ap.add_argument("--min-colors", type=int, default=7, help="Мин. число непрозрачных цветов (по умолч. 7)")
    ap.add_argument("--include-glowmask", action="store_true", help="Проверять также *_glowmask.png")
    ap.add_argument("--recipe", action="store_true", help="Печатать рецепт перекраски для текстур вне порога")
    args = ap.parse_args()

    p = Path(args.target)
    if not p.exists():
        print(f"ОШИБКА: не найден {p}", file=sys.stderr)
        return 1

    all_ok = True
    try:
        if p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p, "r") as zf:
                names = sorted(
                    n for n in zf.namelist()
                    if n.lower().endswith(".png")
                    and (args.include_glowmask or "_glowmask" not in n.lower())
                )
                if not names:
                    print("ОШИБКА: в архиве нет подходящих PNG", file=sys.stderr)
                    return 1
                for n in names:
                    im = Image.open(io.BytesIO(zf.read(n)))
                    ok, line = check_image(im, Path(n).name, args.max_share, args.min_colors)
                    print(line)
                    if not ok:
                        all_ok = False
                        if args.recipe:
                            print_recipe(im, Path(n).name)
        else:
            im = Image.open(p)
            ok, line = check_image(im, p.name, args.max_share, args.min_colors)
            print(line)
            if not ok:
                all_ok = False
                if args.recipe:
                    print_recipe(im, p.name)
    except Exception as exc:
        print(f"ОШИБКА: {exc}", file=sys.stderr)
        return 1

    print("ИТОГ:", "СХОДИТСЯ" if all_ok else "ЕСТЬ ЗАМЕЧАНИЯ")
    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
