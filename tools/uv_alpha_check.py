#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UV-прозрачность: в UV-прямоугольниках модели не должно быть дыр.

Почему это отдельная проверка, а не «глазами в игре».

Bedrock-модель описывает куб одной парой `uv` — из неё выводятся шесть
прямоугольников (up/down/east/north/west/south). Если в текстуре внутри любого
из этих прямоугольников alpha == 0, рендер (`entityCutoutNoCull`) выбрасывает
пиксель целиком: на его месте видно то, что за моделью. Для игрока это
выглядит как «текстура порезанная, через неё видно всё насквозь» — ровно как
дефект N1 в 3.8.1.

Дыры бывают двух разных природ:

    1. **в текстуре** — автор нарисовал `alpha 0` внутри UV. Лечится заливкой
       (инструмент `tools/uv_alpha_fill.py`), проверка ниже это стережёт;
    2. **в UV-раскладке** — два куба делят одну пару `uv`, и их прямоугольники
       не совпадают. Тогда «дыра» появляется не потому, что прозрачно, а
       потому, что грань читает пиксели соседней грани (или пустой угол).
       Заливка тут помогает только если целевой пиксель вообще не занят другой
       гранью; иначе правка одной грани портит другую. Поэтому проверка
       печатает и наложения UV — по ним видно, безопасна ли заливка.

Смысл fail-closed: проверка возвращает 1 при ЛЮБОЙ дыре внутри UV, даже если
её закрывает вторая грань (наложение). «Дыр нет ни у одной грани» — только
тогда 0.

Использование:
    python3 tools/uv_alpha_check.py <пакет.zip> [--mobs a,b,c] [--quiet]

