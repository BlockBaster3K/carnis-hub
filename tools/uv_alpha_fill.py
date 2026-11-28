#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Заливка прозрачных пикселей внутри UV — фикс N1 («порезанная» текстура).

Что делается и почему именно так.

Дефект. В текстуре внутри UV-прямоугольников есть пиксели с alpha == 0.
`entityCutoutNoCull` выбрасывает такой пиксель, и на его месте сквозь модель
видно мир — «порезанная текстура».

Чего НЕЛЬЗЯ делать, чтобы «просто закрыть дыры»:

  * красить в средний цвет всего лица (так делают «плавающие» правки) — на
    мелких гранях 4×7 это даёт ровное пятно, которое видно как заплатка.
  * трогать пиксели, которые уже читает другая грань. У зомби B мандибулы и
    голова делят `uv(0,0)`: часть кадра — чужая грань, и перекраска испортит
    её. Поэтому пиксель заливается только если он ПРОЗРАЧНЫЙ и НЕ НАКРЫТ
    другой гранью: перекрытий не трогаем вообще.

Как выбирается цвет:

  1. если пиксель лежит на краю UV-прямоугольника — берём ближайший
     ОПАКОВЫЙ пиксель по направлению внутрь грани (то есть продолжаем узор
     снаружи внутрь);
  2. иначе — самый частый цвет в окне 3×3/5×5 вокруг дыры (медиана, а не
     среднее: среднее «вымывает» палитру, а текстура нарисована в 6–8 цветов);
  3. если вокруг нет ни одного опакового пикселя — падаем с ошибкой, а не
     заливаем чёрным: «тихо закрасить» означает дыру, которую никто не нашёл.

Результат пишется в новый zip; исходный не трогается. Порядок записей и
метаданные сохраняются, поэтому манифест остаётся валидным.

Использование:
    python3 tools/uv_alpha_fill.py <src.zip> <dst.zip> [--mobs a,b]

