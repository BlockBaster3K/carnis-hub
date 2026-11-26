#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""creature_pack_audit_selftest.py — негативные тесты на `creature_pack_audit.py`.

Каждый случай — ровно та ошибка, которую глазами не видно и которую гейт 3.8.0
сегодня пропускает (см. `00-board/reports/reviewer_gate_380_block16_audit.md`):

  A. текстура из 3 непрозрачных цветов, но 8 разных RGB при альфе 0 — «цветов 11»
     при подсчёте по RGBA-кортежам (норма A3R1: >= 7 именно непрозрачных);
  B. glowmask 8x8 при текстуре 64x64 (Р-3: размер обязан совпадать);
  C. свечение на прозрачных пикселях тела (Р-3: вне силуэта 0 px);
  D. кость без `pivot` и UV куба за пределами текстуры;
  E. контроль: всё в норме — чекер обязан дать код 0.

Запуск: python3 02-reviewer/tools/creature_pack_audit_selftest.py
Код 0 — все ожидания сошлись (чекер строг там, где надо), 1 — расхождение.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "creature_pack_audit.py")
NAME = "infected_probe"
BASE = "src/main/resources/assets/carnis"


def _geo(pivot=True, uv=(0, 0), size=(8, 8, 8)):
    bone = {"name": "body", "cubes": [{"uv": list(uv), "size": list(size)}]}
    if pivot:
        bone["pivot"] = [0, 0, 0]
    return {"minecraft:geometry": [{
        "description": {"texture_width": 64, "texture_height": 64},
        "bones": [bone]}]}


def _tex_normal():
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for i in range(7):
        for x in range(10):
            im.putpixel((x + i * 9, 0), (i * 30, i * 20, i * 10, 255))
    return im


def _tex_three_colors():
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for i, c in enumerate([(10, 10, 10, 255), (20, 20, 20, 255), (30, 30, 30, 255)]):
        for x in range(10):
            im.putpixel((x + i * 10, 0), c)
    for i in range(8):
        for x in range(8):
            im.putpixel((x, 10 + i), (i * 7, i * 11, i * 13, 0))
    return im


def _mask_ok():
    m = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for i in range(7):
        for x in range(10):
            m.putpixel((x + i * 9, 0), (255, 92, 57, 255))
    return m


def _mask_small():
    m = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    for x in range(8):
        m.putpixel((x, 0), (255, 92, 57, 255))
    return m


def _mask_outside():
    m = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for x in range(64):
        m.putpixel((x, 63), (255, 92, 57, 255))
    return m


def _anim(bone="body", keyframes=2):
    """Анимация на одну кость: `keyframes` кадров поворота."""
    return {"animations": {"animation.%s.idle" % NAME: {
        "loop": True,
        "animation_length": 1.0,
        "bones": {bone: {"rotation": [[0, 0, 0]] * max(keyframes, 0)}}}}}


CASES = [
    ("A: 3 непрозрачных цвета + 8 «пустых» RGB", 2,
     dict(tex=_tex_three_colors(), mask=_mask_ok())),
    ("B: маска 8x8 при текстуре 64x64", 2, dict(tex=_tex_normal(), mask=_mask_small())),
    ("C: свечение вне силуэта", 2, dict(tex=_tex_normal(), mask=_mask_outside())),
    ("D: кость без pivot + UV за пределами", 2,
     dict(tex=_tex_normal(), mask=_mask_ok(), geo=_geo(pivot=False, uv=(200, 200)))),
    ("E: контроль — всё в норме", 0, dict(tex=_tex_normal(), mask=_mask_ok())),
    # Ниже — случаи H-блока/3.8.1: «анимация есть, а работать не будет».
    ("F: анимация ссылается на несуществующую кость", 2,
     dict(tex=_tex_normal(), mask=_mask_ok(), anim=_anim(bone="хвост_которого_нет"))),
    ("G: анимация без ключевых кадров", 2,
     dict(tex=_tex_normal(), mask=_mask_ok(), anim=_anim(keyframes=0))),
    # I: мягкая формула UV (size.x+size.z) пропускала это; box-UV обязан ловить
    ("I: box-UV шириной 2*(sx+sz) вылезает за текстуру", 2,
     dict(tex=_tex_normal(), mask=_mask_ok(), geo=_geo(uv=(40, 38), size=(16, 4, 4)))),
    # J: файла анимаций НЕТ вовсе — под --require-anims это провал, а не «ok —»
    ("J: --require-anims, файла анимаций нет", 2,
     dict(tex=_tex_normal(), mask=_mask_ok(), extra=["--require-anims"])),
    ("H: --require-anims при одной анимации из пяти", 2,
     dict(tex=_tex_normal(), mask=_mask_ok(), anim=_anim(),
          extra=["--require-anims"])),
]


def main():
    if not os.path.isfile(TOOL):
        print("ОШИБКА: нет %s" % TOOL)
        return 1
    tmp = tempfile.mkdtemp(prefix="cpa_selftest_")
    bad = 0
    try:
        for label, expect, kw in CASES:
            d = os.path.join(tmp, label.split(":")[0])
            geo_dir = os.path.join(d, BASE, "geo")
            tex_dir = os.path.join(d, BASE, "textures", "entity")
            os.makedirs(geo_dir)
            os.makedirs(tex_dir)
            with open(os.path.join(geo_dir, NAME + ".geo.json"), "w", encoding="utf-8") as f:
                json.dump(kw.get("geo", _geo()), f)
            kw["tex"].save(os.path.join(tex_dir, NAME + ".png"))
            kw["mask"].save(os.path.join(tex_dir, NAME + "_glowmask.png"))
            if kw.get("anim"):
                anim_dir = os.path.join(d, BASE, "animations", "entity")
                os.makedirs(anim_dir)
                with open(os.path.join(anim_dir, NAME + ".animation.json"), "w",
                          encoding="utf-8") as f:
                    json.dump(kw["anim"], f)
            # --registry "": фикстуры синтетические и в реестре Художника их нет,
            # иначе фильтр по реестру отбросил бы проверяемую модель
            r = subprocess.run([sys.executable, TOOL, d, "--min-bones", "1",
                                "--registry", ""]
                               + kw.get("extra", []),
                               capture_output=True, text=True)
            ok = r.returncode == expect
            print("%-40s ожидался код %d, получен %d  %s"
                  % (label, expect, r.returncode, "OK" if ok else "РАСХОЖДЕНИЕ"))
            if not ok:
                bad += 1
                for ln in r.stdout.splitlines():
                    if ln.strip().startswith("\u2717"):
                        print("      " + ln.strip())
        print("\nСлучаев: %d, расхождений: %d" % (len(CASES), bad))
        return 0 if bad == 0 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
