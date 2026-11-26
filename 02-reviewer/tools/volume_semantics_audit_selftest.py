#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Самопроверка `volume_semantics_audit.py` на синтетических пакетах.

Фикстуры создаются тут же, в tempdir: два .ogg с разными уровнями
(разрыв ≈ 7,7 дБ — как у реальной пары `detail_flow_01/02`), sounds.json,
спека. Проверяется, что инструмент ловит ровно те классы ошибок, ради
которых написан, и не валит корректный пакет.

Запуск: python3 02-reviewer/tools/volume_semantics_audit_selftest.py
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "volume_semantics_audit.py")

CALL_SITE = 0.30          # как у hive.detail_flow
LOUD, QUIET = 0.5, 0.205  # амплитуды: 20lg(0.5/0.205) = 7.74 дБ


def make_fixture(root, vols, targets, mode="json", call_site=CALL_SITE,
                 with_audio=True, spec=True, peak_note=None):
    """Собирает пакет-фикстуру. vols — {stem: volume} (None — ключ убрать)."""
    import numpy as np
    import soundfile as sf

    sounds_dir = os.path.join(root, "src", "main", "resources", "assets",
                              "carnis", "sounds", "hive")
    os.makedirs(sounds_dir, exist_ok=True)
    sr = 8000
    t = np.arange(sr, dtype="float32") / sr
    if with_audio:
        for stem, amp in (("fixture_loud", LOUD), ("fixture_quiet", QUIET)):
            sf.write(os.path.join(sounds_dir, stem + ".ogg"),
                     (amp * np.sin(2 * math.pi * 220 * t)).astype("float32"), sr)
    sounds = {"hive.test_event": {"sounds": []}}
    for stem, vol in vols.items():
        node = {"name": "carnis:hive/" + stem}
        if vol is not None:
            node["volume"] = vol
        sounds["hive.test_event"]["sounds"].append(node)
    with open(os.path.join(root, "src", "main", "resources", "assets",
                           "carnis", "sounds.json"), "w") as fh:
        json.dump(sounds, fh, indent=2)

    spec_path = os.path.join(root, "spec.json")
    if spec:
        entry = {"event": "hive.test_event", "call_site": {"volume": call_site},
                 "targets_by_sample": targets, "board_target": call_site}
        if peak_note is not None:
            entry["why"] = ("измерено выравнивание при пике %.2f dBFS" % peak_note)
        with open(spec_path, "w") as fh:
            json.dump({"schema": 2, "tolerance": 0.005, "targets_mode": mode,
                       "events": [entry]}, fh, indent=2, ensure_ascii=False)
    return spec_path


def run(pkg, spec, extra=()):
    cmd = [sys.executable, TOOL, "--pkg", pkg, "--spec", spec] + list(extra)
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def c1_half_fix_caught(tmp):
    """Изменён один сэмпл пары — «правка ухудшила разброс»."""
    base = os.path.join(tmp, "base")
    pkg = os.path.join(tmp, "pkg")
    os.makedirs(base)
    os.makedirs(pkg)
    targets = {"fixture_quiet": 0.30 * 2.437, "fixture_loud": 0.30}
    s_base = make_fixture(base, {"fixture_quiet": None, "fixture_loud": None},
                          targets)
    make_fixture(pkg, {"fixture_quiet": 0.731, "fixture_loud": 1.0}, targets)
    code, out = run(pkg, s_base, ["--baseline", base])
    return code == 2 and "УХУДШИЛА" in out, "код %d, %s" % (
        code, "слово УХУДШИЛА есть" if "УХУДШИЛА" in out else "нет УХУДШИЛА")


@case
def c2_correct_package_passes(tmp):
    """Верный пакет (эффективная семантика) — находок нет."""
    pkg = os.path.join(tmp, "pkg")
    os.makedirs(pkg)
    targets = {"fixture_quiet": 0.30 * 2.437, "fixture_loud": 0.30}
    spec = make_fixture(pkg, {"fixture_quiet": 2.437, "fixture_loud": 1.0},
                        targets)
    code, out = run(pkg, spec)
    return code == 0 and "метка targets_mode" in out, "код %d" % code