Коды: 0 — дыр в UV нет, 1 — есть (или пакет/модель не читаются), 2 — ошибка
запуска (нет пакета).
"""
import io
import json
import os
import sys
import zipfile

# Все пары «модель -> текстура», которые игра реально грузит: 4 моба × 2
# варианта. Список тот же, что у блока E приёмки (`_b`-наборы) плюс A-наборы,
# потому что A — не «эталон по умолчанию», у него свои дыры (в 3.8.1 A чист).
DEFAULT_MOBS = (
    "infected_zombie", "infected_zombie_b",
    "infected_skeleton", "infected_skeleton_b",
    "infected_creeper", "infected_creeper_b",
    "infected_spider", "infected_spider_b",
)

PREFIX = "src/main/resources/assets/carnis/"
GEO = PREFIX + "geo/entity/%s.geo.json"
TEX = PREFIX + "textures/entity/%s.png"


def face_rects(u, v, w, h, d):
    """Шесть UV-прямоугольников куба — как в Bedrock/GeckoLib box UV."""
    u, v = round(u), round(v)
    return {
        "up": (u + d, v, w, d),
        "down": (u + d + w, v, w, d),
        "east": (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "west": (u + d + w, v + d, d, h),
        "south": (u + d + w + d, v + d, w, h),
    }


def iter_cube_faces(geometry):
    """Все (кость, грань, x, y, w, h) для кубов с list-формой uv.

    Куб с dict-формой uv (`{"north": {"uv": [...], "uv_size": [...]}}`) несёт
    прямоугольники явно — их берём как есть. Куб без uv не рендерится и дыр не
    даёт.
    """
    for bone in geometry.get("bones", ()):
        for cube in bone.get("cubes", ()):
            uv = cube.get("uv")
            if uv is None:
                continue
            if isinstance(uv, dict):
                for face, data in uv.items():
                    rect = data.get("uv")
                    size = data.get("uv_size")
                    if not rect or not size:
                        continue
                    yield (bone["name"], face, round(rect[0]), round(rect[1]),
                           round(size[0]), round(size[1]))
                continue
            w, h, d = (round(float(x)) for x in cube["size"])
            for face, (x, y, rw, rh) in face_rects(uv[0], uv[1], w, h, d).items():
                if rw > 0 and rh > 0:
                    yield (bone["name"], face, x, y, rw, rh)


def analyse(zf, mob, names):
    """Возвращает (проблемы, сведения) по одному мобу."""
    import numpy as np
    from PIL import Image

    geo_path, tex_path = GEO % mob, TEX % mob
    if geo_path not in names or tex_path not in names:
        return ["%s: нет %s в пакете" % (mob, geo_path if geo_path not in names
                                        else tex_path)], None
    geo = json.loads(zf.read(geo_path).decode("utf-8"))["minecraft:geometry"][0]
    img = Image.open(io.BytesIO(zf.read(tex_path))).convert("RGBA")
    arr = np.array(img)
    height, width = arr.shape[0], arr.shape[1]

    faces = list(iter_cube_faces(geo))
    if not faces:
        return [], {"mob": mob, "faces": 0, "uv": 0, "holes": 0,
                    "overlap": 0, "detail": []}

    coverage = np.zeros((height, width), dtype=np.int16)
    for _name, _face, x, y, rw, rh in faces:
        coverage[y:y + rh, x:x + rw] += 1

    holes = []
    total_holes = 0
    for name, face, x, y, rw, rh in faces:
        if x + rw > width or y + rh > height:
            holes.append((name, face, x, y, rw, rh, -1, "за пределами текстуры"))
            total_holes += 1
            continue
        alpha = arr[y:y + rh, x:x + rw, 3]
        clear = int((alpha == 0).sum())
        if clear:
            overlap = int((coverage[y:y + rh, x:x + rw] > 1).sum())
            holes.append((name, face, x, y, rw, rh, clear, overlap))
            total_holes += clear

    uv_area = int((coverage > 0).sum())
    overlap_area = int((coverage > 1).sum())
    return (["%s: %d прозрачных px внутри UV" % (mob, total_holes)]
            if total_holes else []), {
        "mob": mob, "faces": len(faces), "uv": uv_area,
        "holes": total_holes, "overlap": overlap_area, "detail": holes,
    }


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in argv
    if not args:
        print("нужен путь к пакету: python3 tools/uv_alpha_check.py <pkg.zip>")
        return 2
    pkg = args[0]
    if not os.path.isfile(pkg):
        print("НЕТ ПАКЕТА: %s" % pkg)
        return 2

    mobs = DEFAULT_MOBS
    for a in argv[1:]:
        if a.startswith("--mobs="):
            mobs = tuple(m.strip() for m in a.split("=", 1)[1].split(",") if m.strip())

    print("UV-прозрачность: дыры внутри UV-прямоугольников модели")
    print("пакет: %s" % pkg)
    problems = []
    with zipfile.ZipFile(pkg) as zf:
        names = set(zf.namelist())
        for mob in mobs:
            mob_problems, info = analyse(zf, mob, names)
            problems += mob_problems
            if info is None:
                continue
            if not quiet or info["holes"]:
                status = "OK" if not info["holes"] else "ДЫРЫ"
                print("  [%-5s] %-22s граней %3d, UV %4d px, дыр %4d, "
                      "наложений UV %4d" % (status, info["mob"], info["faces"],
                                            info["uv"], info["holes"],
                                            info["overlap"]))
            if info["holes"] and not quiet:
                for name, face, x, y, rw, rh, clear, overlap in info["detail"]:
                    if clear == -1:
                        print("           %-18s %-6s uv(%d,%d) %dx%d — %s"
                              % (name, face, x, y, rw, rh, overlap))
                        continue
                    level = "наложение UV" if overlap else "чисто"
                    print("           %-18s %-6s uv(%d,%d) %dx%d — %d px, %s"
                          % (name, face, x, y, rw, rh, clear, level))
    print()
    if problems:
        print("ИТОГ: ЕСТЬ ДЫРЫ — %d" % len(problems))
        for p in problems:
            print("  · %s" % p)
        return 1
    print("ИТОГ: дыр в UV нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
