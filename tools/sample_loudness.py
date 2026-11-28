#!/usr/bin/env python3
"""Громкость сэмплов внутри события: где одна цель на событие неверна.

Зачем. Схема спеки «одна цель на событие» вынуждает выравнивать множители всех
сэмплов события. Это верно, когда сэмплы равноценны, и НЕВЕРНО, когда они разной
громкости по природе: тогда выравнивание множителей сохраняет (и даже
подчёркивает) разницу в уровне, и пара звучит как «то есть звук, то нет».

Так и вышло с `hive.detail_flow`: `flow_01` тише пары на ~7.8 дБ, S17 назначил
ему 0.45 против 0.30, а спека с одной целью потребовала 0.30 обоим — то есть
отменила решение S17, выглядя при этом «зелёной».

Тест показывает числа, на которых такое решение должно приниматься:
пик и RMS каждого сэмпла, разброс внутри события, и во сколько раз множитель
тихого сэмпла должен отличаться от громкого, чтобы уровни сравнялись.

Код возврата: 0 — разброс внутри всех событий ≤ порога;
              2 — есть событие с разбросом > порога (нужны цели по сэмплам);
              3 — не удалось измерить (нет банка/библиотеки).
"""
import argparse
import json
import math
import os
import sys

try:
    import numpy as np
    import soundfile as sf
except ImportError:
    np = None
    sf = None

DEFAULT_THRESHOLD_DB = 3.0


def db(x):
    return 20.0 * np.log10(max(float(x), 1e-12))


