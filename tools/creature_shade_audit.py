#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""creature_shade_audit.py — ревизия плотности светотени по всем существам (T-3114).

Обёртка над чекером Художника `04-artist/tools/shade_density.py`: правила
(доля самой частой непрозрачной краски, число цветов) не дублируются —
импортируется его функция `check_image`. Скрипт только обходит все текстуры
существ и печатает сводную таблицу, отсортированную по доле.

    python3 tools/creature_shade_audit.py [каталог|zip пакета] [--include-glowmask]
                                          [--max-share 0.35] [--min-colors 7]
                                          [--tex-dir textures/block]

`--tex-dir` переключает набор: по умолчанию `textures/entity` (существа),
`textures/block` — текстуры блоков (T-3131). Правила те же, чекер тот же.

Вход — **каталог пакета или ZIP-пакет**: гейты работают с ZIP, и раньше инструмент
на ZIP отвечал ошибкой (T-3159, п.3 — проверка инструмента на 3.7.1/3.6.0-R).
По умолчанию каталог — `01-coder/3.7.0`, сканируется
`src/main/resources/assets/carnis/textures/entity/*.png`.

Коды возврата: 0 — все тела ≤ порога, 2 — есть тела с долей > порога,
1 — ошибка запуска (нет каталога, нет PIL, нет чекера Художника).
"""
import argparse
import importlib.util
import io
import os
import sys
import zipfile
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = "01-coder/3.7.0"
ARTIST_CHECKER = Path("04-artist/tools/shade_density.py")


def load_artist_checker():
    """Подтягиваем правила Художника, а не свои: один источник правды."""
    if not ARTIST_CHECKER.exists():
        print("ОШИБКА: нет чекера Художника %s (T-3109)" % ARTIST_CHECKER)
        return None
    spec = importlib.util.spec_from_file_location("shade_density", ARTIST_CHECKER)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        print("ОШИБКА: чекер Художника не загрузился: %s" % exc)
        return None
    return mod


def main():
    ap = argparse.ArgumentParser(description="Ревизия плотности светотени по существам (T-3114)")
    ap.add_argument("root", nargs="?", default=DEFAULT_ROOT, help="каталог пакета (по умолч. %s)" % DEFAULT_ROOT)
    ap.add_argument("--include-glowmask", action="store_true", help="включить *_glowmask.png")
    ap.add_argument("--max-share", type=float, default=0.35)
    ap.add_argument("--min-colors", type=int, default=7)
    ap.add_argument("--tex-dir", default="textures/entity",
                    help="каталог внутри assets/carnis (по умолч. textures/entity)")
    a = ap.parse_args()

    mod = load_artist_checker()
    if mod is None:
        return 1
    try:
        from PIL import Image
    except ImportError:
        print("ОШИБКА: нужен Pillow (python3 -m pip install pillow)")
        return 1

    inner = "src/main/resources/assets/carnis/" + a.tex_dir
    is_zip = os.path.isfile(a.root) and zipfile.is_zipfile(a.root)
    if is_zip:
        with zipfile.ZipFile(a.root) as z:
            members = sorted(n for n in z.namelist()
                             if n.startswith(inner + "/") and n.lower().endswith(".png"))
            if not a.include_glowmask:
                members = [n for n in members if "_glowmask" not in n.rsplit("/", 1)[-1].lower()]
            if not members:
                print("ОШИБКА: в %s нет подходящих PNG (%s)" % (a.root, inner))
                return 1
            files = [(n, z.read(n)) for n in members]
        src_label = "%s (%s)" % (a.root, inner)
        names = [n.rsplit("/", 1)[-1] for n, _ in files]
    else:
        ent = Path(a.root) / inner
        if not ent.is_dir():
            print("ОШИБКА: нет каталога текстур %s (ни каталог, ни ZIP): %s" % (a.tex_dir, ent))
            return 1
        paths = sorted(p for p in ent.glob("*.png")
                       if a.include_glowmask or "_glowmask" not in p.name.lower())
        if not paths:
            print("ОШИБКА: в %s нет подходящих PNG" % ent)
            return 1
        files = [(p.name, p.read_bytes()) for p in paths]
        src_label = str(ent)
        names = [p.name for p in paths]

    rows = []
    for name, blob in files:
        try:
            im = Image.open(io.BytesIO(blob) if is_zip else name)
            rgba = im.convert("RGBA")
            px = [q[:3] for q in rgba.getdata() if q[3] > 0]
            if not px:
                rows.append((name, 0, 0.0, None, False))
                continue
            cnt = Counter(px)
            top_col, top_n = cnt.most_common(1)[0]
            share = top_n / len(px)
            ok = share <= a.max_share and len(cnt) >= a.min_colors
            rows.append((name, len(cnt), share, top_col, ok))
        except Exception as exc:
            print("ОШИБКА: %s не прочитан: %s" % (name, exc))
            return 1

    subject = "существ" if a.tex_dir.endswith("entity") else "блоков"
    print("Ревизия светотени %s" % subject)
    print("Источник: %s" % src_label)
    print("Правила чекера Художника %s: доля одной краски ≤ %.0f %%, цветов ≥ %d"
          % (ARTIST_CHECKER, a.max_share * 100, a.min_colors))
    print()
    print("%-30s %7s %9s  %-16s %s" % ("текстура", "цветов", "доля", "краска", "вывод"))
    print("-" * 80)
    bad = []
    for name, ncol, share, top, ok in sorted(rows, key=lambda r: -r[2]):
        col = "—" if top is None else "#%02X%02X%02X" % top
        verdict = "OK" if ok else "ВЫШЕ ПОРОГА"
        print("%-30s %7d %8.1f%%  %-16s %s" % (name, ncol, share * 100, col, verdict))
        if not ok:
            bad.append((name, share, ncol))
    print("-" * 80)
    print("Текстур проверено: %d" % len(rows))
    if bad:
        print("ИТОГ: ВЫШЕ ПОРОГА — %d" % len(bad))
        for name, share, ncol in bad:
            print("  %-30s %.1f %% (цветов %d)" % (name, share * 100, ncol))
        return 2
    print("ИТОГ: ВСЕ В НОРМЕ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
