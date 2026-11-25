#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""creature_pack_audit.py — независимая проверка сдачи существ (geo + текстура + glowmask).

Зачем: с 3.8.0 Художник сдаёт существ пачками (`Carnis_3.8.0_*.zip`), а проверять
их до сборки пакета нечем: гейт 3.7.3 смотрит пакет, в котором этих файлов ещё
нет, `glowmask_r3_check.py` смотрит только маски и только при наличии тела рядом,
`shade_density.py` — только плотность светотени. Этот чекер собирает все сдачи в
один набор и проверяет существо целиком (ROADMAP R10/R14).

Проверяется по каждому существу:
  1. geo разбирается; есть `minecraft:geometry[0].bones`; у каждой кости есть
     `pivot`; имена костей уникальны;
  2. UV кубов не выходят за размер текстуры (u+size.x, v+size.y+size.z);
  3. текстура по нормам A3R1: >= 7 непрозрачных цветов, топ-доля <= 35 %,
     альфа только {0,255};
  4. glowmask по правилу Р-3: файл есть, размер == текстурe, ровно один
     непрозрачный цвет (255,92,57), альфа бинарная, свечения вне силуэта 0 px;
  5. анимации (если сданы): каждое имя кости из `bones` существует в geo;
     отмечено наличие idle/walk/attack/hurt/death;
  6. число костей (для H-блока) — в таблицу, с порогом `--min-bones`.

Использование:
    python3 02-reviewer/tools/creature_pack_audit.py <zip|dir> [<zip|dir> ...] \\
            [--min-bones 12] [--only имя,имя]

