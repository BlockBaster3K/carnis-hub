#!/usr/bin/env python3
"""Сводка всех проверок звука одной командой — чтобы находки не жили в stdout.

Зачем. Ревизор (reviewer_gate_split_audit.md §3) назвал главную проблему этого
контура: `.github/workflows/build.yml` не запускает ни гейт, ни отчётные
проверки, поэтому находки существуют **только в выводе ручного прогона**. Вся
история с громкостью началась ровно с такого случая: таблицу в доске проверили
глазами, а спеку — никто.

Этот агрегатор запускает все проверки звука и печатает ОДНУ сводку:

  manifest_canon_test     — манифест канона актуален (S65)
  pull_damage_check       — pull не удалил артефакты роли (S74)
  canon_normalize_plan    — что сломается при правке файла канона (S82)
  volume_effective_check  — итоговая громкость по спеке T-3202 (S70/S86)
  sample_loudness         — разброс сэмплов внутри события (S78)
  volume_double_check     — двойное применение громкости (Ревизор, R24)
  gate_selfoff_check      — проверка не отключается по чужому провалу (S92)

Коды возврата:
  0 — все проверки выполнились и все чистые
  2 — проверки выполнились, но есть находки (не «провал приёмки» — см. ниже)
  3 — хотя бы одна проверка НЕ ВЫПОЛНИЛАСЬ (fail-closed: «не проверили» ≠ «чисто»)

ВАЖНО про код 2. Находки по спеке роли (volume_effective_check, sample_loudness)
— это критерий Звука, а не приёмочная норма (это признано в S84 и в
`reviewer_gate_split_audit.md`). Поэтому агрегатор НЕ должен подключаться в гейт
как норма. Его место — CI как шаг, который ПЕЧАТАЕТ сводку и кладёт её в
summary/artifact. Кто захочет валить сборку — пусть решает отдельно и явно.

Использование:
  python3 tools/sound_report_all.py [--pkg ZIP_ИЛИ_КАТАЛОГ] [--json ФАЙЛ]
"""
import argparse
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

# (имя, скрипт, аргументы, как передаётся пакет: "flag" | "positional" | None)
#
# Про "positional": volume_double_check.py принимает пакет ПЕРВЫМ аргументом,
# без флага. Я сначала передал ему "--pkg" — он прочитал это как имя файла,
# не нашёл его и вернул 1. Агрегатор показал «не выполнено» вместо «чисто»,
# то есть fail-closed поймал мою же ошибку обвязки, а не дефект пакета.
CHECKS = [
    ("манифест канона", "tools/manifest_canon_test.py", [], None),
    ("содержимое после pull", "tools/pull_damage_check.py", [], None),
    ("план правки канона", "tools/canon_normalize_plan.py",
     ["--file", "sounds/hive/detail_flow_01.ogg"], None),
    ("разброс сэмплов", "tools/sample_loudness.py",
     ["--bank", os.path.join(REPO, "03-sound", "sounds")], None),
    ("громкость по спеке", "tools/volume_effective_check.py",
     ["--spec", os.path.join(REPO, "03-sound", "spec",
                             "volume_spec_t3202.json")], "flag"),
    ("двойное применение", "tools/volume_double_check.py", [], "positional"),
    ("гейты: самовыключение", "tools/gate_selfoff_check.py",
     [os.path.join(REPO, "tools", "accept_3.7.3.py"),
      os.path.join(REPO, "tools", "accept_3.8.0.py")], None),
]


def run_one(name, script, args, pkg_mode, pkg):
    path = os.path.join(REPO, script)
    if not os.path.isfile(path):
        return {"check": name, "code": None, "verdict": "НЕТ ИНСТРУМЕНТА",
                "detail": script, "ran": False}
    if pkg_mode and not pkg:
        return {"check": name, "code": None, "verdict": "ПРОПУЩЕНО (нет --pkg)",
                "detail": "", "ran": False}
    cmd = [PY, path] + list(args)
    if pkg_mode == "flag":
        cmd += ["--pkg", pkg]
    elif pkg_mode == "positional":
        cmd += [pkg]
    r = subprocess.run(cmd, capture_output=True, text=True)
    tail = [l for l in (r.stdout or "").strip().split("\n") if l.startswith("ИТОГ")]
    return {"check": name, "code": r.returncode,
            "verdict": tail[0][5:].strip() if tail else "(нет строки ИТОГ)",
            "detail": script, "ran": True}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default=None,
                    help="ZIP или каталог пакета; без него пакетные проверки пропускаются")
    ap.add_argument("--json", default=None, help="записать сводку в JSON")
    a = ap.parse_args(argv)

    rows = [run_one(n, s, args, mode, a.pkg) for n, s, args, mode in CHECKS]

    print("Сводка проверок звука")
    print("%-24s %5s  %s" % ("проверка", "код", "вердикт"))
    for r in rows:
        code = "—" if r["code"] is None else r["code"]
        print("%-24s %5s  %s" % (r["check"], code, r["verdict"]))

    not_run = [r for r in rows if not r["ran"] or r["code"] not in (0, 2)]
    findings = [r for r in rows if r["code"] == 2 and r["ran"]]
    clean = [r for r in rows if r["code"] == 0]

    print()
    print("чисто: %d, находок: %d, не выполнено: %d"
          % (len(clean), len(findings), len(not_run)))
    for r in findings:
        print("  · %s: %s" % (r["check"], r["verdict"]))
    for r in not_run:
        print("  x %s: %s — это НЕ «чисто»" % (r["check"], r["verdict"]))

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"rows": rows,
                       "clean": len(clean), "findings": len(findings),
                       "not_run": len(not_run)}, fh, ensure_ascii=False, indent=2)
        print("сводка записана: %s" % a.json)

    if not_run:
        print("ИТОГ: НЕПОЛНАЯ СВОДКА — %d проверок не выполнено" % len(not_run))
        return 3
    if findings:
        print("ИТОГ: ЕСТЬ НАХОДКИ — %d (критерий роли, не приёмочная норма)"
              % len(findings))
        return 2
    print("ИТОГ: ЧИСТО — все проверки выполнены и без находок")
    return 0


if __name__ == "__main__":
    sys.exit(main())