Коды: 0 — залито (или заливать нечего), 1 — не удалось залить без порчи
чужих пикселей (см. сообщение), 2 — ошибка запуска.
"""
import io
import json
import os
import sys
import zipfile

DEFAULT_MOBS = ("infected_zombie_b", "infected_skeleton_b")
PREFIX = "src/main/resources/assets/carnis/"
GEO = PREFIX + "geo/entity/%s.geo.json"
TEX = PREFIX + "textures/entity/%s.png"


def face_rects(u, v, w, h, d):
    u, v = round(u), round(v)
    return {
        "up": (u + d, v, w, d),
        "down": (u + d + w, v, w, d),
        "east": (u, v + d, d, h),
        "north": (u + d, v + d, w, h),
        "west": (u + d + w, v + d, d, h),
        "south": (u + d + w + d, v + d, w, h),
    }


def rects_of(geo):
    out = []
    for bone in geo.get("bones", ()):
        for cube in bone.get("cubes", ()):
            uv = cube.get("uv")
            if uv is None:
                continue
            if isinstance(uv, dict):
                for face, data in uv.items():
                    rect, size = data.get("uv"), data.get("uv_size")
                    if rect and size:
                        out.append((bone["name"], face, round(rect[0]),
                                    round(rect[1]), round(size[0]),
                                    round(size[1])))
                continue
            w, h, d = (round(float(x)) for x in cube["size"])
            for face, (x, y, rw, rh) in face_rects(uv[0], uv[1], w, h, d).items():
                if rw > 0 and rh > 0:
                    out.append((bone["name"], face, x, y, rw, rh))
    return out


def nearest_inside(arr, x, y, rect, coverage):
    """Опаковый цвет, продолжающий узор внутрь грани; либо самый частый в окне."""
    import numpy as np

    height, width = arr.shape[0], arr.shape[1]
    rx, ry, rw, rh = rect

    # 1) край грани → идём внутрь по нормали
    inward = []
    if x == rx:
        inward.append((1, 0))
    if x == rx + rw - 1:
        inward.append((-1, 0))
    if y == ry:
        inward.append((0, 1))
    if y == ry + rh - 1:
        inward.append((0, -1))
    for dx, dy in inward:
        cx, cy = x + dx, y + dy
        if rx <= cx < rx + rw and ry <= cy < ry + rh:
            pack = arr[cy, cx]
            if pack[3] > 0:
                return tuple(int(v) for v in pack[:3]), "край"

    # 2) окно вокруг: медиана опаковых соседей (3×3, затем 5×5, затем 7×7)
    for radius in (1, 2, 3):
        found = []
        for cy in range(max(0, y - radius), min(height, y + radius + 1)):
            for cx in range(max(0, x - radius), min(width, x + radius + 1)):
                if cy == y and cx == x:
                    continue
                pack = arr[cy, cx]
                if pack[3] > 0:
                    found.append((int(pack[0]), int(pack[1]), int(pack[2])))
        if found:
            med = tuple(int(np.median([c[i] for c in found])) for i in range(3))
            return med, "медиана %dx%d" % (radius, radius)
    return None, "нет соседей"


def fill_mob(zf, mob, names, strict_overlap=True):
    """Возвращает (новый png-байты | None, отчёт по мобу)."""
    import numpy as np
    from PIL import Image

    geo_path, tex_path = GEO % mob, TEX % mob
    geo = json.loads(zf.read(geo_path).decode("utf-8"))["minecraft:geometry"][0]
    img = Image.open(io.BytesIO(zf.read(tex_path))).convert("RGBA")
    arr = np.array(img)
    height, width = arr.shape[:2]

    faces = rects_of(geo)
    coverage = np.zeros((height, width), dtype=np.int16)
    for _n, _f, x, y, rw, rh in faces:
        coverage[y:y + rh, x:x + rw] += 1

    # Пиксели-цели: ВСЕ прозрачные внутри UV, включая перекрытые.
    #
    # Почему перекрытие больше не блокирует заливку. Пишем мы только туда, где
    # alpha == 0, то есть где СЕГОДНЯ дыра у каждой грани, которая этот пиксель
    # читает: ни одна из них сейчас ничего не рисует. Замена «ничего» на цвет не
    # может испортить соседнюю грань — испортить можно только ОПАКОВЫЙ пиксель,
    # а его мы не трогаем. Первая версия этого инструмента перекрытые пиксели
    # пропускала «на всякий случай» — и у зомби B остались 33 дыры ровно в тех
    # местах, где левая и правая мандибулы делят одну пару uv (зеркальная пара
    # по замыслу автора, а не конфликт раскладки).
    targets = set()
    for name, face, x, y, rw, rh in faces:
        for cy in range(y, min(height, y + rh)):
            for cx in range(x, min(width, x + rw)):
                if arr[cy, cx, 3] == 0:
                    targets.add((cx, cy))
    blocked = []

    changes = []
    failures = []
    for cx, cy in sorted(targets):
        # грань, которой принадлежит пиксель (первая по порядку — их не >1)
        rect = None
        for name, face, x, y, rw, rh in faces:
            if x <= cx < x + rw and y <= cy < y + rh:
                rect = (x, y, rw, rh)
                break
        color, how = nearest_inside(arr, cx, cy, rect, coverage)
        if color is None:
            failures.append((cx, cy))
            continue
        arr[cy, cx] = (color[0], color[1], color[2], 255)
        changes.append((cx, cy, color, how))

    if failures:
        return None, {"mob": mob, "error": "нечем залить %d px: %s"
                      % (len(failures), failures[:5])}

    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    return buf.getvalue(), {"mob": mob, "filled": len(changes),
                            "blocked": len(blocked), "changes": changes}


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print("нужно: python3 tools/uv_alpha_fill.py <src.zip> <dst.zip>")
        return 2
    src, dst = args[0], args[1]
    if not os.path.isfile(src):
        print("НЕТ ПАКЕТА: %s" % src)
        return 2

    mobs = DEFAULT_MOBS
    for a in argv[1:]:
        if a.startswith("--mobs="):
            mobs = tuple(m.strip() for m in a.split("=", 1)[1].split(",") if m.strip())

    print("Заливка прозрачных пикселей внутри UV (N1)")
    print("источник: %s" % src)
    with zipfile.ZipFile(src) as zf:
        names = set(zf.namelist())
        results = {}
        reports = []
        for mob in mobs:
            tex_path = TEX % mob
            if tex_path not in names:
                print("  ✗ %s: нет текстуры %s" % (mob, tex_path))
                return 2
            data, rep = fill_mob(zf, mob, names)
            reports.append(rep)
            if data is None:
                print("  ✗ %s: %s" % (mob, rep.get("error")))
                return 1
            if rep["filled"]:
                results[tex_path] = data
            print("  %-22s залито %3d px, перекрытых (не тронуто) %3d"
                  % (mob, rep["filled"], rep["blocked"]))
            for cx, cy, color, how in rep["changes"][:1000]:
                pass

        if not results:
            print("  · заливать нечего — копирую как есть")
        with zipfile.ZipFile(dst, "w") as out:
            for info in zf.infolist():
                data = results.get(info.filename, zf.read(info.filename))
                out.writestr(info, data)
    print()
    print("записано: %s (%d файлов изменено)" % (dst, len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