Код возврата: 0 — всё в норме, 2 — есть замечания, 1 — ошибка запуска.
"""

import argparse
import io
import json
import os
import sys
import zipfile
from collections import Counter

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("ОШИБКА: нужен Pillow")
    sys.exit(1)

GLOW = (255, 92, 57)
REQUIRED_ANIMS = ("idle", "walk", "attack", "hurt", "death")


def iter_files(sources):
    """{относительный путь внутри assets/carnis: bytes} по всем источникам."""
    out = {}
    for src in sources:
        if zipfile.is_zipfile(src):
            with zipfile.ZipFile(src) as z:
                for n in z.namelist():
                    if n.endswith("/"):
                        continue
                    key = n.split("assets/carnis/", 1)[-1]
                    out.setdefault(key, z.read(n))
        elif os.path.isdir(src):
            for dp, _, fs in os.walk(src):
                for f in fs:
                    full = os.path.join(dp, f)
                    rel = os.path.relpath(full, src).replace(os.sep, "/")
                    key = rel.split("assets/carnis/", 1)[-1]
                    with open(full, "rb") as fh:
                        out.setdefault(key, fh.read())
    return out


def png_stats(data):
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    px = list(im.get_flattened_data())
    opaque = [c for c in px if c[3] > 0]
    cnt = Counter((c[0], c[1], c[2]) for c in opaque)
    top = cnt.most_common(1)[0] if cnt else ((0, 0, 0), 0)
    return {
        "size": im.size,
        "im": im,
        "opaque": len(opaque),
        "colors": len(cnt),
        "top_share": (top[1] / len(opaque)) if opaque else 0.0,
        "alphas": {c[3] for c in px},
        "rgb_opaque": set(cnt),
    }


def geo_info(data):
    g = json.loads(data.decode("utf-8"))
    geos = g.get("minecraft:geometry")
    if not geos:
        raise ValueError("нет minecraft:geometry")
    geo = geos[0]
    bones = geo.get("bones") or []
    names = [b.get("name") for b in bones]
    problems = []
    if len(names) != len(set(names)):
        problems.append("имена костей повторяются")
    for b in bones:
        if "pivot" not in b:
            problems.append("кость без pivot: %s" % b.get("name"))
    uv_max_u = uv_max_v = 0
    for b in bones:
        for c in b.get("cubes", []) or []:
            uv = c.get("uv")
            size = c.get("size") or [0, 0, 0]
            if uv and len(uv) == 2 and isinstance(uv[0], (int, float)):
                # Развёртка коробки в Bedrock-геометрии (uv задан парой = box UV):
                # по ширине коробка занимает 2*(size.x+size.z), по высоте
                # size.y+size.z. Мягкая формула (size.x+size.z) НЕДООЦЕНИВАЕТ
                # ширину вдвое: на сдаче 3.8.0 она пропустила 3 из 4 реальных
                # переполнений (witch/evoker/illusioner, uv 40 + 2*(16+4) = 80
                # при текстуре 64). Проверено сравнением с эталоном Художника.
                uv_max_u = max(uv_max_u, uv[0] + 2 * ((size[0] or 0) + (size[2] or 0)))
                uv_max_v = max(uv_max_v, uv[1] + (size[1] or 0) + (size[2] or 0))
    return {
        "bones": len(bones),
        "raw_bones": bones,
        "names": [n for n in names if n],
        "problems": problems,
        "uv_max": (uv_max_u, uv_max_v),
        "tex_size": geo.get("description", {}).get("texture_size") or [64, 64],
    }


# Минимум костей в ключах по каждой анимации — решение Архитектора H36.
MIN_KEYED = {"idle": 2, "walk": 3, "attack": 3, "hurt": 3, "death": 4}
EPS = 1e-6


def _motion_values(node, out):
    """Собрать числа-значения каналов, отбросив времена ключей.

    Формат Bedrock: `rotation: [[t, [x,y,z]], ...]` либо `[[x,y,z], ...]`
    (равномерные кадры) либо `{"pre":..,"post":..}`. Время (первый элемент
    пары) в значения не попадает — иначе анимация «с двумя одинаковыми
    кадрами» выглядела бы движущейся только потому, что у кадров разные t.
    """
    if isinstance(node, (int, float)):
        out.append(float(node))
    elif isinstance(node, list):
        if (len(node) == 2 and isinstance(node[0], (int, float))
                and isinstance(node[1], (list, dict))):
            _motion_values(node[1], out)
        else:
            for x in node:
                _motion_values(x, out)
    elif isinstance(node, dict):
        # Ключи каналов: {"0.0": [..], "1.0": [..]} (Bedrock, время строкой)
        # либо {"pre": .., "post": ..} — значения рекурсивно, времена-ключи нет.
        for v in node.values():
            _motion_values(v, out)


def _molang(node):
    """Есть ли в канале выражение Molang (строка) — его числом не измерить."""
    if isinstance(node, str):
        return True
    if isinstance(node, list):
        return any(_molang(x) for x in node)
    if isinstance(node, dict):
        return any(_molang(v) for v in node.values())
    return False


def anim_stats(body):
    """(костей в ключах, из них реально двигаются, есть ли статика).

    R14 §7: канал может быть задан выражением Molang (строкой). Такое
    движение существует, но числом не измеряется — считать его «без ключевых
    кадров» было бы ложным провалом (нашлось на `infected_zombie.pulsing`).
    """
    bones = body.get("bones") or {}
    keyed = 0
    moving = 0
    for chans in bones.values():
        vals = []
        mol = False
        for v in chans.values():
            _motion_values(v, vals)
            mol = mol or _molang(v)
        if vals or mol:
            keyed += 1
            if mol or (vals and max(vals) - min(vals) > EPS):
                moving += 1
    return keyed, moving


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--min-bones", type=int, default=12)
    ap.add_argument("--require-anims", action="store_true",
                    help="отсутствие idle/walk/attack/hurt/death — провал, "
                         "а не предупреждение (приёмка 3.8.1/H-блока)")
    ap.add_argument("--only", default=None,
                    help="имена через запятую — проверять только их")
    ap.add_argument("--dedupe-bones", action="store_true",
                    help="R14 §6: считать только «реальные» (анатомические) кости — "
                         "кости с одинаковыми pivot и кубами у ≥80 %% существ "
                         "считаются скопированной декорацией и в порог не идут")
    a = ap.parse_args()

    files = iter_files(a.sources)

    def by_tail(suffix):
        """{базовое имя: реальный ключ} по хвосту пути.

        Сдача может лежать и плоско (`geo/x.geo.json`, `textures/entity/x.png`),
        и полным пакетом (`src/main/resources/assets/carnis/geo/entity/x.geo.json`).
        Поэтому имя ищется по хвосту, а не собирается из шаблона пути.
        """
        out = {}
        for k in files:
            if k.endswith(suffix):
                base = k.split("/")[-1][: -len(suffix)]
                out.setdefault(base, k)
        return out

    geo_by_name = by_tail(".geo.json")
    tex_by_name = {}
    for k in files:
        if "/textures/entity/" in ("/" + k) or k.startswith("textures/entity/"):
            base = k.split("/")[-1][:-4]
            if k.endswith(".png"):
                tex_by_name.setdefault(base, k)
    anim_by_name = by_tail(".animation.json")

    geos = sorted(geo_by_name.values())
    if not geos:
        print("ОШИБКА: в источниках нет geo/*.geo.json")
        return 1

    only = set(x.strip() for x in a.only.split(",")) if a.only else None
    creatures = []
    for g in geos:
        name = g.split("/")[-1].replace(".geo.json", "")
        if only and name not in only:
            continue
        creatures.append(name)

    # R14 §6: одна и та же кость с ОДИНАКОВЫМИ pivot и кубами у большинства
    # существ — это скопированная декорация, а не анатомия. Она раздувает
    # счётчик «костей», по которому H36 требует >= 12.
    _sig = {}
    for _n in creatures:
        _g = geo_by_name.get(_n)
        if not _g:
            continue
        try:
            _info = geo_info(files[_g])
        except Exception:
            continue
        for _b in _info.get("raw_bones", []):
            k = (_b.get("name"), json.dumps(_b.get("pivot"), sort_keys=True),
                 json.dumps([(c.get("size"), c.get("origin"))
                             for c in (_b.get("cubes") or [])], sort_keys=True))
            _sig[k] = _sig.get(k, 0) + 1
    _limit = max(2, int(0.8 * max(1, len(creatures))))

    def real_bones(info):
        out = []
        for b in info.get("raw_bones", []):
            k = (b.get("name"), json.dumps(b.get("pivot"), sort_keys=True),
                 json.dumps([(c.get("size"), c.get("origin"))
                             for c in (b.get("cubes") or [])], sort_keys=True))
            if _sig.get(k, 0) < _limit:
                out.append(b.get("name"))
        return out

    fails, warns = [], []

    def bad(msg):
        fails.append(msg)
        print("  \u2717 " + msg)

    def warn(msg):
        warns.append(msg)
        print("  ! " + msg)

    print("Источники: %s" % ", ".join(a.sources))
    print("Существ в сдаче: %d\n" % len(creatures))
    header = ("существо", "костей", "текстура", "цветов", "топ%", "glowmask", "UV", "анимации")
    print("%-26s %6s %10s %6s %6s %12s %9s %s" % header)
    print("-" * 104)

    for name in creatures:
        g = geo_by_name.get(name, "")
        tex = tex_by_name.get(name, "")
        glow = tex_by_name.get(name + "_glowmask", "")
        try:
            if not g:
                raise ValueError("нет geo с таким именем")
            info = geo_info(files[g])
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            bad("%s: geo не разбирается (%s)" % (name, e))
            continue
        for p in info["problems"]:
            bad("%s: %s" % (name, p))
        if info["bones"] < a.min_bones:
            warn("%s: костей %d < %d" % (name, info["bones"], a.min_bones))
        rb = real_bones(info)
        if a.dedupe_bones and len(rb) < a.min_bones:
            bad("%s: реальных костей %d < %d (из %d: остальные — одинаковая "
                "декорация у большинства существ)" % (name, len(rb), a.min_bones,
                                                      info["bones"]))

        if not tex or tex not in files:
            bad("%s: нет текстуры textures/entity/%s.png" % (name, name))
            continue
        st = png_stats(files[tex])
        w, h = st["size"]
        u, v = info["uv_max"]
        uv_ok = u <= w and v <= h
        if not uv_ok:
            bad("%s: UV выходит за текстуру: нужно %dx%d, файл %dx%d" % (name, u, v, w, h))
        if st["colors"] < 7:
            bad("%s: цветов %d < 7 (A3R1)" % (name, st["colors"]))
        if st["top_share"] > 0.35:
            bad("%s: топ-доля %.1f %% > 35 %% (A3R1)" % (name, st["top_share"] * 100))
        if not st["alphas"] <= {0, 255}:
            bad("%s: альфа не бинарная %s" % (name, sorted(st["alphas"])[:5]))

        glow_res = "нет"
        if not glow or glow not in files:
            bad("%s: нет glowmask (правило Р-3)" % name)
        else:
            gs = png_stats(files[glow])
            if gs["size"] != st["size"]:
                bad("%s: размер маски %s != текстуры %s" % (name, gs["size"], st["size"]))
            elif gs["rgb_opaque"] != {GLOW}:
                bad("%s: непрозрачные цвета маски %s, нужен только %s"
                    % (name, sorted(gs["rgb_opaque"])[:4], GLOW))
            elif not gs["alphas"] <= {0, 255}:
                bad("%s: альфа маски не бинарная" % name)
            else:
                tim, gim = st["im"], gs["im"]
                out = 0
                for y in range(tim.height):
                    for x in range(tim.width):
                        if gim.getpixel((x, y))[3] > 0 and tim.getpixel((x, y))[3] == 0:
                            out += 1
                if out:
                    bad("%s: свечение вне силуэта %d px" % (name, out))
                glow_res = "%dpx" % gs["opaque"]

        # анимации
        anim_files = ([anim_by_name[name]] if name in anim_by_name else
                      [k for k in files if k.endswith("/" + name + ".animation.json")
                       or k == name + ".animation.json"])
        anim_res = "—"
        if anim_files:
            anim_bones = set()
            anim_names = set()
            _anim_bodies = []
            for af in anim_files:
                data = json.loads(files[af].decode("utf-8"))
                for anim_name, body in (data.get("animations") or {}).items():
                    anim_names.add(anim_name.split(".")[-1].split(".")[0])
                    _anim_bodies.append((anim_name, body))
                    for bname in (body.get("bones") or {}):
                        anim_bones.add(bname)
            unknown = sorted(anim_bones - set(info["names"]))
            if unknown:
                bad("%s: анимации ссылаются на несуществующие кости: %s"
                    % (name, ", ".join(unknown[:5])))
            missing = [x for x in REQUIRED_ANIMS if x not in anim_names]
            anim_res = "%d/%d" % (len(REQUIRED_ANIMS) - len(missing), len(REQUIRED_ANIMS))
            if missing:
                (bad if a.require_anims else warn)(
                    "%s: нет анимаций %s" % (name, ", ".join(missing)))
            # Ключи: сколько костей реально двигается (H36) и есть ли движение
            # вообще. Пустая или статичная анимация — та же болванка, только
            # выглядит как выполненная работа.
            cov = []
            union = set()
            for anim_name, body in _anim_bodies:
                union |= set((body.get("bones") or {}).keys())
                short = anim_name.split(".")[-1]
                keyed, moving = anim_stats(body)
                if keyed == 0:
                    bad("%s: анимация %s без ключевых кадров" % (name, anim_name))
                elif moving == 0:
                    bad("%s: анимация %s статична — ключи есть, тело не движется"
                        % (name, anim_name))
                need = MIN_KEYED.get(short)
                if need and keyed < need:
                    (bad if a.require_anims else warn)(
                        "%s: %s двигает %d костей из нужных %d"
                        % (name, short, keyed, need))
                if short in REQUIRED_ANIMS:
                    cov.append("%s:%d" % (short, keyed))
            if cov:
                anim_res = " ".join(cov)
            # H36: на существо в ключах должно быть >= 4 костей суммарно.
            if a.require_anims and union and len(union) < 4:
                bad("%s: в ключах всего %d костей (H36 требует >= 4): %s"
                    % (name, len(union), ", ".join(sorted(union))))
            fv = set()
            for af in anim_files:
                d = json.loads(files[af].decode("utf-8"))
                if "format_version" in d:
                    fv.add(str(d["format_version"]))
            if fv and fv != {"1.8.0"}:
                (bad if a.require_anims else warn)(
                    "%s: format_version анимаций %s, нужен 1.8.0 (H37)"
                    % (name, ", ".join(sorted(fv))))

        print("%-26s %6d %10s %6d %6.1f %12s %9s %s"
              % (name, info["bones"], "%dx%d" % (w, h), st["colors"],
                 st["top_share"] * 100, glow_res,
                 "%s" % ("ok" if uv_ok else "ВЫХОД"), anim_res))

    print("\n" + "-" * 104)
    print("Существ: %d, провалов: %d, предупреждений: %d"
          % (len(creatures), len(fails), len(warns)))
    if fails:
        print("ИТОГ: ЕСТЬ ЗАМЕЧАНИЯ")
        return 2
    print("ИТОГ: СХОДИТСЯ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
