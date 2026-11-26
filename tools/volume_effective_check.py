#!/usr/bin/env python3
"""Итоговая громкость события = call-site (Java) x sounds.json.

Зачем: S62 [sound] сравнил ТЗ с ОДНИМ множителем (sounds.json) и выдал вывод
«7 из 9 событий не по ТЗ». Фактически множителей два, они перемножаются, и
верное число было «1 из 9». Этот тест считает итог и не даёт повторить ошибку.

    effective = call_site_volume (из Java) * volume каждого сэмпла (sounds.json)

Коды возврата:
  0 — все события спеки в пределах tolerance
  2 — есть расхождение (печатает событие, сэмпл, ожидание, факт)
  3 — спек/пакет/поле не читаются (fail-closed: не «нет данных», а ошибка)

Пути к Java берутся из спеки (поле call_site.file) — тест НЕ угадывает, в каком
файле живёт вызов, и НЕ ищет вызовы по всему дереву: неоднозначность дала бы
ложное «всё хорошо» при верном числе файлов.

Использование:
  python3 tools/volume_effective_check.py --pkg 01-coder/3.7.3 \
      --spec 03-sound/spec/volume_spec_t3202.json
"""
import argparse
import json
import os
import re
import sys

# volume — последний float-литерал в аргументах playSound/playLocalSound
CALL_RE = re.compile(r"(?:playLocalSound|playSound)\s*\((.*?)\)\s*;", re.S)


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sounds_json_of(pkg):
    p = os.path.join(pkg, "src/main/resources/assets/carnis/sounds.json")
    if not os.path.isfile(p):
        raise FileNotFoundError(p)
    return p


def volumes_of_event(sj, event):
    """Список volume по сэмплам события из sounds.json."""
    reg = sj.get("sounds", sj)
    node = reg.get(event)
    if node is None:
        raise KeyError(event)
    out = []
    for s in node.get("sounds", []):
        out.append(float(s.get("volume", sj.get("volume", 1.0))
                        if isinstance(s, dict) else 1.0))
    return out or [1.0]


def call_site_volume(pkg_path, event, spec_entry):
    """vol из Java: ищем playSound/playLocalSound(...), где встречается событие."""
    rel = spec_entry.get("call_site", {}).get("file")
    if not rel:
        raise KeyError("call_site.file")
    path = os.path.join(pkg_path, rel)
    if not os.path.isfile(path):
        raise FileNotFoundError(rel)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    ev = event.replace(".", "_").upper()          # hive.spread -> HIVE_SPREAD
    marker = spec_entry.get("call_site", {}).get("arg_marker")
    if marker:
        # Общий call-site через переменную: событие должно ВЫБИРАТЬСЯ в этом же
        # файле, иначе маркер — допущение, а не факт кода.
        if ev not in src.upper():
            raise LookupError("%s: событие %s не выбирается в этом файле, "
                              "arg_marker '%s' не подтверждается" % (rel, ev, marker))
        needle = marker
    else:
        needle = ev
    for m in CALL_RE.finditer(src):
        args = m.group(1)
        if needle not in args:
            continue
        floats = re.findall(r"(\d+\.\d+)F", args)
        if len(floats) >= 2:                       # (volume, pitch)
            return float(floats[-2])
        if len(floats) == 1:
            return float(floats[0])
    raise LookupError("%s: вызов %s не найден" % (rel, ev))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", required=True, help="каталог версии пакета, напр. 01-coder/3.7.3")
    ap.add_argument("--spec", required=True, help="JSON спеки громкостей")
    a = ap.parse_args(argv)

    try:
        spec = read_json(a.spec)
        sj = read_json(sounds_json_of(a.pkg))
    except (OSError, ValueError) as exc:
        print("ОШИБКА: %s" % exc)
        return 3

    tol = float(spec.get("tolerance", 0.005))
    bad = 0
    total = 0
    print("пакет: %s" % a.pkg)
    print("%-22s %6s %8s %10s  %s" % ("событие", "ТЗ", "call-site", "факт", "вердикт"))
    for ent in spec.get("events", []):
        ev = ent["event"]
        target = float(ent["target"])
        try:
            cs = call_site_volume(a.pkg, ev, ent)
            vols = volumes_of_event(sj, ev)
        except (OSError, KeyError, LookupError) as exc:
            print("%-22s %6.2f %8s %10s  ОШИБКА: %s" % (ev, target, "?", "?", exc))
            return 3
        # каждый сэмпл события должен давать target
        worst = max(vols, key=lambda v: abs(cs * v - target))
        eff = cs * worst
        total += 1
        ok = abs(eff - target) <= tol
        if not ok:
            bad += 1
        print("%-22s %6.2f %8.2f %10.3f  %s" % (
            ev, target, cs, eff,
            "ok" if ok else "РАСХОЖДЕНИЕ (x%.2f)" % (eff / target)))
        if not ok:
            for i, v in enumerate(vols):
                if abs(cs * v - target) > tol:
                    print("      сэмпл %d: sounds.json volume %.2f -> %.3f" % (i, v, cs * v))

    if bad:
        print("ИТОГ: %d из %d вне допуска (tolerance %.3f)" % (bad, total, tol))
        print("Починка — править ОДИН множитель, не оба: снижение в sounds.json\n"
              "поверх уже понижённого call-site даёт двойное умножение (S62/S68).")
        return 2
    print("ИТОГ: %d из %d в норме" % (total, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
