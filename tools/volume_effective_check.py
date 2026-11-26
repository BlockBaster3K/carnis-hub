#!/usr/bin/env python3
"""Итоговая громкость события = call-site (Java) x sounds.json.

Зачем: S62 [sound] сравнил ТЗ с ОДНИМ множителем (sounds.json) и выдал вывод
«7 из 9 событий не по ТЗ». Фактически множителей два, они перемножаются, и
верное число было «1 из 9». Этот тест считает итог и не даёт повторить ошибку.

    effective = call_site_volume (из Java) * volume каждого сэмпла (sounds.json)

Цель задаётся ДВУМЯ способами (схема carnis.volume_spec/2):
  * "target": одно число на событие — когда сэмплы события равноценны;
  * "targets_by_sample": цель по имени сэмпла — когда сэмплы разной громкости
    ПО ПРИРОДЕ и одна цель на событие неверна.

Второй случай не гипотетический: `hive.detail_flow_01` тише пары на 8 дБ
(пик −15.1 / RMS −29.6 против −7.3 / −21.9), поэтому S17 назначил ему 0.45,
а `flow_02` — 0.30. Схема «одна цель на событие» вынудила бы выровнять
множители и создать слышимый провал «то есть звук, то нет».

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
import zipfile

# volume — последний float-литерал в аргументах playSound/playLocalSound
CALL_RE = re.compile(r"(?:playLocalSound|playSound)\s*\((.*?)\)\s*;", re.S)


SJ_REL = "src/main/resources/assets/carnis/sounds.json"


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_zip(pkg):
    """Пакет может быть ZIP — гейт передаёт путь к архиву, а не каталог.

    Пока чекер умел только каталог, интеграция с гейтом давала код 3 на
    ЛЮБОМ пакете: блок 9в передавал `os.path.dirname(zip_path)`, и проверка
    громкости не выполнялась ни разу. Поддержка ZIP убирает эту зависимость
    от того, распакован пакет или нет.
    """
    return os.path.isfile(pkg) and zipfile.is_zipfile(pkg)


def _read_from_zip(zf, rel):
    try:
        return zf.read(rel).decode("utf-8")
    except KeyError:
        raise FileNotFoundError("%s (внутри %s)" % (rel, os.path.basename(zf.filename)))


def volumes_of_event(sj, event):
    """[(имя сэмпла или None, volume)] по звукам события из sounds.json."""
    reg = sj.get("sounds", sj)
    node = reg.get(event)
    if node is None:
        raise KeyError(event)
    out = []
    for s in node.get("sounds", []):
        if isinstance(s, dict):
            name = s.get("name")
            name = name.split(":")[-1].split("/")[-1] if name else None
            out.append((name, float(s.get("volume", 1.0))))
        else:
            out.append((None, 1.0))
    return out or [(None, 1.0)]


def call_site_volume(pkg_path, event, spec_entry, zf=None):
    """vol из Java: ищем playSound/playLocalSound(...), где встречается событие."""
    rel = spec_entry.get("call_site", {}).get("file")
    if not rel:
        raise KeyError("call_site.file")
    if zf is not None:
        src = _read_from_zip(zf, rel)
    else:
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

    zf = None
    try:
        spec = read_json(a.spec)
        if is_zip(a.pkg):
            zf = zipfile.ZipFile(a.pkg)
            sj = json.loads(_read_from_zip(zf, SJ_REL))
        else:
            sj = read_json(os.path.join(a.pkg, SJ_REL))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print("ОШИБКА: %s" % exc)
        return 3
    try:
        return _run(a, spec, sj, zf)
    finally:
        if zf is not None:
            zf.close()


def _run(a, spec, sj, zf=None):

    tol = float(spec.get("tolerance", 0.005))
    bad = 0
    total = 0
    print("пакет: %s" % a.pkg)
    print("%-22s %10s %8s %10s  %s" % ("событие", "ТЗ", "call-site", "факт", "вердикт"))
    for ent in spec.get("events", []):
        ev = ent["event"]
        by_sample = ent.get("targets_by_sample")
        target = ent.get("target")
        if by_sample is None and target is None:
            print("%-22s %6s %8s %10s  ОШИБКА: нет цели (target или targets_by_sample)" % (ev, "?", "?", "?"))
            return 3
        try:
            cs = call_site_volume(a.pkg, ev, ent, zf)
            vols = volumes_of_event(sj, ev)
        except (OSError, KeyError, LookupError) as exc:
            print("%-22s %6s %8s %10s  ОШИБКА: %s" % (ev, target or "по сэмплам", "?", "?", exc))
            return 3
        # Для каждого сэмпла — своя цель: из targets_by_sample либо общая target.
        per = []
        for name, v in vols:
            if by_sample is not None:
                if name not in by_sample:
                    print("%-22s  ОШИБКА: цель для сэмпла '%s' не задана в targets_by_sample" % (ev, name))
                    return 3
                t = float(by_sample[name])
            else:
                t = float(target)
            per.append((name, v, cs * v, t))
        total += 1
        worst = max(per, key=lambda r: abs(r[2] - r[3]))
        ok = abs(worst[2] - worst[3]) <= tol
        if not ok:
            bad += 1
        label = ("%.2f" % float(target)) if target is not None else "по сэмплам"
        print("%-22s %10s %8.2f %10.3f  %s" % (
            ev, label, cs, worst[2],
            "ok" if ok else "РАСХОЖДЕНИЕ (x%.2f)" % (worst[2] / worst[3])))
        if not ok or by_sample is not None:
            for name, v, eff, t in per:
                mark = "" if abs(eff - t) <= tol else "  <-- вне допуска"
                print("      %s: sounds.json volume %.2f -> %.3f (цель %.2f)%s"
                      % (name or "?", v, eff, t, mark))

    if bad:
        print("ИТОГ: %d из %d вне допуска (tolerance %.3f)" % (bad, total, tol))
        print("Починка — править ОДИН множитель, не оба: снижение в sounds.json\n"
              "поверх уже понижённого call-site даёт двойное умножение (S62/S68).")
        return 2
    print("ИТОГ: %d из %d в норме" % (total, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