def measure(path):
    data, sr = sf.read(path, dtype="float64")
    if data.ndim > 1:
        data = data.mean(axis=1)
    return db(np.max(np.abs(data))), db(np.sqrt(np.mean(data ** 2))), len(data) / sr


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True, help="каталог sounds/ с .ogg")
    ap.add_argument("--events", nargs="*", default=None,
                    help="события как префиксы имён файлов; по умолчанию — все detail_*")
    ap.add_argument("--map", default=None,
                    help="sounds.json: группировать события по карте, а не по именам файлов")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD_DB)
    ap.add_argument("--spec", default=None,
                    help="volume_spec*.json: проверить, что объявленные targets_by_sample "
                         "действительно выравнивают разброс (поправка Ревизора, S98)")
    # 0.25, а не 1.0: Ревизор (reviewer_s98 §3) показал, что при 1.0 ошибка
    # в множителе на 1 дБ даёт остаток 0.98 и проходит как «ПОДТВЕРЖДЕНО».
    ap.add_argument("--residual", type=float, default=0.25,
                    help="допустимый ОСТАТОЧНЫЙ разброс после применения множителей, дБ")
    a = ap.parse_args(argv)

    if sf is None:
        print("ОШИБКА: нужны numpy и soundfile (pip install soundfile numpy)")
        return 3
    if not os.path.isdir(a.bank):
        print("ОШИБКА: нет каталога банка %s" % a.bank)
        return 3

    groups = {}
    for dp, _, fs in os.walk(a.bank):
        for f in fs:
            if not f.endswith(".ogg"):
                continue
            stem = f[:-4]
            if a.events and not any(stem.startswith(p) for p in a.events):
                continue
            groups.setdefault(stem, os.path.join(dp, f))

    if not groups:
        print("ОШИБКА: не найдено ни одного .ogg по заданным префиксам")
        return 3
    if not a.events and not any(k.startswith("detail_") for k in groups):
        # Без --events и без detail_* в банке раньше возвращалось «не найдено»,
        # то есть инструмент молча отказывался работать на чужом банке
        # (например sounds_380). Теперь меряет весь банк.
        print("банк без detail_*-сэмплов — меряю все %d файлов\n" % len(groups))

    bad = 0
    undeclared = 0
    spec_targets = {}
    spec_tol = {}
    spec_tol_why = {}
    spec_call_site = {}
    spec_mode = "json"
    if a.spec:
        # ⛔ Ревизор/Интегратор 2026-11-26: битый путь к спеке давал
        # FileNotFoundError с трейсбеком. В гейте это выглядело бы как
        # «чекер упал», а не как «спека не прочитана» — и разбор ушёл бы
        # искать дефект в пакете. Код 1 = «не смог проверить», по общей
        # конвенции чекеров, и без трейсбека.
        try:
            with open(a.spec, encoding="utf-8") as f:
                sp = json.load(f)
        except OSError as exc:
            print("ОШИБКА: спека не прочитана (%s) — объявленное засчитать "
                  "нельзя" % exc)
            return 1
        except ValueError as exc:
            print("ОШИБКА: спека не разобрана как JSON (%s)" % exc)
            return 1
        spec_mode = sp.get("targets_mode", "json")
        for e in sp.get("events", []):
            spec_targets[e.get("event", "")] = e.get("targets_by_sample", {}) or {}
            if e.get("residual_tolerance") is not None:
                spec_tol[e.get("event", "")] = float(e["residual_tolerance"])
                spec_tol_why[e.get("event", "")] = e.get("tolerance_why", "") or "" 
            # Точка вызова без множителя в коде (volume: null, kind:
            # "no_code_multiplier") — это НЕ «неизвестно», а ровно 1.0:
            # громкость не масштабируется кодом вовсе. Раньше такой случай
            # выпадал из словаря (if cs — а None ложно), и объявление с
            # корректными итоговыми целями печаталось как «СПЕКА НЕПОЛНА».
            # Нашёл на своём же событии combat.flesh_hit (S127).
            cs_obj = e.get("call_site") or {}
            cs = cs_obj.get("volume")
            if cs is not None:
                spec_call_site[e.get("event", "")] = float(cs)
            elif cs_obj.get("kind") == "no_code_multiplier":
                spec_call_site[e.get("event", "")] = 1.0
        print("спека: %s — целей по сэмплам: %d; семантика targets_by_sample: %s\n"
              % (a.spec, sum(1 for v in spec_targets.values() if v),
                 "ИТОГОВАЯ громкость (call_site x volume, как в блоке 9в)"
                 if spec_mode == "effective" else "volume в sounds.json"))
    if not a.map:
        print("ВНИМАНИЕ: группировка ПО ИМЕНАМ ФАЙЛОВ — может склеить РАЗНЫЕ события\n"
              "и разъединить ОДНО (файл без номера на конце уезжает в свою группу).\n"
              "Для верного счёта передайте --map sounds.json.\n")
    else:
        print("группировка: по карте %s\n" % a.map)
    # Карта читается ДО замера: несуществующий/битый --map раньше МОЛЧА
    # откатывался на группировку по именам файлов (она слепа к 6 событиям из 31)
    # и результат выглядел достоверным. Теперь отказ с кодом 3.
    map_data = None
    if a.map:
        try:
            with open(a.map, encoding="utf-8") as f:
                map_data = json.load(f)
        except (OSError, ValueError) as exc:
            print("ОШИБКА: карта %s не читается (%s)" % (a.map, exc))
            print("Без карты группировка по именам файлов слепа (6 событий из 31) — "
                  "результат недостоверен.")
            return 3

    print("%-40s %9s %9s %8s" % ("сэмпл", "пик dBFS", "RMS dBFS", "длит, с"))
    rows = []
    for stem in sorted(groups):
        peak, rms, dur = measure(groups[stem])
        rows.append((stem, peak, rms, dur))
        print("%-40s %9.1f %9.1f %8.2f" % (stem, peak, rms, dur))

    # ГРУППИРОВКА. Правильно — по карте событий sounds.json: только она знает,
    # какие файлы принадлежат одному событию. Группировка по имени файла
    # склеивает разные события (phantom_whisper + phantom_cry, если оба без
    # номера) и разъединяет настоящие (hive_spread_01_creep не оканчивается на
    # цифру -> каждое из трёх уезжает в свою группу, и разброс НЕ ВИДЕН).
    # Найдено Ревизором в reviewer_s94_spread_verify.md §2.
    # Столбец «длит, с» берётся из строки, где он посчитан, а не из кортежа
    # измерения: у measure() длительности нет (S94 потерял файл при сведении).
    print()   # печатаем ДО предупреждений о группировке, а не после
    meas = {stem: (peak, rms) for stem, peak, rms, _ in rows}
    events = {}
    if a.map:
        sj = map_data
        missing = []
        for ev, node in sj.items():
            if not isinstance(node, dict):
                continue
            lst = []
            for item in node.get("sounds", []):
                nm = item.get("name", "") if isinstance(item, dict) else str(item)
                nm = nm.split(":")[-1].split("/")[-1]
                nm = nm[:-4] if nm.endswith(".ogg") else nm
                if nm in meas:
                    lst.append((nm, meas[nm][0], meas[nm][1]))
                else:
                    missing.append(nm)
            if lst:
                events[ev] = lst
        if missing:
            print("ВНИМАНИЕ: %d файлов из карты не найдены в банке: %s"
                  % (len(missing), ", ".join(sorted(set(missing))[:5])))
        print("группировка: по карте — %d событий\n" % len(events))
    else:
        print("группировка: ПО ИМЕНАМ ФАЙЛОВ — может склеить разные события и\n"
              "разъединить одно. Для верного счёта передайте --map sounds.json\n")
        for stem, peak, rms, dur in rows:
            base = stem.rsplit("_", 1)[0] if stem.rsplit("_", 1)[-1].isdigit() else stem
            events.setdefault(base, []).append((stem, peak, rms))

    for base in sorted(events):
        items = events[base]
        if len(items) < 2:
            continue
        lo = min(items, key=lambda t: t[2])      # самый тихий по RMS
        hi = max(items, key=lambda t: t[2])
        spread = hi[2] - lo[2]
        factor = 10 ** (spread / 20.0)
        status = "ok" if spread <= a.threshold else "РАЗБРОС"
        if spread > a.threshold:
            bad += 1
        print("%-22s разброс RMS %.1f дБ -> %s" % (base, spread, status))
        print("      тихий %s (%.1f), громкий %s (%.1f)"
              % (lo[0], lo[2], hi[0], hi[2]))
        # З-29/Ревизор r29 (2026-11-26): норма разброса меряет RMS, а потолок
        # пика — пик. Если crest у файлов разный, выравнивание RMS упирается
        # в пол: развести громкости нельзя, не пробив потолок. Тогда «разброс
        # выше нормы» — свойство МЕТРИКИ, а не небрежность Звука, и печатать
        # это как «не выровняли» нечестно.
        crests = [peak - rms for _, peak, rms in items]
        floor = max(crests) - min(crests)
        if spread > a.threshold and floor >= a.threshold:
            print("      пол ПРИ ВЫРАВНИВАНИИ ПО ПИКАМ: crest разный "
                  "(%.1f…%.1f дБ), остаточный разброс RMS = %.2f дБ > %.1f"
                  % (min(crests), max(crests), floor, a.threshold))
            # ⚠ Уточнение S127: это НЕ универсальный предел. Множители
            # свободны в ОБЕ стороны, поэтому, опуская всё событие, RMS можно
            # выровнять в 0 (для flesh_hit — при уровне −22.73 дБ и пике
            # −1.20 ровно у _03). Поэтому принимать объявление «по полу»
            # НЕЛЬЗЯ: пол — свойство одного способа выравнивания, а не
            # физики. Ниже работает явный допуск из спеки.
            print("      → норма и потолок пика взаимно невыполнимы; "
                  "нужен явный допуск в спеке или перерисовка crest")
        if spread > a.threshold:
            print("      чтобы уровни сравнялись, множитель тихого должен быть "
                  "в %.2fx больше: одна цель на событие даст слышимый провал" % factor)
            # Ниже проверка объявления СРАВНИВАЕТ цели со средним, поэтому
            # событие с ФИЗИЧЕСКИМ ПОЛОМ печаталось «ОБЪЯВЛЕНО, НО НЕ
            # РАБОТАЕТ», хотя объявление снимает разброс ровно настолько,
            # насколько это физически возможно. Считаем остаток по ФАКТУ:
            # применяем множители к измеренным RMS и печатаем, до какого
            # уровня их можно довести, не пробив потолок пика.
            _tbs = spec_targets.get(base, {}) if a.spec else {}
            if _tbs and all(_tbs.get(st_) for st_, _, _ in items):
                _cs = spec_call_site.get(base, 1.0)
                _adj = [(st_, rms_ + 20 * math.log10(_tbs[st_] / _cs))
                        for st_, _, rms_ in items]
                # Остаток — это просто разброс ПОСЛЕ применения объявленных
                # множителей. Первая версия этой строки пыталась ещё и
                # «подтянуть» результат к потолку и печатала для detail_flow
                # остаток 6.15 дБ вместо фактических 0.02 — считать надо
                # ровно то, что даёт спека, без домыслов.
                _res = max(v for _, v in _adj) - min(v for _, v in _adj)
                _top = max(pk_ + 20 * math.log10(_tbs[st_] / _cs)
                           for st_, pk_, _ in items)
                # Пик в «пространстве JSON» — это пик ДО точки вызова. Если
                # call_site < 1, движок опустит его дополнительно, поэтому
                # сверять с потолком надо ЭФФЕКТИВНЫЙ пик, иначе событие с
                # call_site 0.65 объявляется «пробивающим потолок», хотя на
                # деле оно тише. Печатаю оба числа.
                _eff = _top + 20 * math.log10(_cs) if _cs else _top
                print("      по факту: остаток %.2f дБ, пик после множителей "
                      "%+.2f dBFS, эффективный %.2f dBFS (потолок -1.20)"
                      % (_res, _top, _eff))
                if _eff > -1.20 + 1e-9:
                    print("      ✗ ЭФФЕКТИВНЫЙ ПИК ВЫШЕ ПОТОЛКА — правка "
                          "недопустима")

            # Правило «объявлено в спеке -> ok» БЕЗ проверки остатка = fail-open:
            # объявление становится вечным пропуском. Проверяем, что после
            # применения targets_by_sample разброс действительно схлопнулся.
            if a.spec:
                tbs = spec_targets.get(base, {})
                if not tbs:
                    print("      В СПЕКЕ НЕ ОБЪЯВЛЕНО -> находка (нормы нет)")
                    undeclared += 1
                else:
                    # СЕМАНТИКА targets_by_sample — по умолчанию «volume в
                    # sounds.json» (обратная совместимость: спеку заполнял я,
                    # и раньше там лежали именно множители sounds.json).
                    # mode == "effective" читает их как ИТОГОВУЮ громкость
                    # (call_site x volume), то есть так, как их понимает
                    # volume_effective_check (блок 9в). Без явного выбора режима
                    # два инструмента считают одно событие по-разному —
                    # расхождение, на которое указал Интегратор.
                    adj = []
                    for stem_, pk_, rms_ in items:
                        t = tbs.get(stem_)
                        if t and spec_mode == "effective":
                            cs_vol = spec_call_site.get(base)
                            if not cs_vol:
                                t = None
                            else:
                                t = t / cs_vol
                        adj.append((stem_, rms_ + 20 * math.log10(t) if t else None))
                    known = [v for _, v in adj if v is not None]
                    if len(known) != len(adj):
                        print("      СПЕКА НЕПОЛНА: цель задана не для всех сэмплов -> находка")
                        undeclared += 1
                    else:
                        res = max(known) - min(known)
                        # Допуск — не только a.residual, но и физический пол
                        # (разница crest). Объявление, которое доводит разброс
                        # до пола, работает МАКСИМАЛЬНО хорошо; требовать от
                        # него «<= 0.25» — требовать пробить потолок пика.
                        # Fail-open это не открывает: плохое объявление
                        # (например, без множителей) даёт остаток БОЛЬШЕ пола
                        # и падает. Плюс пик после множителей обязан быть в
                        # норме — «выровнять в потолок» не считается.
                        # Допуск берётся из спеки, если событие его ЯВНО
                        # объявило (residual_tolerance). Так решение не
                        # становится вечным пропуском: без объявления событие
                        # остаётся находкой, а объявленный допуск виден в
                        # диффе спеки и подлежит ревью.
                        _decl = spec_tol.get(base, 0.0)
                        _cap = max(a.residual, _decl)
                        ok = res <= _cap
                        if ok and _decl > a.residual:
                            print("      остаток %.2f дБ -> в пределах "
                                  "объявленного допуска %.2f дБ (метрика: %s)"
                                  % (res, _decl,
                                     spec_tol_why.get(base, "не указана")))
                        else:
                            print("      остаток после множителей: %.2f дБ "
                                  "(допуск %g) -> %s"
                                  % (res, _cap,
                                     "объявление ПОДТВЕРЖДЕНО" if ok
                                     else "ОБЪЯВЛЕНО, НО НЕ РАБОТАЕТ"))
                        if not ok:
                            undeclared += 1

    print()
    if bad:
        print("ИТОГ: у %d событий разброс > %.1f дБ" % (bad, a.threshold))
        if a.spec:
            print("  из них объявление в спеке ПОДТВЕРЖДЕНО: %d" % (bad - undeclared))
            print("  и находок (нет в спеке / неполна / не выравнивает): %d" % undeclared)
        else:
            print("  --spec не задан: засчитать объявленное событие как решённое НЕЛЬЗЯ,")
            print("  иначе «объявил в спеке» станет вечным пропуском (fail-open).")
        return 2
    print("ИТОГ: разброс внутри событий в пределах %.1f дБ — одна цель годится"
          % a.threshold)
    return 0


if __name__ == "__main__":
    sys.exit(main())
