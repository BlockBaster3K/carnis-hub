"""
tendrils_apply.py — вносит найденную подстройкой раскладку в tendrils_gen.py.

Читает tuned.json (результат tendrils_tune.py) и переписывает блок VARIANTS
в генераторе. Формат блока сохраняется — чтобы правка читалась.

Запуск:  python3 tools/tendrils_apply.py [tuned.json]
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "tendrils_gen.py")


def fmt_spec(name, spec):
    lines = []
    lines.append("    {")
    lines.append(f'        "name": "{name}",')
    lines.append(f'        "seed": {spec["seed"]},')
    lines.append(f'        "rot": {spec["rot"]:.2f},')
    lines.append('        "nodes": [')
    for node in spec["nodes"]:
        cx, cy = node["c"]
        rx, ry = node["r"]
        tend = ", ".join(f"({p:.1f}, {l:.1f}, {r:.1f})" for (p, l, r) in node["tendrils"])
        lines.append("            {")
        lines.append(f'                "c": ({cx:.1f}, {cy:.1f}), "r": ({rx:.1f}, {ry:.1f}), '
                     f'"gd": {node["gd"]:.2f},')
        lines.append(f'                "tendrils": [{tend}],')
        lines.append("            },")
    lines.append("        ],")
    lines.append("    },")
    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "tuned.json")
    with open(path, encoding="utf-8") as fh:
        tuned = json.load(fh)
    src = open(GEN, encoding="utf-8").read()
    start = src.index("VARIANTS = [")
    end = src.index("\n]\n", start) + 3
    block = "VARIANTS = [\n" + "\n".join(fmt_spec(n, d["spec"]) for n, d in tuned.items()) + "\n]\n"
    open(GEN, "w", encoding="utf-8").write(src[:start] + block + src[end:])
    print("tendrils_gen.py: блок VARIANTS обновлён")


if __name__ == "__main__":
    main()