@case
def c3_label_mismatch_is_note_not_finding(tmp):
    """Метка врёт, пакет верен: по умолчанию — замечание, со --strict-label — находка."""
    pkg = os.path.join(tmp, "pkg")
    os.makedirs(pkg)
    targets = {"fixture_quiet": 0.30 * 2.437, "fixture_loud": 0.30}
    spec = make_fixture(pkg, {"fixture_quiet": 2.437, "fixture_loud": 1.0},
                        targets)
    code_soft, _ = run(pkg, spec)
    code_hard, _ = run(pkg, spec, ["--strict-label"])
    return code_soft == 0 and code_hard == 2, "мягко %d / строго %d" % (
        code_soft, code_hard)


@case
def c4_silenced_event_caught_by_peak(tmp):
    """Пара выровнена, но событие уведено на −10 дБ: ловит канал пика."""
    base = os.path.join(tmp, "base")
    pkg = os.path.join(tmp, "pkg")
    os.makedirs(base)
    os.makedirs(pkg)
    targets = {"fixture_quiet": 0.731, "fixture_loud": 0.30}
    s_base = make_fixture(base, {"fixture_quiet": None, "fixture_loud": None},
                          targets)
    # «правильный» пакет (2.437/1.0) даёт пик −6,01 dBFS — он и объявлен в спеке;
    # пакет ниже выравнивает отношение, но уводит событие на −10,46 дБ
    s_pkg = make_fixture(pkg, {"fixture_quiet": 0.731, "fixture_loud": 0.30},
                         targets, peak_note=-6.01)
    code, out = run(pkg, s_pkg, ["--baseline", base])
    return code == 2 and "пик после множителей" in out, "код %d" % code


@case
def c5_no_sounds_json(tmp):
    """Нет sounds.json — «проверить нельзя», код 3."""
    pkg = os.path.join(tmp, "pkg")
    os.makedirs(os.path.join(pkg, "src"))
    spec = make_fixture(os.path.join(tmp, "gen"), {"x": 1.0}, {"x": 1.0})
    code, out = run(pkg, spec)
    return code == 3 and "НЕ ПРОВЕРЕНО" in out, "код %d" % code


@case
def c6_no_spec(tmp):
    """Нет спеки — код 3."""
    pkg = os.path.join(tmp, "pkg")
    os.makedirs(pkg)
    make_fixture(pkg, {"fixture_loud": 1.0}, {"fixture_loud": 1.0})
    code, out = run(pkg, os.path.join(tmp, "нет-такой-спеки.json"))
    return code == 3, "код %d" % code


@case
def c7_no_audio_no_crash(tmp):
    """Пакет без .ogg: каналы звука отключаются замечанием, падения нет."""
    pkg = os.path.join(tmp, "pkg")
    os.makedirs(pkg)
    targets = {"fixture_quiet": 0.30 * 2.437, "fixture_loud": 0.30}
    spec = make_fixture(pkg, {"fixture_quiet": 2.437, "fixture_loud": 1.0},
                        targets, with_audio=False)
    code, out = run(pkg, spec, ["--baseline", pkg])
    return code == 0 and "не посчитан" in out, "код %d" % code


def main():
    ok = 0
    failures = []
    for fn in CASES:
        tmp = tempfile.mkdtemp(prefix="vsa_")
        try:
            good, info = fn(tmp)
        except Exception as exc:                      # noqa: BLE001
            good, info = False, "исключение: %s" % exc
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        print("%s %-42s %s" % ("✓" if good else "✗", fn.__name__, info))
        if good:
            ok += 1
        else:
            failures.append(fn.__name__)
    print("\nИтог: %d/%d" % (ok, len(CASES)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
