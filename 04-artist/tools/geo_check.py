#!/usr/bin/env python3
"""Геометрический чекер для Bedrock .geo.json моделей (H24).
Проверяет:
  - наличие texture_width / texture_height
  - уникальность имён костей
  - наличие pivot и валидность parent
  - UV-координаты кубов в пределах [0, texture_width] x [0, texture_height]
"""
from __future__ import annotations
import json
from typing import Any

def check_geo(data: dict[str, Any], name: str = "model") -> tuple[bool, list[str]]:
    errors: list[str] = []
    geos = data.get("minecraft:geometry") or []
    if not geos:
        return False, [f"{name}: missing minecraft:geometry"]
    g = geos[0]
    desc = g.get("description", {})
    tw = desc.get("texture_width")
    th = desc.get("texture_height")
    if not tw or not th:
        errors.append(f"{name}: missing texture_width/texture_height")
        return False, errors

    bones = g.get("bones", [])
    seen = set()
    for b in bones:
        bn = b.get("name", "")
        if not bn:
            errors.append(f"{name}: bone without name")
        elif bn in seen:
            errors.append(f"{name}: duplicate bone '{bn}'")
        seen.add(bn)
        if "pivot" not in b:
            errors.append(f"{name}: bone '{bn}' missing pivot")

    for b in bones:
        bn = b.get("name", "?")
        par = b.get("parent")
        if par and par not in seen:
            errors.append(f"{name}: bone '{bn}' has unknown parent '{par}'")
        for ci, c in enumerate(b.get("cubes", [])):
            uv = c.get("uv")
            sz = c.get("size", [0, 0, 0])
            if isinstance(uv, list) and len(uv) == 2 and len(sz) == 3:
                u, v = uv
                w, h, d = sz
                max_u = u + 2 * d + 2 * w
                max_v = v + d + h
                if u < 0 or v < 0 or max_u > tw or max_v > th:
                    errors.append(
                        f"{name}: bone '{bn}' cube[{ci}] UV ({u},{v})+({2*d+2*w},{d+h}) > {tw}x{th}"
                    )
    return len(errors) == 0, errors
